
from flask import current_app as app # if you directly import app> circular import error
from flask import (
    current_app as app,   # you used this pattern to avoid circular imports
    render_template,
    redirect,
    request,
    session,
    flash,
    url_for
)
from sqlalchemy import func 
from flask import jsonify
from datetime import date

from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Department, Doctor, Appointment, Treatment, Feedback,PatientHistory, DoctorAvailability
from .database import db
from datetime import datetime
#current_app refers to app object that we create 

from .database import db

@app.route("/login",methods=["GET","POST"])
def login():
  if request.method=="POST":
    name=request.form["name"]
    password=request.form.get("password")
    #both  are the same method as above to feetch the name and password
    #fetching the data
    this_user=User.query.filter_by(name=name).first() #LHS> Table attribute and RHS> Form data
    if this_user:
      if this_user.password == password:
                # ✅ store session info
                session['user_id'] = this_user.user_id
                session['role'] = this_user.role
                session['name'] = this_user.name
      if this_user.password==password:
        if this_user.role=="admin":
          return redirect("/admin-dash")
        else:
          return redirect("/patient-dash")
      else:
        return "Password is wrong"
    else:
      return "User doesn't exist"
  return render_template("login.html")

@app.route("/register",methods=["GET","POST"])
def register():
  if request.method=="POST":
    name=request.form["name"]
    email=request.form["email"]
    password=request.form["password"]
    user_name=User.query.filter_by(name=name).first()
    user_email=User.query.filter_by(email=email).first()
    if user_name or user_email:
      return "user already exists"
    else:
      user=User(name=name,email=email,password=password)
      db.session.add(user)
      db.session.commit()
    flash("Registered Successfully! Please login.", "success")
    return redirect(url_for("login"))
  return render_template("register.html") #get method


@app.route("/request-history/<int:appointment_id>")
def request_history(appointment_id):

    # Load appointment
    appt = Appointment.query.get(appointment_id)
    if not appt:
        flash("Appointment not found!", "danger")
        return redirect("/admin-dash")

    # Patient (comes from Appointment → user relation)
    patient = appt.user          # Correct

    # Doctor (comes from Appointment → doctor relation)
    doctor = appt.doctor         # Correct

    # Department (comes from Doctor → department relation)
    department = doctor.department   # Correct

    # All patient medical history
    history_records = PatientHistory.query.filter_by(user_id=patient.user_id).all()

    return render_template(
        "patient_history.html",
        patient=patient,
        doctor=doctor,
        department=department,
        history=history_records
    )




from flask import request, redirect, url_for, flash, render_template, session
# Import your models: db, User, Doctor, Department, and DoctorAvailability
# from .models import db, User, Doctor, Department, DoctorAvailability 
# from werkzeug.security import generate_password_hash # Recommended for password hashing

@app.route("/add-doctor", methods=["GET", "POST"])
def add_doctor():
    # 1. Access Restriction
    if session.get('role') != 'admin':
        flash("Only Admin can add new doctors.", "danger")
        return redirect(url_for('login'))

    departments = Department.query.all()

    if request.method == "POST":
        # 2. Extract Data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password') # Remember to HASH this!
        dept_id = request.form.get('dept_id', type=int)
        specialization = request.form.get('specialization')
        
        # NEW: Get list of selected days and time slots
        available_days = request.form.getlist('available_days')
        available_slots = request.form.getlist('available_slots')
        
        # 3. Basic Validation (Availability is now optional until the final step)
        if not all([name, email, password, dept_id, specialization]):
            flash("⚠️ Please fill all required fields.", "warning")
            return render_template("add_new_doctor.html", departments=departments)

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("❌ Doctor with this email already exists!", "danger")
            return render_template("add_new_doctor.html", departments=departments)

        try:
            # Hash the password before saving (Security Best Practice)
            # hashed_password = generate_password_hash(password)

            # 4. Create new User
            # Assuming your User model handles the 'name' field if necessary
            new_user = User(name=name, email=email, password=password, role="doctor")
            db.session.add(new_user)
            db.session.flush() # Get user_id before committing the whole transaction

            # 5. Create Doctor profile
            new_doctor = Doctor(
                name=name,
                email=email,
                password=password, # Use the password variable, hashed version preferred
                dept_id=dept_id,
                specialization=specialization,
                # NOTE: 'availability' column has been removed/ignored based on previous steps
                user_id=new_user.user_id
            )
            db.session.add(new_doctor)
            db.session.flush() # Get doctor_id

            # 6. Create DoctorAvailability Records (NEW LOGIC)
            if available_days and available_slots:
                for day in available_days:
                    for slot in available_slots:
                        new_schedule_slot = DoctorAvailability(
                            doctor_id=new_doctor.doctor_id,
                            day_of_week=day,
                            time_slot=slot
                        )
                        db.session.add(new_schedule_slot)
            
            # 7. Commit everything
            db.session.commit()
            flash("✅ Doctor and schedule successfully added!", "success")
            return redirect(url_for('add_doctor')) 

        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error adding doctor: {str(e)}", "danger")
            return render_template("add_new_doctor.html", departments=departments)

    # GET request → show empty form
    return render_template("add_new_doctor.html", departments=departments)




from flask import request, redirect, url_for, flash
# from .models import db, Doctor, DoctorAvailability, User # Ensure DoctorAvailability is imported



@app.route("/doctor-dept")
def doctor_dept():
    dept_name = request.args.get("name")
    dept_id = request.args.get("dept_id")

    if dept_id:
        department = Department.query.filter_by(dept_id=dept_id).first()
    elif dept_name:
        department = Department.query.filter_by(name=dept_name).first()
    else:
        flash("Invalid department request!", "danger")
        return redirect(url_for("patient_dash"))

    if not department:
        flash("Department not found!", "danger")
        return redirect(url_for("patient_dash"))

    doctors = Doctor.query.filter_by(dept_id=department.dept_id).all()

    return render_template("doctor_dept.html",
                           department=department,
                           doctors=doctors)


@app.route("/doctor-profile")
def doctor_profile():
    doctor_id = request.args.get("doctor_id")   # <-- GET doctor_id from URL query string

    if not doctor_id:
        return "Doctor ID missing"

    doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
    if not doctor:
        return "Doctor not found"

    department = Department.query.filter_by(dept_id=doctor.dept_id).first()

    return render_template(
        "doctor_profile.html",
        doctor=doctor,
        department=department
    )


@app.route("/patient-dash")
def patient_dash():

    if session.get("role") != "patient":
        flash("Unauthorized access.", "danger")
        return redirect(url_for("login"))

    user_id = session.get("user_id")
    this_user = User.query.get(user_id)

    # Fetch ALL appointments for this patient
    appointments = Appointment.query.filter_by(
        user_id=user_id
    ).order_by(Appointment.date.asc()).all()

    # Fetch all departments from database (dynamic display)
    departments = Department.query.all()

    return render_template(
        "patient_dash.html",
        this_user=this_user,
        appointments=appointments,
        departments=departments
    )




@app.route("/doctor-dash")
def doctor_dash():

    # ------------------------------------------------
    # 1. Check Login
    # ------------------------------------------------
    if "user_id" not in session:
        flash("Please login first!", "warning")
        return redirect(url_for("login"))

    if session.get("role") != "doctor":
        flash("Access denied!", "danger")
        return redirect(url_for("welcome"))

    user_id = session.get("user_id")

    this_user = User.query.get(user_id)

    # ------------------------------------------------
    # 2. Fetch Doctor Profile
    # ------------------------------------------------
    doctor = Doctor.query.filter_by(user_id=user_id).first()

    if not doctor:
        flash("Doctor profile not found!", "danger")
        return redirect(url_for("welcome"))

    # ================================================================
    # 3. UPCOMING APPOINTMENTS → For "Upcoming Appointments" table
    # ======================================================
    # ==========
    appointments = Appointment.query.filter_by(
        doctor_id=doctor.doctor_id,
        status="Booked"
    ).order_by(Appointment.date.asc()).all()

    # ================================================================
    # 4. COMPLETED TREATMENTS TODAY → For "Completed Treatments" table
    # ================================================================
    # Note: Patient history contains treatment details
    completed_treatments = PatientHistory.query.filter(
        PatientHistory.doctor_id == doctor.doctor_id,
        db.func.date(PatientHistory.created_at) == date.today()
    ).order_by(PatientHistory.created_at.desc()).all()

    # ================================================================
    # 5. Dashboard statistics (optional)
    # ================================================================
    total_appointments_today = Appointment.query.filter(
        Appointment.doctor_id == doctor.doctor_id,
        Appointment.date == date.today()
    ).count()

    total_assigned_patients = Appointment.query.filter_by(
        doctor_id=doctor.doctor_id
    ).count()

    # ================================================================
    # 6. Render doctor dashboard with required data
    # ================================================================
    return render_template(
        "doctor_dash.html",

        # For upcoming appointments table
        appointments=appointments,

        # For completed treatments table
        completed_treatments=completed_treatments,

        # Stats
        todays_count=total_appointments_today,
        total_patients=total_assigned_patients,

        # Logged-in doctor
        doctor=doctor,
        this_user=this_user
    )

@app.route("/",methods =["GET","POST"])
def welcome():
   return render_template("welcome.html")

@app.route("/admin-login",methods=["GET","POST"])
def admin_login():
   return render_template("admin_login.html")

@app.route("/doctor-login", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        # ✅ Basic field validation
        if not name or not password:
            flash("⚠️ Please enter both email and password.", "warning")
            return render_template("doctor_login.html")

        # ✅ Check if doctor exists in User table
        doctor_user = User.query.filter_by(name=name, role="doctor").first()

        if doctor_user and doctor_user.password == password:
            # ✅ Login success: store in session
            session["user_id"] = doctor_user.user_id
            session["role"] = "doctor"
            session["name"] = doctor_user.name

            flash(f"✅ Welcome Dr. {doctor_user.name}!", "success")
            return redirect(url_for("doctor_dash"))  # ← change route name as per your project

        else:
            flash("❌ Invalid email or password. Please try again.", "danger")
            return render_template("doctor_login.html")

    # GET request — show login page
    return render_template("doctor_login.html")




@app.route("/doctor-avail",methods=["GET","POST"])
def doctor_avail():
   return render_template("doctor_avail.html")
   
@app.route("/logout",methods=["GET","POST"])
def logout():
   return render_template("doctor_login.html")

@app.route("/cancel-appointment/<int:appt_id>", methods=["POST","GET"])
def cancel_appointment(appt_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect("/login")

    appointment = Appointment.query.get_or_404(appt_id)

    # Optional: prevent others from canceling others' appointments
    if appointment.user_id != user_id:
        flash("Unauthorized access", "danger")
        return redirect("/doctor-dash")

    db.session.delete(appointment)
    db.session.commit()
    flash("Appointment cancelled successfully!", "success")
    return redirect("/doctor-dash")  # or wherever your list page is

@app.route("/add_department", methods=["GET", "POST"])
def add_department():
    if request.method == "POST":
        # ✅ Get form data
        dept_name = request.form.get("name")
        description = request.form.get("description")

        # ✅ Validation check
        if not dept_name:
            flash("Department name is required!", "danger")
            return redirect(url_for("add_department"))

        # ✅ Check if department already exists
        existing = Department.query.filter_by(name=dept_name).first()
        if existing:
            flash("Department already exists!", "warning")
            return redirect(url_for("add_department"))

        # ✅ Create and save new department
        new_department = Department(name=dept_name, description=description)
        db.session.add(new_department)
        db.session.commit()

        flash("✅ Department added successfully!", "success")
        return redirect(url_for("add_department"))

    # GET request → render form
    return render_template("add_department.html")
# ============================================================
# ROUTE: Update Patient History
# ============================================================
@app.route("/update-patient-history/<int:user_id>", methods=["GET", "POST"])
def update_patient_history(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for("dashboard"))

    # You can later make this dynamic based on doctor login, etc.
    department = Department.query.filter_by(name="Cardiology").first()
    if not department:
        flash("Department not found!", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        visit_type = request.form.get("visit-type")
        test_done = request.form.get("test-done")
        diagnosis = request.form.get("diagnosis")
        medicines = request.form.get("medicines")
        prescription = request.form.get("prescription")

        new_history = PatientHistory(
            user_id=user.user_id,
            department_id=department.dept_id,
            visit_type=visit_type,
            test_done=test_done,
            diagnosis=diagnosis,
            medicines=medicines,
            prescription=prescription
        )

        db.session.add(new_history)
        db.session.commit()

        flash("✅ Patient history updated successfully!", "success")
        return redirect(url_for("update_patient_history_bp.update_patient_history", user_id=user_id))

    # Fetch previous patient histories for display (optional)
    history_records = PatientHistory.query.filter_by(user_id=user_id).order_by(PatientHistory.created_on.desc()).all()

    return render_template("update_patient_history.html", user=user, department=department, histories=history_records)









def is_role(expected_role):
    from flask import session
    return session.get('role') == expected_role

@app.route("/admin-dash")
def admin_dash():

    if not is_role('admin'):
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    this_user = User.query.get(user_id)

    # === Dashboard Counts ===
    doctor_count = Doctor.query.count()
    patient_count = User.query.filter_by(role='patient').count()

    # === Doctors and Patients List ===
    doctors_list = Doctor.query.all()
    patient_list = User.query.filter_by(role="patient").all()

    # === Departments List (ADDED) ===
    departments_list = Department.query.all()

    # === Latest 10 Appointments (JOIN FIXED) ===
    upcoming_appts = db.session.query(
        Appointment,
        User.name.label("patient_name"),
        Doctor.name.label("doctor_name"),
        Department.name.label("dept_name")
    ).join(
        User, Appointment.user_id == User.user_id
    ).join(
        Doctor, Appointment.doctor_id == Doctor.doctor_id
    ).join(
        Department, Doctor.dept_id == Department.dept_id
    ).order_by(
        Appointment.appointment_id.desc()
    ).limit(10).all()

    return render_template(
        "admin_dash.html",
        this_user=this_user,
        doctors_list=doctors_list,
        doctor_count=doctor_count,
        patient_count=patient_count,
        patient_list=patient_list,
        appointment_list=upcoming_appts,
        departments_list=departments_list   # <-- ADDED
    )





@app.route("/search")
def search():
    query = request.args.get("query", "").strip()

    # Search in doctors, departments, or anything you want
    results = []

    if query:
        results = Doctor.query.filter(Doctor.specialization.ilike(f"%{query}%")).all()

    return render_template("search_results.html", results=results, query=query)


from datetime import datetime

from flask import request, redirect, url_for, flash, render_template, session
from datetime import datetime
from sqlalchemy import func
# Assuming your models are defined and imported (db, Appointment, User, Department)
# from .models import db, Appointment, User, Department 

# --- CONFIGURATION CONSTANT ---
# Define the maximum number of appointments allowed for any slot
# MAX_APPOINTMENTS_PER_SLOT = 5

@app.route("/new-appointment", methods=["GET", "POST"])
def new_appointment():
    # 1. Authentication Check
    if "user_id" not in session:
        flash("Please log in to book an appointment.", "danger")
        return redirect(url_for("login")) # Use url_for for redirects

    # Retrieve the currently logged-in user
    user = User.query.get(session["user_id"])

    if request.method == "POST":
        try:
            # 2. Extract and Validate Form Data
            doctor_id = request.form.get("doctor_id", type=int)
            # Use user from session for security, not hidden form field
            user_id = session["user_id"] 
            
            date_str = request.form["date"]
            # Convert HTML date string to Python date object
            appointment_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            time_slot = request.form["time"]

            if not all([doctor_id, appointment_date, time_slot]):
                 flash("Missing appointment details. Please fill all fields.", "danger")
                 return redirect(url_for("new_appointment"))
            
            # 3. CRUCIAL: Final Server-Side Capacity Check
            # Count how many appointments already exist for this doctor, date, and time slot
            booked_count = db.session.query(Appointment).filter(
                Appointment.doctor_id == doctor_id,
                Appointment.date == appointment_date, 
                Appointment.time == time_slot
                # Optional: Filter out 'Cancelled' appointments if you allow re-booking
                # Appointment.status != 'Cancelled' 
            ).count()

            if booked_count >= MAX_APPOINTMENTS_PER_SLOT:
                # Limit reached, roll back any implicit transaction and reject booking
                flash(f"❌ This time slot ({time_slot}) is fully booked (Limit: {MAX_APPOINTMENTS_PER_SLOT}). Please choose another time or date.", "danger")
                return redirect(url_for("new_appointment")) 

            # 4. Create and Commit New Appointment (If limit not reached)
            new_appt = Appointment(
                doctor_id=doctor_id,
                user_id=user_id,
                date=appointment_date,
                time=time_slot, # Use the descriptive variable name
                status="Booked"
            )

            db.session.add(new_appt)
            db.session.commit()
            
            flash("✅ Appointment successfully booked!", "success")
            return redirect(url_for("patient_dash")) # Redirect to dashboard after successful booking

        except ValueError:
            # Handle error if date format is incorrect or doctor_id/user_id conversion fails
            flash("Invalid date or form submission error.", "danger")
            db.session.rollback()
            return redirect(url_for("new_appointment"))
            
        except Exception as e:
            # General error handling
            db.session.rollback()
            print(f"Booking Error: {e}")
            flash("An unexpected error occurred. Please try again.", "danger")
            return redirect(url_for("new_appointment"))

    # GET Request Logic: Render the form
    departments = Department.query.all()
    # Ensure you are passing the correct variables expected by your template
    return render_template("new_appointment.html", departments=departments, user=user)

@app.route('/check-availability', methods=['POST'])
def check_availability():
    """
    Checks the current number of bookings for a specific doctor, date, and time slot.
    Returns JSON status to the client-side JavaScript.
    """
    try:
        data = request.get_json()
        doctor_id = data.get('doctor_id')
        date_str = data.get('date') # Date is received as a string 'YYYY-MM-DD'
        time_slot = data.get('time')
        
        # 1. Validation check
        if not all([doctor_id, date_str, time_slot]):
            return jsonify({"error": "Missing required data for check."}), 400

        # Convert doctor_id to integer (it comes as string from JavaScript/JSON)
        doctor_id = int(doctor_id)

        # 2. Database Query
        # We query the Appointment model using the submitted criteria
        booked_count = db.session.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.date == date_str, # SQLAlchemy handles comparison with string 'YYYY-MM-DD'
            Appointment.time == time_slot
        ).count()

        # 3. Determine availability based on the constant limit
        is_available = booked_count < MAX_APPOINTMENTS_PER_SLOT
        remaining_slots = MAX_APPOINTMENTS_PER_SLOT - booked_count
        
        # Ensure remaining_slots is not negative
        if remaining_slots < 0:
            remaining_slots = 0

        # 4. Return result as JSON
        return jsonify({
            "is_available": is_available,
            "remaining_slots": remaining_slots
        })

    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error checking availability: {e}")
        return jsonify({"error": "An internal server error occurred during check."}), 500
    
from datetime import datetime
# from .models import db, Appointment, DoctorAvailability
from flask import request, jsonify
from datetime import datetime
# Assuming db, Appointment, DoctorAvailability are imported from your models file

MAX_APPOINTMENTS_PER_SLOT = 5

@app.route('/get-available-slots', methods=['POST'])
def get_available_slots():
    """
    Checks doctor's scheduled availability and current booking capacity 
    for a specific date.
    """
    try:
        # CRITICAL: Attempt to get JSON data
        data = request.get_json()
        
        # Check if JSON payload was correctly received
        if not data:
            print("ERROR: Request body is missing or not valid JSON.")
            return jsonify({"slots": [], "error": "Invalid request format. Must be JSON."}), 400
        
        doctor_id = data.get('doctor_id')
        date_str = data.get('date') 
        
        # 1. Validation check
        if not doctor_id or not date_str:
            return jsonify({"slots": [], "error": "Doctor and date required."}), 400
            
        # Ensure doctor_id is an integer for the query
        doctor_id = int(doctor_id)
        
        # Convert Date string to Day of Week and date object
        appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        day_name = appointment_date.strftime('%A') 

        # 2. Get the Doctor's Scheduled Slots for that Day (from DoctorAvailability model)
        scheduled_slots = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id, 
            day_of_week=day_name
        ).all()
        
        if not scheduled_slots:
            # Doctor is not scheduled to work on this specific day of the week
            return jsonify({"slots": []})

        available_slots = []

        # 3. For each scheduled slot, check the booking count (from Appointment model)
        for slot in scheduled_slots:
            time_slot_value = slot.time_slot
            
            booked_count = db.session.query(Appointment).filter(
                Appointment.doctor_id == doctor_id,
                Appointment.date == appointment_date,
                Appointment.time == time_slot_value
            ).count()
            
            remaining = MAX_APPOINTMENTS_PER_SLOT - booked_count
            
            # Only show the slot if it has capacity (remaining > 0)
            if remaining > 0:
                # Determine display label based on the stored value (09:00 AM or 02:00 PM)
                display_label = f"{time_slot_value} - { '01:00 PM' if time_slot_value == '09:00 AM' else '06:00 PM'}"

                available_slots.append({
                    'time_value': time_slot_value,
                    'time_label': display_label,
                    'remaining': remaining
                })
        
        return jsonify({"slots": available_slots})
    
    except ValueError as ve:
        # Catches errors like invalid date format (if date_str is bad) or doctor_id conversion
        print(f"DATA CONVERSION ERROR in /get-available-slots: {ve}")
        return jsonify({"slots": [], "error": "Invalid data submitted (e.g., date format)."}), 400

    except Exception as e:
        # Catches unexpected server crashes (e.g., database connection errors, SQLAlchemy issues)
        print(f"SERVER CRASH in /get-available-slots: {e}")
        # Return a 500 status to the client
        return jsonify({"slots": [], "error": "Internal Server Error."}), 500

@app.route("/get-doctors/<int:dept_id>", methods=["GET"])
def get_doctors(dept_id):
    try:
        doctors = Doctor.query.filter_by(dept_id=dept_id).all()
        doctor_data = [doc.to_dict() for doc in doctors]
        return jsonify(doctor_data)
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Failed to load doctors"}), 500


@app.route("/full-report/<int:history_id>")
def full_report(history_id):
    history = PatientHistory.query.get(history_id)
    if not history:
        flash("History record not found!", "danger")
        return redirect("/patient-dash")

    user = history.user
    department = history.department

    return render_template(
        "full_report.html",
        history=history,
        user=user,
        department=department
    )

@app.route("/mark-complete/<int:appt_id>", methods=["POST"])
def mark_complete(appt_id):
    appt = Appointment.query.get(appt_id)
    if not appt:
        flash("Appointment not found!", "danger")
        return redirect("/doctor-dash")

    appt.status = "Completed"
    db.session.commit()

    flash("Appointment marked as completed!", "success")
    return redirect("/doctor-dash")
@app.route('/save-treatment/<int:appt_id>', methods=['POST'])
def save_treatment(appt_id):

    # 1. Load Appointment
    appointment = Appointment.query.filter_by(appointment_id=appt_id).first()
    if not appointment:
        flash("Appointment not found!", "danger")
        return redirect(url_for('doctor_dash'))

    # 2. Extract patient user_id from appointment
    user_id = appointment.user_id

    # 3. Get doctor from appointment
    doctor = Doctor.query.filter_by(doctor_id=appointment.doctor_id).first()
    if not doctor:
        flash("Doctor data missing!", "danger")
        return redirect(url_for('doctor_dash'))

    # 4. Department of the doctor
    department_id = doctor.dept_id

    # 5. Get all form values
    diagnosis = request.form.get('diagnosis')
    visit_type = request.form.get('visit_type')
    medicines = request.form.get('medicines')
    test_done = request.form.get('test_done')
    prescription = request.form.get('prescription')
    notes = request.form.get('notes')  # Not saved in model (optional)

    # 6. Create PatientHistory entry
    history = PatientHistory(
        user_id=user_id,
        department_id=department_id,
        visit_type=visit_type,
        test_done=test_done,
        diagnosis=diagnosis,
        medicines=medicines,
        prescription=prescription
    )

    db.session.add(history)

    # 7. Mark appointment as Completed
    appointment.status = "Completed"

    db.session.commit()

    flash("Treatment details saved successfully!", "success")
    return redirect(url_for('doctor_dash'))
