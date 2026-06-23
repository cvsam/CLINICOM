import os
import sys
from datetime import datetime

import pwinput
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from database import init_db, get_session, USE_MOCK
from models import User
from auth import AuthManager
from controllers import PatientManager, AppointmentManager, RecordManager

console = Console()


def seed_database():
    """Seed the database with initial data for presentation purposes."""
    auth = AuthManager()
    pm = PatientManager()
    am = AppointmentManager()
    rm = RecordManager()

    with get_session() as session:
        user_count = session.query(User).count()
        if user_count == 0:
            console.print("[dim]Seeding mock data for presentation...[/dim]")
            
            # Seed Users
            admin_id = auth.register_user("admin", "admin123", "Admin")
            doc_id = auth.register_user("doctor_john", "docpass123", "Doctor")
            rec_id = auth.register_user("receptionist_mary", "recpass123", "Receptionist")
            
            console.print("[dim]Created default users: admin, doctor_john, receptionist_mary[/dim]")
            
            # Seed Patients
            p1 = pm.add_patient("Kamau Njoroge", "1980-05-15", "Male", "0712345678", "Nairobi")
            p2 = pm.add_patient("Amina Hassan", "1992-11-20", "Female", "0722345678", "Mombasa")
            p3 = pm.add_patient("David Omondi", "1975-02-10", "Male", "0733345678", "Kisumu")
            p4 = pm.add_patient("Jane Wanjiku", "2001-08-30", "Female", "0744345678", "Nakuru")
            
            # Seed Appointments
            if doc_id and p1 and p2:
                # Scheduled
                am.book_appointment(p1, doc_id, f"{datetime.now().strftime('%Y-%m-%d')} 10:00", "Routine checkup")
                am.book_appointment(p2, doc_id, f"{datetime.now().strftime('%Y-%m-%d')} 11:30", "Follow up")
                # Completed
                old_app = am.book_appointment(p3, doc_id, "2024-01-10 09:00", "Malaria test")
                if old_app:
                    am.update_status(old_app, "Completed")
            
            # Seed Medical Records
            if doc_id and p3:
                rm.add_record(p3, doc_id, "2024-01-10 09:30", "Confirmed Malaria positive.", "Artemether Lumefantrine 80/480mg")
            if doc_id and p4:
                rm.add_record(p4, doc_id, "2024-02-14 14:00", "Mild respiratory infection.", "Amoxicillin 500mg TDS for 5 days")


class App:
    def __init__(self):
        self.auth = AuthManager()
        self.pm = PatientManager()
        self.am = AppointmentManager()
        self.rm = RecordManager()
        self.current_user = None

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self):
        self.clear_screen()
        db_mode = "MOCK-DB (Demo)" if USE_MOCK else "MySQL (Production)"
        
        title_panel = Panel.fit(
            f"[bold blue]CLINICOM[/bold blue] - Professional Clinic Management System\n[dim]Mode: {db_mode}[/dim]",
            border_style="blue"
        )
        console.print(title_panel)
        
        if self.current_user:
            console.print(f"Logged in as: [bold green]{self.current_user['username']}[/bold green] | Role: [bold cyan]{self.current_user['role']}[/bold cyan]\n")

    def run(self):
        while True:
            if not self.current_user:
                self.login_menu()
            else:
                self.main_menu()

    def login_menu(self):
        self.display_header()
        console.print("[bold]Login to CLINICOM[/bold]")
        username = Prompt.ask("Username")
        password = pwinput.pwinput(prompt="Password: ", mask="*")
        
        user = self.auth.login(username, password)
        if user:
            self.current_user = user
            console.print("[bold green]Login successful![/bold green]")
        else:
            console.print("[bold red]Invalid credentials or Database error.[/bold red]")
            Prompt.ask("Press Enter to try again")

    def main_menu(self):
        self.display_header()
        
        options = ["1. View All Patients", "2. Search Patient"]
        
        if self.auth.has_permission(self.current_user['role'], ['Admin', 'Receptionist']):
            options.append("3. Add New Patient")
            options.append("4. Book Appointment")
        
        if self.auth.has_permission(self.current_user['role'], ['Admin', 'Doctor']):
            options.append("5. View Upcoming Appointments")
            options.append("6. Manage Medical Records")
            
        if self.auth.has_permission(self.current_user['role'], ['Admin']):
            options.append("7. System Administration (Register Users)")
            
        options.append("8. Export Data to CSV")
        options.append("0. Logout")
        
        for opt in options:
            console.print(opt)
            
        choice = Prompt.ask("\nSelect an option", choices=[opt.split('.')[0] for opt in options])
        
        try:
            if choice == '1':
                self.view_patients()
            elif choice == '2':
                self.search_patient()
            elif choice == '3' and self.auth.has_permission(self.current_user['role'], ['Admin', 'Receptionist']):
                self.add_patient()
            elif choice == '4' and self.auth.has_permission(self.current_user['role'], ['Admin', 'Receptionist']):
                self.book_appointment()
            elif choice == '5' and self.auth.has_permission(self.current_user['role'], ['Admin', 'Doctor']):
                self.view_appointments()
            elif choice == '6' and self.auth.has_permission(self.current_user['role'], ['Admin', 'Doctor']):
                self.manage_records()
            elif choice == '7' and self.auth.has_permission(self.current_user['role'], ['Admin']):
                self.system_admin()
            elif choice == '8':
                self.export_data()
            elif choice == '0':
                self.current_user = None
        except Exception as e:
            console.print(f"[bold red]An error occurred: {e}[/bold red]")
            Prompt.ask("Press Enter to continue")

    def view_patients(self, patients=None):
        self.display_header()
        
        if patients is None:
            patients = self.pm.get_all_patients()
        
        if not patients:
            console.print("[yellow]No patients found.[/yellow]")
        else:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID", style="dim")
            table.add_column("Name")
            table.add_column("DOB")
            table.add_column("Gender")
            table.add_column("Contact")
            table.add_column("Address")
            
            for p in patients:
                table.add_row(
                    str(p['patient_id']), 
                    p['full_name'], 
                    str(p['dob']), 
                    p.get('gender', 'N/A'),
                    p['contact_info'],
                    p.get('address', '')
                )
                
            console.print(table)
        Prompt.ask("\nPress Enter to return")

    def search_patient(self):
        self.display_header()
        console.print("[bold]Search Patient[/bold]")
        keyword = Prompt.ask("Enter name or phone number to search")
        
        results = self.pm.search_patient(keyword)
        if results:
            console.print(f"\n[bold green]Found {len(results)} matching records:[/bold green]")
            self.view_patients(patients=results)
        else:
            console.print("[yellow]No matching patients found.[/yellow]")
            Prompt.ask("\nPress Enter to return")

    def add_patient(self):
        self.display_header()
        console.print("[bold]Add New Patient[/bold]")
        
        name = Prompt.ask("Full Name")
        dob = Prompt.ask("Date of Birth (YYYY-MM-DD)")
        gender = Prompt.ask("Gender", choices=["Male", "Female", "Other"])
        contact = Prompt.ask("Contact Number (e.g. 0712345678)")
        address = Prompt.ask("Address")
        
        patient_id = self.pm.add_patient(name, dob, gender, contact, address)
        if patient_id:
            console.print(f"[bold green]Patient added successfully! (ID: {patient_id})[/bold green]")
        else:
            console.print("[bold red]Failed to add patient. Please check your inputs and try again.[/bold red]")
        Prompt.ask("Press Enter to return")

    def book_appointment(self):
        self.display_header()
        console.print("[bold]Book New Appointment[/bold]")
        
        patient_id = Prompt.ask("Patient ID")
        doctor_id = Prompt.ask("Doctor ID (User ID)")
        date = Prompt.ask("Appointment Date (YYYY-MM-DD)")
        time = Prompt.ask("Appointment Time (HH:MM)")
        notes = Prompt.ask("Notes (Optional)", default="")
        
        datetime_str = f"{date} {time}"
        
        app_id = self.am.book_appointment(patient_id, doctor_id, datetime_str, notes)
        if app_id:
            console.print(f"[bold green]Appointment {app_id} booked successfully![/bold green]")
        else:
            console.print("[bold red]Failed to book appointment. Check ID and Date formats.[/bold red]")
        Prompt.ask("Press Enter to return")

    def view_appointments(self):
        self.display_header()
        apps = self.am.get_upcoming_appointments()
        
        if not apps:
            console.print("[yellow]No upcoming appointments.[/yellow]")
        else:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("ID")
            table.add_column("Patient")
            table.add_column("Doctor")
            table.add_column("Date")
            table.add_column("Status")
            
            for a in apps:
                table.add_row(
                    str(a['appointment_id']), 
                    a['patient_name'], 
                    a['doctor_name'], 
                    str(a['appointment_date']), 
                    a['status']
                )
            console.print(table)
        Prompt.ask("\nPress Enter to return")
        
    def manage_records(self):
        self.display_header()
        console.print("[bold]Manage Medical Records[/bold]")
        
        console.print("1. View Patient Records")
        console.print("2. Add New Record")
        console.print("0. Back")
        
        choice = Prompt.ask("\nSelect option", choices=["1", "2", "0"])
        
        if choice == "1":
            patient_id = Prompt.ask("Enter Patient ID")
            records = self.rm.get_patient_records(patient_id)
            if not records:
                console.print("[yellow]No medical records found for this patient.[/yellow]")
            else:
                table = Table(show_header=True, header_style="bold blue")
                table.add_column("Date")
                table.add_column("Doctor")
                table.add_column("Diagnosis")
                table.add_column("Prescription")
                
                for r in records:
                    table.add_row(r['visit_date'], r['doctor_name'], r['diagnosis'], r['prescription'])
                console.print(table)
                
        elif choice == "2":
            patient_id = Prompt.ask("Enter Patient ID")
            diagnosis = Prompt.ask("Diagnosis")
            prescription = Prompt.ask("Prescription")
            
            # Use current doctor's ID
            doctor_id = self.current_user["id"]
            
            if self.rm.add_record(patient_id, doctor_id, datetime.now().strftime("%Y-%m-%d %H:%M"), diagnosis, prescription):
                console.print("[bold green]Medical record added successfully.[/bold green]")
            else:
                console.print("[bold red]Failed to add record. Ensure patient ID is correct.[/bold red]")
                
        if choice != "0":
            Prompt.ask("\nPress Enter to return")

    def system_admin(self):
        self.display_header()
        console.print("[bold]System Administration[/bold]")
        console.print("Register a new staff member.")
        
        username = Prompt.ask("New Username")
        password = pwinput.pwinput("Password: ", mask="*")
        role = Prompt.ask("Role", choices=["Admin", "Doctor", "Receptionist"])
        
        if self.auth.register_user(username, password, role):
            console.print(f"[bold green]User {username} registered successfully as {role}.[/bold green]")
        else:
            console.print("[bold red]Failed to register user. Username might exist or password too short.[/bold red]")
            
        Prompt.ask("\nPress Enter to return")

    def export_data(self):
        self.display_header()
        console.print("[bold]Export Data (CSV)[/bold]")
        
        if self.pm.export_patients_to_csv():
            console.print("[bold green]Patients exported to patients_export.csv[/bold green]")
        else:
            console.print("[bold red]Failed to export patients.[/bold red]")
            
        if self.auth.has_permission(self.current_user['role'], ['Admin', 'Doctor']):
            p_id = Prompt.ask("Enter Patient ID to export their medical records (or press Enter to skip)", default="")
            if p_id:
                if self.rm.export_records_to_csv(p_id):
                    console.print(f"[bold green]Records exported to medical_records_patient_{p_id}.csv[/bold green]")
                else:
                    console.print("[bold red]Failed to export medical records.[/bold red]")
        
        Prompt.ask("\nPress Enter to return")


if __name__ == "__main__":
    try:
        console.print("[bold blue]Initializing CLINICOM database...[/bold blue]")
        init_db()
        seed_database()
        console.print("[bold green]Database ready.[/bold green]\n")
        app = App()
        app.run()
    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting CLINICOM...[/bold red]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Fatal error: {e}[/bold red]")
        sys.exit(1)
