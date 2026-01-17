from flask import render_template, request
from app.models.finance import Student, db
from flask import Blueprint

# Define the blueprint
portal = Blueprint('portal', __name__)

@portal.route('/')
def home():
    """Main landing page for Alber School Kutus with enrollment stats"""
    # Count total students to show on the dashboard
    total_enrolled = Student.query.count()
    return render_template('home.html', total_enrolled=total_enrolled)

@portal.route('/about')
def about():
    """About page for Alber School Kutus"""
    return render_template('about.html')

@portal.route('/admission', methods=['GET', 'POST'])
def admission():
    """Handles new student registrations via HTMX"""
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        cbc_grade = request.form.get('cbc_grade')
        parent_phone = request.form.get('parent_phone')

        try:
            # Create student record
            new_student = Student(
                full_name=full_name,
                cbc_grade=int(cbc_grade),
                parent_phone=parent_phone
            )
            db.session.add(new_student)
            db.session.commit()
            
            # Return success message snippet for HTMX
            return f'''
            <div class="p-4 bg-green-100 text-green-800 rounded-lg shadow-sm border border-green-200">
                ✅ Success! {full_name} has been admitted. 
                <a href="/students" class="underline font-bold ml-2">View List</a>
            </div>
            '''
        except Exception as e:
            db.session.rollback()
            # Handle duplicate phone numbers or database errors
            if "UNIQUE constraint failed" in str(e):
                return '<div class="p-4 bg-red-100 text-red-800 rounded-lg border border-red-200">❌ Error: This phone number is already registered.</div>'
            return f'<div class="p-4 bg-red-100 text-red-800 rounded-lg border border-red-200">❌ Error: {str(e)}</div>'

    return render_template('admission.html')

@portal.route('/students')
def list_students():
    """Displays all admitted students in a clean list"""
    all_students = Student.query.order_by(Student.id.desc()).all()
    return render_template('students.html', students=all_students)

@portal.route('/pay-fees')
def pay_fees():
    """Displays the M-Pesa fee payment form"""
    return render_template('pay_fees.html')