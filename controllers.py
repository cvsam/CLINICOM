from database import DatabaseManager
from models import Patient, Appointment

class BaseManager:
    """Base Manager using Inheritance to share DB connection."""
    def __init__(self):
        self.db = DatabaseManager()

class PatientManager(BaseManager):
    """Business logic for Patient operations."""
    
    def add_patient(self, full_name, dob, gender, contact_info, address):
        query = """
            INSERT INTO patients (full_name, dob, gender, contact_info, address)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (full_name, dob, gender, contact_info, address))

    def get_all_patients(self):
        query = "SELECT * FROM patients ORDER BY full_name ASC"
        return self.db.fetch_all(query)

    def search_patient(self, keyword):
        query = "SELECT * FROM patients WHERE full_name LIKE %s OR contact_info LIKE %s"
        search_term = f"%{keyword}%"
        return self.db.fetch_all(query, (search_term, search_term))

class AppointmentManager(BaseManager):
    """Business logic for Appointment operations."""
    
    def book_appointment(self, patient_id, doctor_id, appointment_date, notes):
        query = """
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, notes)
            VALUES (%s, %s, %s, 'Scheduled', %s)
        """
        return self.db.execute_query(query, (patient_id, doctor_id, appointment_date, notes))

    def get_upcoming_appointments(self):
        query = """
            SELECT a.appointment_id, p.full_name as patient_name, u.username as doctor_name, 
                   a.appointment_date, a.status, a.notes
            FROM appointments a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN users u ON a.doctor_id = u.id
            WHERE a.status = 'Scheduled' AND a.appointment_date >= CURDATE()
            ORDER BY a.appointment_date ASC
        """
        return self.db.fetch_all(query)

    def update_status(self, appointment_id, new_status):
        query = "UPDATE appointments SET status = %s WHERE appointment_id = %s"
        return self.db.execute_query(query, (new_status, appointment_id))

class RecordManager(BaseManager):
    """Business logic for Medical Records."""
    
    def add_record(self, patient_id, doctor_id, visit_date, diagnosis, prescription):
        query = """
            INSERT INTO medical_records (patient_id, doctor_id, visit_date, diagnosis, prescription)
            VALUES (%s, %s, %s, %s, %s)
        """
        return self.db.execute_query(query, (patient_id, doctor_id, visit_date, diagnosis, prescription))

    def get_patient_records(self, patient_id):
        query = """
            SELECT r.record_id, r.visit_date, r.diagnosis, r.prescription, u.username as doctor_name
            FROM medical_records r
            JOIN users u ON r.doctor_id = u.id
            WHERE r.patient_id = %s
            ORDER BY r.visit_date DESC
        """
        return self.db.fetch_all(query, (patient_id,))
