"""
app.py — Flask Web Application for CLINICOM
============================================
Provides a beautiful, modern graphical user interface using HTML/CSS.
Wires up to the exact same backend logic (controllers.py).
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime

from auth import AuthManager
from controllers import PatientManager, AppointmentManager, RecordManager
from database import init_db

app = Flask(__name__)
app.secret_key = "very_secret_clinicom_key"  # Needed for session and flash messages

# Initialize controllers
auth_mgr = AuthManager()
patient_mgr = PatientManager()
appt_mgr = AppointmentManager()
record_mgr = RecordManager()

# Ensure database is created on startup
init_db()

@app.context_processor
def inject_user():
    """Inject current user role into all templates for navbar logic."""
    return dict(current_user=session.get('user'))

# ----------------- AUTHENTICATION -----------------

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = auth_mgr.login(username, password)
        if user:
            session['user'] = user
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials. Please try again.", "error")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# ----------------- DASHBOARD -----------------

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    patients = patient_mgr.get_all_patients()
    appointments = appt_mgr.get_upcoming_appointments()
    
    # Calculate simple stats
    stats = {
        'total_patients': len(patients),
        'upcoming_appointments': len(appointments),
    }
    
    return render_template('dashboard.html', stats=stats, appointments=appointments[:5])


# ----------------- PATIENTS -----------------

@app.route('/patients', methods=['GET'])
def patients():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    keyword = request.args.get('search', '')
    if keyword:
        patients_list = patient_mgr.search_patient(keyword)
    else:
        patients_list = patient_mgr.get_all_patients()
        
    return render_template('patients.html', patients=patients_list, search=keyword)

@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    # Access control: Only Admin or Receptionist
    if not auth_mgr.has_permission(session['user']['role'], ['Admin', 'Receptionist']):
        flash("You don't have permission to add patients.", "error")
        return redirect(url_for('patients'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        contact = request.form.get('contact')
        address = request.form.get('address')
        
        pid = patient_mgr.add_patient(full_name, dob, gender, contact, address)
        if pid:
            flash(f"Patient {full_name} added successfully!", "success")
            return redirect(url_for('patients'))
        else:
            flash("Failed to add patient. Please check your inputs.", "error")
            
    return render_template('add_patient.html')


# ----------------- APPOINTMENTS -----------------

@app.route('/appointments')
def appointments():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    all_appointments = appt_mgr.get_upcoming_appointments()
    return render_template('appointments.html', appointments=all_appointments)


# ----------------- USERS (ADMIN ONLY) -----------------

@app.route('/users')
def users():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    # Access control: Only Admin
    if session['user']['role'] != 'Admin':
        flash("Only Administrators can manage users.", "error")
        return redirect(url_for('dashboard'))
        
    all_users = auth_mgr.get_all_users()
    return render_template('users.html', users=all_users)

@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if 'user' not in session:
        return redirect(url_for('login'))
        
    if session['user']['role'] != 'Admin':
        flash("Only Administrators can add users.", "error")
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        uid = auth_mgr.register_user(username, password, role)
        if uid:
            flash(f"User {username} added successfully as {role}!", "success")
            return redirect(url_for('users'))
        else:
            flash("Failed to add user. Username may exist or password too short.", "error")
            
    return render_template('add_user.html')

if __name__ == '__main__':
    # Start the Flask web server
    app.run(debug=True, port=5000)
