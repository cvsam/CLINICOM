"""
controllers.py — Business Logic Controllers for CLINICOM
=========================================================
Implements the Controller layer of the MVC architecture.

Class Hierarchy (demonstrates INHERITANCE):
    BaseManager          ← Abstract parent with shared validation utilities
      ├── PatientManager     ← CRUD operations for patients
      ├── AppointmentManager ← Booking and status management
      └── RecordManager      ← Medical record creation and retrieval

Design Patterns:
    - Inheritance:    All managers share BaseManager's validation methods
    - Encapsulation:  Private methods (prefixed _) hide internal logic
    - Error Handling: Every DB operation wrapped in try/except
"""

import csv
import os
import re
from datetime import date, datetime

from sqlalchemy.orm import joinedload

from database import get_session
from models import Patient, Appointment, MedicalRecord, User


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BASE MANAGER — Parent class demonstrating INHERITANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class BaseManager:
    """Abstract base class for all managers.

    Provides shared validation and utility methods that are INHERITED
    by PatientManager, AppointmentManager, and RecordManager.

    This demonstrates the OOP concept of INHERITANCE — child classes
    reuse and extend the parent's functionality without duplicating code.

    Private methods (prefixed with _) demonstrate ENCAPSULATION — they
    hide internal validation logic from external callers.
    """

    def _validate_date(self, date_string, date_format="%Y-%m-%d"):
        """Validate and parse a date string (ENCAPSULATED helper).

        Args:
            date_string: The date to validate (e.g., '2024-01-15').
            date_format:  Expected format (default: YYYY-MM-DD).

        Returns:
            A datetime.date object if valid, None otherwise.
        """
        try:
            parsed = datetime.strptime(date_string.strip(), date_format)
            return parsed.date()
        except (ValueError, AttributeError):
            return None

    def _validate_datetime(self, datetime_string):
        """Validate and parse a datetime string (ENCAPSULATED helper).

        Accepts: 'YYYY-MM-DD HH:MM' format.

        Returns:
            A datetime object if valid, None otherwise.
        """
        try:
            return datetime.strptime(datetime_string.strip(), "%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            return None

    def _validate_name(self, name):
        """Validate that a name contains only letters and spaces.

        Args:
            name: The name string to validate.

        Returns:
            True if valid, False otherwise.
        """
        if not name or not name.strip():
            return False
        # Allow letters, spaces, hyphens, and apostrophes (e.g., O'Brien, Mary-Jane)
        return bool(re.match(r"^[A-Za-z\s\-']+$", name.strip()))

    def _validate_phone(self, phone):
        """Validate a phone number format (ENCAPSULATED helper).

        Accepts formats: 0712345678, +254712345678, 254712345678

        Args:
            phone: The phone number string.

        Returns:
            True if valid, False otherwise.
        """
        if not phone or not phone.strip():
            return False
        # Remove spaces and dashes for validation
        cleaned = re.sub(r"[\s\-]", "", phone.strip())
        return bool(re.match(r"^(\+?\d{10,13})$", cleaned))

    def _validate_gender(self, gender):
        """Validate gender input (ENCAPSULATED helper).

        Returns:
            True if gender is Male, Female, or Other.
        """
        return gender in ("Male", "Female", "Other")

    def _validate_id(self, id_value):
        """Validate that an ID is a positive integer.

        Returns:
            The integer ID if valid, None otherwise.
        """
        try:
            parsed = int(id_value)
            return parsed if parsed > 0 else None
        except (ValueError, TypeError):
            return None

    def _format_error(self, operation, error):
        """Format a consistent error message for logging.

        Returns:
            A formatted error string.
        """
        return f"[DB Error] {operation}: {error}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PATIENT MANAGER — Inherits from BaseManager
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class PatientManager(BaseManager):
    """Business logic for Patient operations using SQLAlchemy ORM.

    INHERITS from BaseManager to reuse validation methods like
    _validate_date, _validate_name, and _validate_phone.
    """

    def add_patient(self, full_name, dob, gender, contact_info, address):
        """Register a new patient with full input validation.

        Validates all inputs before attempting database insertion.
        Returns the new patient's ID on success, or None on failure.
        """
        # ── Input Validation (using inherited methods) ──
        if not self._validate_name(full_name):
            print("[Validation] Invalid name: must contain only letters and spaces.")
            return None

        parsed_dob = self._validate_date(dob)
        if not parsed_dob:
            print("[Validation] Invalid date format. Use YYYY-MM-DD.")
            return None

        if not self._validate_gender(gender):
            print("[Validation] Gender must be Male, Female, or Other.")
            return None

        if not self._validate_phone(contact_info):
            print("[Validation] Invalid phone number format.")
            return None

        # ── Database Operation ──
        try:
            with get_session() as session:
                patient = Patient(
                    full_name=full_name.strip(),
                    dob=parsed_dob,
                    gender=gender,
                    contact_info=contact_info.strip(),
                    address=address.strip() if address else "",
                )
                session.add(patient)
                session.flush()  # Populate patient_id before commit
                return patient.patient_id
        except Exception as e:
            print(self._format_error("add_patient", e))
            return None

    def get_all_patients(self):
        """Return all patients ordered alphabetically by name.

        Returns:
            A list of dictionaries, each representing a patient.
        """
        try:
            with get_session() as session:
                patients = (
                    session.query(Patient)
                    .order_by(Patient.full_name.asc())
                    .all()
                )
                # Convert to dicts so they are usable outside the session
                return [
                    {
                        "patient_id": p.patient_id,
                        "full_name": p.full_name,
                        "dob": str(p.dob),
                        "gender": p.gender,
                        "contact_info": p.contact_info,
                        "address": p.address or "",
                    }
                    for p in patients
                ]
        except Exception as e:
            print(self._format_error("get_all_patients", e))
            return []

    def search_patient(self, keyword):
        """Search patients by name or contact info (case-insensitive).

        Uses SQL LIKE for partial matching, demonstrating data processing.

        Args:
            keyword: The search term to match against name or contact.

        Returns:
            A list of matching patient dictionaries.
        """
        try:
            with get_session() as session:
                search_term = f"%{keyword}%"
                patients = (
                    session.query(Patient)
                    .filter(
                        Patient.full_name.ilike(search_term)
                        | Patient.contact_info.ilike(search_term)
                    )
                    .all()
                )
                return [
                    {
                        "patient_id": p.patient_id,
                        "full_name": p.full_name,
                        "dob": str(p.dob),
                        "contact_info": p.contact_info,
                    }
                    for p in patients
                ]
        except Exception as e:
            print(self._format_error("search_patient", e))
            return []

    def export_patients_to_csv(self, filepath="patients_export.csv"):
        """Export all patient records to a CSV file (demonstrates FILE HANDLING).

        This method satisfies the coursework requirement for file handling
        by writing structured data to a CSV file using Python's csv module.

        Args:
            filepath: Path to the output CSV file.

        Returns:
            The filepath on success, None on failure.
        """
        try:
            patients = self.get_all_patients()
            if not patients:
                print("[Export] No patients to export.")
                return None

            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["patient_id", "full_name", "dob", "gender", "contact_info", "address"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for patient in patients:
                    writer.writerow(patient)

            return filepath
        except IOError as e:
            print(self._format_error("export_patients_to_csv", e))
            return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  APPOINTMENT MANAGER — Inherits from BaseManager
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class AppointmentManager(BaseManager):
    """Business logic for Appointment operations using SQLAlchemy ORM.

    INHERITS from BaseManager to reuse validation methods like
    _validate_id and _validate_datetime.
    """

    def book_appointment(self, patient_id, doctor_id, appointment_date, notes):
        """Book a new appointment with input validation.

        Validates IDs and date format before database insertion.
        Returns the appointment ID on success, or None on failure.
        """
        # ── Input Validation ──
        parsed_pid = self._validate_id(patient_id)
        parsed_did = self._validate_id(doctor_id)
        if not parsed_pid or not parsed_did:
            print("[Validation] Patient ID and Doctor ID must be positive integers.")
            return None

        parsed_date = self._validate_datetime(appointment_date)
        if not parsed_date:
            print("[Validation] Invalid datetime. Use 'YYYY-MM-DD HH:MM' format.")
            return None

        # ── Database Operation ──
        try:
            with get_session() as session:
                appointment = Appointment(
                    patient_id=parsed_pid,
                    doctor_id=parsed_did,
                    appointment_date=parsed_date,
                    status="Scheduled",
                    notes=notes if notes else "",
                )
                session.add(appointment)
                session.flush()
                return appointment.appointment_id
        except Exception as e:
            print(self._format_error("book_appointment", e))
            return None

    def get_upcoming_appointments(self):
        """Return all scheduled appointments from today onward.

        Uses SQLAlchemy's joinedload to eagerly fetch related patient
        and doctor data in a single query (demonstrates efficient queries).

        Returns:
            A list of appointment dictionaries with patient/doctor names.
        """
        try:
            with get_session() as session:
                appointments = (
                    session.query(Appointment)
                    .options(
                        joinedload(Appointment.patient),
                        joinedload(Appointment.doctor),
                    )
                    .filter(
                        Appointment.status == "Scheduled",
                        Appointment.appointment_date >= datetime.combine(
                            date.today(), datetime.min.time()
                        ),
                    )
                    .order_by(Appointment.appointment_date.asc())
                    .all()
                )
                return [
                    {
                        "appointment_id": a.appointment_id,
                        "patient_name": a.patient.full_name,
                        "doctor_name": a.doctor.username,
                        "appointment_date": str(a.appointment_date),
                        "status": a.status,
                    }
                    for a in appointments
                ]
        except Exception as e:
            print(self._format_error("get_upcoming_appointments", e))
            return []

    def get_all_appointments(self):
        """Return ALL appointments regardless of status or date.

        Returns:
            A list of appointment dictionaries.
        """
        try:
            with get_session() as session:
                appointments = (
                    session.query(Appointment)
                    .options(
                        joinedload(Appointment.patient),
                        joinedload(Appointment.doctor),
                    )
                    .order_by(Appointment.appointment_date.desc())
                    .all()
                )
                return [
                    {
                        "appointment_id": a.appointment_id,
                        "patient_name": a.patient.full_name,
                        "doctor_name": a.doctor.username,
                        "appointment_date": str(a.appointment_date),
                        "status": a.status,
                    }
                    for a in appointments
                ]
        except Exception as e:
            print(self._format_error("get_all_appointments", e))
            return []

    def update_status(self, appointment_id, new_status):
        """Update the status of an appointment.

        Args:
            appointment_id: The ID of the appointment to update.
            new_status:     New status (Scheduled, Completed, Cancelled).

        Returns:
            True on success, False on failure.
        """
        if new_status not in ("Scheduled", "Completed", "Cancelled"):
            print("[Validation] Status must be Scheduled, Completed, or Cancelled.")
            return False

        parsed_id = self._validate_id(appointment_id)
        if not parsed_id:
            print("[Validation] Invalid appointment ID.")
            return False

        try:
            with get_session() as session:
                appointment = (
                    session.query(Appointment)
                    .filter(Appointment.appointment_id == parsed_id)
                    .first()
                )
                if appointment:
                    appointment.status = new_status
                    return True
                return False
        except Exception as e:
            print(self._format_error("update_status", e))
            return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  RECORD MANAGER — Inherits from BaseManager
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class RecordManager(BaseManager):
    """Business logic for Medical Records using SQLAlchemy ORM.

    INHERITS from BaseManager to reuse validation methods.
    """

    def add_record(self, patient_id, doctor_id, visit_date, diagnosis, prescription):
        """Create a new medical record with validation.

        Args:
            patient_id:   ID of the patient.
            doctor_id:    ID of the attending doctor.
            visit_date:   Date of the visit (YYYY-MM-DD HH:MM).
            diagnosis:    Doctor's diagnosis text.
            prescription: Prescribed treatment/medication.

        Returns:
            The record ID on success, None on failure.
        """
        parsed_pid = self._validate_id(patient_id)
        parsed_did = self._validate_id(doctor_id)
        if not parsed_pid or not parsed_did:
            print("[Validation] Invalid patient or doctor ID.")
            return None

        if not diagnosis or not diagnosis.strip():
            print("[Validation] Diagnosis cannot be empty.")
            return None

        try:
            with get_session() as session:
                record = MedicalRecord(
                    patient_id=parsed_pid,
                    doctor_id=parsed_did,
                    visit_date=datetime.now(),
                    diagnosis=diagnosis.strip(),
                    prescription=prescription.strip() if prescription else "",
                )
                session.add(record)
                session.flush()
                return record.record_id
        except Exception as e:
            print(self._format_error("add_record", e))
            return None

    def get_patient_records(self, patient_id):
        """Return all medical records for a given patient.

        Args:
            patient_id: The patient's ID.

        Returns:
            A list of record dictionaries, newest first.
        """
        parsed_id = self._validate_id(patient_id)
        if not parsed_id:
            return []

        try:
            with get_session() as session:
                records = (
                    session.query(MedicalRecord)
                    .options(joinedload(MedicalRecord.doctor))
                    .filter(MedicalRecord.patient_id == parsed_id)
                    .order_by(MedicalRecord.visit_date.desc())
                    .all()
                )
                return [
                    {
                        "record_id": r.record_id,
                        "visit_date": str(r.visit_date),
                        "diagnosis": r.diagnosis,
                        "prescription": r.prescription,
                        "doctor_name": r.doctor.username,
                    }
                    for r in records
                ]
        except Exception as e:
            print(self._format_error("get_patient_records", e))
            return []

    def export_records_to_csv(self, patient_id, filepath=None):
        """Export a patient's medical records to CSV (FILE HANDLING).

        Args:
            patient_id: The patient whose records to export.
            filepath:   Output file path (auto-generated if None).

        Returns:
            The filepath on success, None on failure.
        """
        if filepath is None:
            filepath = f"medical_records_patient_{patient_id}.csv"

        try:
            records = self.get_patient_records(patient_id)
            if not records:
                print("[Export] No records found for this patient.")
                return None

            with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["record_id", "visit_date", "diagnosis", "prescription", "doctor_name"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for record in records:
                    writer.writerow(record)

            return filepath
        except IOError as e:
            print(self._format_error("export_records_to_csv", e))
            return None
