# application/models.py
# ------------------------------------------------------------
# This file defines the database schema for the Hospital Management System
# using SQLAlchemy ORM. It handles Admin, Doctor, Patient, Appointment,
# Treatment, and Department relationships.
# ------------------------------------------------------------

# application/models.py
from application.database import db
from datetime import datetime

# ============================================================
# 1️⃣ USER MODEL
# ============================================================
class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')

    def __init__(self, name, email, password, role="patient"):
        self.name = name
        self.email = email
        self.password = password
        self.role = role


# ============================================================
# 2️⃣ DEPARTMENT MODEL
# ============================================================
class Department(db.Model):
    __tablename__ = 'department'

    dept_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<Department {self.name}>"

    def to_dict(self):
        return {
            'dept_id': self.dept_id,
            'name': self.name,
            'description': self.description
        }



# ============================================================
# 3️⃣ DOCTOR MODEL (FINAL)
# ============================================================
class Doctor(db.Model):
    __tablename__ = 'doctor'

    doctor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey('department.dept_id'), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    # availability = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False,unique=True)

    user = db.relationship('User', backref=db.backref('doctor_profile', uselist=False))
    department = db.relationship('Department', backref=db.backref('doctors', lazy=True))

    def __init__(self, name, email, password, dept_id, specialization, user_id):
        self.name = name
        self.email = email
        self.password = password
        self.dept_id = dept_id
        self.specialization = specialization
        # self.availability = availability
        self.user_id = user_id
    def to_dict(self):
        return {
            'doctor_id': self.doctor_id,
            'name': self.name,
            'specialization': self.specialization,
            'email': self.email
        }
# In your models.py file
# In your models.py file, modify the Doctor class


class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availability'
    
    # Primary Key
    availability_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Link to the Doctor
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable=False)
    
    # Store the Day of the Week (e.g., 'Monday', 'Tuesday')
    day_of_week = db.Column(db.String(10), nullable=False)
    
    # Store the Time Slot value (e.g., '09:00 AM' - same as in appointment form)
    time_slot = db.Column(db.String(20), nullable=False)
    
    # Define relationship
    doctor = db.relationship('Doctor', backref=db.backref('schedule', lazy=True))

    # Optional: Add a unique constraint to prevent duplicate slots for the same doctor
    __table_args__ = (
        db.UniqueConstraint('doctor_id', 'day_of_week', 'time_slot', name='_doctor_slot_uc'),
    )

    def __repr__(self):
        return f"<DoctorAvailability {self.doctor_id} - {self.day_of_week} {self.time_slot}>"
# ============================================================
# 5️⃣ APPOINTMENT MODEL
# ============================================================
class Appointment(db.Model):
    __tablename__ = 'appointment'

    appointment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Booked')  
    # statuses = ['Booked', 'Completed', 'Cancelled']

    doctor = db.relationship('Doctor', backref=db.backref('appointments', lazy=True))
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))

    def __repr__(self):
        return f"<Appointment {self.appointment_id} - {self.status}>"

    def to_dict(self):
        return {
            'appointment_id': self.appointment_id,
            'doctor': self.doctor.user.name,
            'user': self.user.name,
            'date': self.date,
            'time': self.time,
            'status': self.status
        }


# ============================================================
# 6️⃣ TREATMENT MODEL
# ============================================================
class Treatment(db.Model):
    __tablename__ = 'treatment'

    treatment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.appointment_id'), nullable=False)
    diagnosis = db.Column(db.String(250), nullable=True)
    prescription = db.Column(db.String(250), nullable=True)
    notes = db.Column(db.String(250), nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    appointment = db.relationship('Appointment', backref=db.backref('treatment', uselist=False))

    def __repr__(self):
        return f"<Treatment {self.treatment_id}>"

    def to_dict(self):
        return {
            'treatment_id': self.treatment_id,
            'appointment_id': self.appointment_id,
            'diagnosis': self.diagnosis,
            'prescription': self.prescription,
            'notes': self.notes
        }


# ============================================================
# 7️⃣ FEEDBACK MODEL
# ============================================================
class Feedback(db.Model):
    __tablename__ = 'feedback'

    feedback_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable=False)
    message = db.Column(db.String(250), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback {self.feedback_id}>"

    def to_dict(self):
        return {
            'feedback_id': self.feedback_id,
            'user_id': self.user_id,
            'doctor_id': self.doctor_id,
            'message': self.message,
            'created_on': self.created_on.strftime('%Y-%m-%d %H:%M:%S')
        }
    
from datetime import datetime

class PatientHistory(db.Model):
    __tablename__ = 'patient_history'

    history_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.dept_id'), nullable=False)

    # Missing fields → ADD THEM
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.doctor_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    visit_type = db.Column(db.String(100), nullable=True)
    test_done = db.Column(db.String(200), nullable=True)
    diagnosis = db.Column(db.String(250), nullable=True)
    medicines = db.Column(db.String(250), nullable=True)
    prescription = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref=db.backref('patient_histories', lazy=True))
    department = db.relationship('Department', backref=db.backref('patient_histories', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('patient_histories', lazy=True))

    def __init__(self, user_id, department_id, doctor_id, visit_type, test_done, diagnosis, medicines, prescription):
        self.user_id = user_id
        self.department_id = department_id
        self.doctor_id = doctor_id
        self.visit_type = visit_type
        self.test_done = test_done
        self.diagnosis = diagnosis
        self.medicines = medicines
        self.prescription = prescription
