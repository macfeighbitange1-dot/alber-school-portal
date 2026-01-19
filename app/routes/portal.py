from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models.finance import Student, db, Notification, FeeTransaction
from flask import Blueprint
from functools import wraps

# Define the blueprint
portal = Blueprint('portal', __name__)

# --- SECURITY DECORATOR ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Access denied: Admins only.", "danger")
            return redirect(url_for('portal.home'))
        return f(*args, **kwargs)
    return decorated_function

# --- PUBLIC ROUTES ---
@portal.route('/')
def home():
    """Main landing page for Alber School Kutus"""
    total_enrolled = Student.query.count()
    return render_template('home.html', total_enrolled=total_enrolled)

@portal.route('/about')
def about():
    """About page"""
    return render_template('about.html')

# --- ADMIN ONLY ROUTES ---
@portal.route('/admission', methods=['GET', 'POST'])
@login_required
@admin_required
def admission():
    """Handles new registrations (Only Admins can see/submit this)"""
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        cbc_grade = request.form.get('cbc_grade')
        parent_phone = request.form.get('parent_phone')
        admission_no = request.form.get('admission_no') # New field

        try:
            new_student = Student(
                full_name=full_name,
                cbc_grade=int(cbc_grade),
                parent_phone=parent_phone,
                admission_no=admission_no
            )
            db.session.add(new_student)
            db.session.commit()
            
            return f'''
            <div class="p-4 bg-green-100 text-green-800 rounded-lg shadow-sm">
                ✅ Success! {full_name} admitted as {admission_no}.
                <a href="/students" class="underline font-bold ml-2">View List</a>
            </div>
            '''
        except Exception as e:
            db.session.rollback()
            return f'<div class="p-4 bg-red-100 text-red-800 rounded-lg">❌ Error: {str(e)}</div>'

    return render_template('admission.html')

@portal.route('/students')
@login_required
@admin_required
def list_students():
    """Staff view of all students"""
    all_students = Student.query.order_by(Student.admission_no.asc()).all()
    return render_template('students.html', students=all_students)

# --- STUDENT ONLY ROUTES ---
@portal.route('/dashboard')
@login_required
def dashboard():
    """Personal portal for students to see fees and notifications"""
    if current_user.role == 'admin':
        return redirect(url_for('portal.list_students'))
    
    # Get the student profile linked to this user
    student = current_user.student_profile
    if not student:
        flash("Student profile not found.", "warning")
        return redirect(url_for('portal.home'))
    
    # Fetch data specific to this student
    notifications = Notification.query.filter_by(target_role='student').order_by(Notification.created_at.desc()).all()
    recent_fees = FeeTransaction.query.filter_by(student_id=student.id).limit(5).all()
    
    return render_template('student_dashboard.html', 
                           student=student, 
                           notifications=notifications,
                           recent_fees=recent_fees)

@portal.route('/pay-fees')
@login_required
def pay_fees():
    """Student fee payment page"""
    return render_template('pay_fees.html', student=current_user.student_profile)