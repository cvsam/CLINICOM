import os
import sys
import pwinput
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from auth import AuthManager
from controllers import PatientManager, AppointmentManager, RecordManager

console = Console()

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
        console.print(Panel.fit("[bold blue]CLINICOM[/bold blue] - Professional Clinic Management System", border_style="blue"))
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
            console.print("[bold red]Invalid credentials or Database is not connected.[/bold red]")
            Prompt.ask("Press Enter to try again")

    def main_menu(self):
        self.display_header()
        
        options = ["1. View Patients"]
        if self.auth.has_permission(self.current_user['role'], ['Admin', 'Receptionist']):
            options.append("2. Add New Patient")
            options.append("3. Book Appointments")
        
        if self.auth.has_permission(self.current_user['role'], ['Admin', 'Doctor']):
            options.append("4. View Upcoming Appointments")
            options.append("5. Manage Medical Records")
            
        options.append("0. Logout")
        
        for opt in options:
            console.print(opt)
            
        choice = Prompt.ask("\nSelect an option", choices=[opt.split('.')[0] for opt in options])
        
        try:
            if choice == '1':
                self.view_patients()
            elif choice == '2' and self.auth.has_permission(self.current_user['role'], ['Admin', 'Receptionist']):
                self.add_patient()
            elif choice == '3' and self.auth.has_permission(self.current_user['role'], ['Admin', 'Receptionist']):
                self.book_appointment()
            elif choice == '4' and self.auth.has_permission(self.current_user['role'], ['Admin', 'Doctor']):
                self.view_appointments()
            elif choice == '5' and self.auth.has_permission(self.current_user['role'], ['Admin', 'Doctor']):
                self.manage_records()
            elif choice == '0':
                self.current_user = None
        except Exception as e:
            console.print(f"[bold red]An error occurred: {e}[/bold red]")
            Prompt.ask("Press Enter to continue")

    def view_patients(self):
        self.display_header()
        patients = self.pm.get_all_patients()
        
        if not patients:
            console.print("[yellow]No patients found.[/yellow]")
        else:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID", style="dim")
            table.add_column("Name")
            table.add_column("DOB")
            table.add_column("Contact")
            
            for p in patients:
                table.add_row(str(p['patient_id']), p['full_name'], str(p['dob']), p['contact_info'])
                
            console.print(table)
        Prompt.ask("\nPress Enter to return")

    def add_patient(self):
        self.display_header()
        console.print("[bold]Add New Patient[/bold]")
        name = Prompt.ask("Full Name")
        dob = Prompt.ask("Date of Birth (YYYY-MM-DD)")
        gender = Prompt.ask("Gender", choices=["Male", "Female", "Other"])
        contact = Prompt.ask("Contact Number")
        address = Prompt.ask("Address")
        
        if self.pm.add_patient(name, dob, gender, contact, address):
            console.print("[bold green]Patient added successfully![/bold green]")
        else:
            console.print("[bold red]Failed to add patient. Check database connection/format.[/bold red]")
        Prompt.ask("Press Enter to return")

    def book_appointment(self):
        self.display_header()
        console.print("[bold]Book New Appointment[/bold]")
        patient_id = Prompt.ask("Patient ID")
        doctor_id = Prompt.ask("Doctor ID")
        date = Prompt.ask("Appointment Date (YYYY-MM-DD)")
        time = Prompt.ask("Appointment Time (HH:MM)")
        notes = Prompt.ask("Notes (Optional)", default="")
        
        datetime_str = f"{date} {time}"
        
        if self.am.book_appointment(patient_id, doctor_id, datetime_str, notes):
            console.print("[bold green]Appointment booked successfully![/bold green]")
        else:
            console.print("[bold red]Failed to book appointment.[/bold red]")
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
                table.add_row(str(a['appointment_id']), a['patient_name'], a['doctor_name'], str(a['appointment_date']), a['status'])
            console.print(table)
        Prompt.ask("\nPress Enter to return")
        
    def manage_records(self):
        self.display_header()
        console.print("Module for Doctors to add Medical Records (TBD).")
        Prompt.ask("Press Enter to return")


if __name__ == "__main__":
    try:
        app = App()
        app.run()
    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting CLINICOM...[/bold red]")
        sys.exit(0)
