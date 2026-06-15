import os

class DatabaseManager:
    """Handles mocked database connections and queries."""
    
    # Class-level variables to hold in-memory state across instances
    mock_patients = [
        {'patient_id': 1, 'full_name': 'John Doe', 'dob': '1990-01-01', 'contact_info': '123-456-7890'},
        {'patient_id': 2, 'full_name': 'Jane Smith', 'dob': '1985-05-15', 'contact_info': '098-765-4321'}
    ]
    mock_appointments = [
        {'appointment_id': 1, 'patient_name': 'John Doe', 'doctor_name': 'Dr. Smith', 'appointment_date': '2026-06-20', 'status': 'Scheduled'}
    ]
    next_patient_id = 3
    next_appointment_id = 2

    def __init__(self):
        pass

    def connect(self):
        """Mocks establishing a connection."""
        return True

    def disconnect(self):
        """Mocks closing the database connection."""
        pass

    def execute_query(self, query, params=None):
        """Mocks executing an INSERT, UPDATE, or DELETE query."""
        if "insert into patients" in query.lower():
            new_patient = {
                'patient_id': DatabaseManager.next_patient_id,
                'full_name': params[0],
                'dob': params[1],
                'contact_info': params[3]
            }
            DatabaseManager.mock_patients.append(new_patient)
            DatabaseManager.next_patient_id += 1
            return new_patient['patient_id']
        elif "insert into appointments" in query.lower():
            patient_name = f"Patient {params[0]}"
            for p in DatabaseManager.mock_patients:
                if str(p['patient_id']) == str(params[0]):
                    patient_name = p['full_name']
                    break
                    
            new_apt = {
                'appointment_id': DatabaseManager.next_appointment_id,
                'patient_name': patient_name,
                'doctor_name': f"Doctor {params[1]}",
                'appointment_date': params[2],
                'status': 'Scheduled',
                'notes': params[3]
            }
            DatabaseManager.mock_appointments.append(new_apt)
            DatabaseManager.next_appointment_id += 1
            return new_apt['appointment_id']
        return 1

    def fetch_all(self, query, params=None):
        """Mocks executing a SELECT query and returns dummy results."""
        if "patients" in query.lower() and "join" not in query.lower():
            return DatabaseManager.mock_patients
        elif "appointments" in query.lower():
            return DatabaseManager.mock_appointments
        return []

    def fetch_one(self, query, params=None):
        """Mocks executing a SELECT query and returns a single dummy result."""
        if "users" in query.lower():
            return {'id': 1, 'username': 'admin', 'password_hash': 'mock', 'role': 'Admin'}
        return None

