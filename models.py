class User:
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role

    def __str__(self):
        return f"User({self.username}, Role: {self.role})"


class Patient:
    def __init__(self, patient_id, full_name, dob, gender, contact_info, address):
        self.id = patient_id
        self.full_name = full_name
        self.dob = dob
        self.gender = gender
        self.contact_info = contact_info
        self.address = address

    def __str__(self):
        return f"Patient({self.full_name}, Contact: {self.contact_info})"


class Appointment:
    def __init__(self, appointment_id, patient_id, doctor_id, appointment_date, status, notes):
        self.id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date
        self.status = status
        self.notes = notes

    def __str__(self):
        return f"Appointment(ID: {self.id}, Date: {self.appointment_date}, Status: {self.status})"
