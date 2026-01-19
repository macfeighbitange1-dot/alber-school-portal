import os
from flask import render_template, request, redirect, url_for, flash, abort, Blueprint
from flask_login import login_required, current_user
from app.models.finance import Student, db, Notification, FeeTransaction
from functools import wraps
from mistralai import Mistral # Updated import for 2026 syntax

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

# --- AI TUTOR API ROUTE ---
@portal.route('/api/ai-tutor', methods=['POST'])
def ai_tutor():
    """Handles the AI Homework Helper logic using Mistral AI"""
    user_query = request.form.get('student_query')
    api_key = os.environ.get("MISTRAL_API_KEY")
    
    if not api_key:
        return '<div class="p-4 bg-yellow-100 text-yellow-800 rounded-lg">AI Error: API Key missing in environment.</div>'

    try:
        # Initializing the new 2026 Mistral Client
        client = Mistral(api_key=api_key)
        
        chat_response = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": "You are Teacher AI, a friendly and helpful tutor for CBC students at Alber School Kutus."},
                {"role": "user", "content": user_query}
            ]
        )
        answer = chat_response.choices[0].message.content
        
        return f'''
        <div class="bg-blue-50 p-6 rounded-2xl border border-blue-100 shadow-inner prose max-w-none">
            <p class="text-blue-900 leading-relaxed">{answer}</p>
        </div>
        '''
    except Exception as e:
        return f'<div class="p-4 bg-red-100 text-red-800 rounded-lg">Teacher AI Error: {str(e)}</div>'

# --- ADMIN ONLY ROUTES ---
@portal.route('/admission', methods=['GET', 'POST'])
@login_required
@admin_required
def admission():
    """Handles new registrations"""
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

@portal.route('/post-notification', methods=['POST'])
@login_required
@admin_required
def post_notification():
    """Admin route to broadcast messages to student dashboards"""
    title = request.form.get('title')
    message = request.form.get('message')
    
    try:
        new_notif = Notification(title=title, message=message, target_role='student')
        db.session.add(new_notif)
        db.session.commit()
        return '<div class="text-green-600 font-bold p-2 bg-green-50 rounded">✅ Broadcast sent successfully!</div>'
    except Exception as e:
        return f'<div class="text-red-600 p-2 bg-red-50 rounded">❌ Failed to send: {str(e)}</div>'

# --- STUDENT ONLY ROUTES ---
@portal.route('/dashboard')
@login_required
def dashboard():
    """Personal portal for students"""
    if current_user.role == 'admin':
        return redirect(url_for('portal.list_students'))
    
    student = current_user.student_profile
    if not student:
        flash("Student profile not found. Please contact administration.", "warning")
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
    """Student fee payment page"""
    return render_template('pay_fees.html', student=current_user.student_profile)