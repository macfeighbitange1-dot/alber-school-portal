from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.finance import User, db

# Define the blueprint name as 'auth'
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in, send them to the home page
    if current_user.is_authenticated:
        return redirect(url_for('portal.home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        # Find the user in the database
        user = User.query.filter_by(username=username).first()

        # Check if user exists and password is correct
        # Note: This assumes your User model has a check_password method
        if not user or not user.check_password(password):
            flash('Please check your login details and try again.', 'danger')
            return redirect(url_for('auth.login'))

        # Log the user in
        login_user(user, remember=remember)
        
        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('portal.list_students'))
        return redirect(url_for('portal.dashboard'))

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('portal.home'))