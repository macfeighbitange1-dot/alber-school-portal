import os
from flask import render_template, request, redirect, url_for, flash, Blueprint
from flask_login import login_required, current_user
from app.models.finance import Student, db, Notification, FeeTransaction
from functools import wraps
from mistralai import Mistral

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
    try:
        total_enrolled = Student.query.count()
    except:
        total_enrolled = 0
    return render_template('home.html', total_enrolled=total_enrolled)

@portal.route('/about')
def about():
    """About page"""
    return render_template('about.html')

# --- AI TUTOR API ROUTE ---
@portal.route('/api/ai-tutor', methods=['POST'])
def ai_tutor():
    """Handles the AI Homework Helper logic using Mistral AI"""
    user_query = request.form.get('student_query')
    api_key = os.environ.get("MISTRAL_API_KEY")
    
    if not api_key:
        return '<div class="p-4 bg-yellow-100 text-yellow-800 rounded-lg">AI Error: API Key missing in environment.</div>'

    try:
        client = Mistral(api_key=api_key)
        chat_response = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": "You are Teacher AI, a tutor for Alber School Kutus."},
                {"role": "user", "content": user_query}
            ]
        )
        answer = chat_response.choices[0].message.content
        return f'<div class="bg-blue-50 p-6 rounded-2xl border border-blue-100 shadow-inner prose max-w-none"><p class="text-blue-900">{answer}</p></div>'
    except Exception as e:
        return f'<div class="p-4 bg-red-100 text-red-800 rounded-lg">Teacher AI Error: {str(e)}</div>'

# --- ADMIN ONLY ROUTES ---
@portal.route('/admission', methods=['GET', 'POST'])
@login_required
@admin_required
def admission():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        cbc_grade = request.form.get('cbc_grade')
        parent_phone = request.form.get('parent_phone')
        admission_no = request.form.get('admission_no')

        try:
            new_student = Student(
                full_name=full_name,
                cbc_grade=int(cbc_grade),
                parent_phone=parent_phone,
                admission_no=admission_no
            )
            db.session.add(new_student)
            db.session.commit()
            return f'<div class="p-4 bg-green-100 text-green-800 rounded-lg shadow-sm">✅ Success! {full_name} admitted. <a href="/students" class="underline font-bold ml-2">View List</a></div>'
        except Exception as e:
            db.session.rollback()
            return f'<div class="p-4 bg-red-100 text-red-800 rounded-lg">❌ Error: {str(e)}</div>'
    return render_template('admission.html')

@portal.route('/students')
@login_required
@admin_required
def list_students():
    all_students = Student.query.order_by(Student.admission_no.asc()).all()
    return render_template('students.html', students=all_students)

# --- STUDENT ONLY ROUTES ---
@portal.route('/dashboard')
@login_required
def dashboard():
    # If Admin clicks this, redirect them to the staff view
    if current_user.role == 'admin':
        return redirect(url_for('portal.list_students'))
    
    # Safe check for student profile to prevent 500 Error
    student = getattr(current_user, 'student_profile', None)
    
    if not student:
        flash("Student profile not found. Please contact the Admin.", "warning")
        return redirect(url_for('portal.home'))
    
    notifications = Notification.query.filter_by(target_role='student').order_by(Notification.created_at.desc()).all()
    recent_fees = FeeTransaction.query.filter_by(student_id=student.id).limit(5).all()
    
    return render_template('student_dashboard.html', 
                           student=student, 
                           notifications=notifications,
                           recent_fees=recent_fees)

@portal.route('/pay-fees')
@login_required
def pay_fees():
    student = getattr(current_user, 'student_profile', None)
    if not student:
        flash("You need a student profile to access the payment portal.", "danger")
        return redirect(url_for('portal.home'))
    return render_template('pay_fees.html', student=student)