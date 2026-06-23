"""
models.py — ORM Data Models for CLINICOM
=========================================
Defines the database schema using SQLAlchemy ORM.

Each class maps to a database table and represents a real-world entity:
    - User:          System users with role-based access (Admin, Doctor, Receptionist)
    - Patient:       Registered patients with personal and contact details
    - Appointment:   Scheduled meetings between patients and doctors
    - MedicalRecord: Clinical records documenting diagnoses and prescriptions

Relationships:
    Users (Doctor) ──┬── Appointments ──── Patients
                     └── MedicalRecords ── Patients
"""

from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    """Represents a system user (Admin, Doctor, or Receptionist).

    Attributes:
        id:            Unique auto-incremented identifier.
        username:      Login name (must be unique).
        password_hash: bcrypt-hashed password for secure storage.
        role:          Access level — determines menu visibility.
        created_at:    Timestamp of account creation.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # Admin, Doctor, or Receptionist
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships — a doctor can have many appointments and medical records
    appointments = relationship("Appointment", back_populates="doctor")
    medical_records = relationship("MedicalRecord", back_populates="doctor")

    def __repr__(self):
        return f"User({self.username}, Role: {self.role})"


class Patient(Base):
    """Represents a registered patient in the clinic.

    Attributes:
        patient_id:        Unique auto-incremented identifier.
        full_name:         Patient's full name.
        dob:               Date of birth.
        gender:            Male, Female, or Other.
        contact_info:      Phone number or email.
        address:           Physical address.
        registration_date: When the patient was first registered.
    """
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)  # Male, Female, or Other
    contact_info = Column(String(100), nullable=False)
    address = Column(Text)
    registration_date = Column(DateTime, default=datetime.utcnow)

    # A patient can have many appointments and medical records
    appointments = relationship(
        "Appointment", back_populates="patient", cascade="all, delete-orphan"
    )
    medical_records = relationship(
        "MedicalRecord", back_populates="patient", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Patient({self.full_name}, Contact: {self.contact_info})"


class Appointment(Base):
    """Represents a scheduled appointment between a patient and a doctor.

    Attributes:
        appointment_id:   Unique auto-incremented identifier.
        patient_id:       Foreign key → patients table.
        doctor_id:        Foreign key → users table (doctor).
        appointment_date: Scheduled date and time.
        status:           Current state — Scheduled, Completed, or Cancelled.
        notes:            Optional clinical notes about the visit.
    """
    __tablename__ = "appointments"

    appointment_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(
        Integer,
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
    )
    doctor_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    appointment_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="Scheduled")  # Scheduled, Completed, Cancelled
    notes = Column(Text)

    # Relationships — allow eager access to patient/doctor info
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("User", back_populates="appointments")

    def __repr__(self):
        return (
            f"Appointment(ID: {self.appointment_id}, "
            f"Date: {self.appointment_date}, Status: {self.status})"
        )


class MedicalRecord(Base):
    """Represents a medical record for a patient visit.

    Attributes:
        record_id:    Unique auto-incremented identifier.
        patient_id:   Foreign key → patients table.
        doctor_id:    Foreign key → users table (doctor).
        visit_date:   Date and time of the clinical visit.
        diagnosis:    Doctor's diagnosis notes.
        prescription: Prescribed medication and instructions.
    """
    __tablename__ = "medical_records"

    record_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(
        Integer,
        ForeignKey("patients.patient_id", ondelete="CASCADE"),
        nullable=False,
    )
    doctor_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    visit_date = Column(DateTime, nullable=False)
    diagnosis = Column(Text, nullable=False)
    prescription = Column(Text)

    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("User", back_populates="medical_records")

    def __repr__(self):
        return f"MedicalRecord(ID: {self.record_id}, Date: {self.visit_date})"
