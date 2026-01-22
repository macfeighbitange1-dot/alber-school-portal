from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.finance import User, db

# Define the blueprint
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, don't show the login page
    if current_user.is_authenticated:
        return redirect(url_for('portal.home'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Query user from database
        user = User.query.filter_by(username=username).first()
        
        # Verify user and password
        if user and user.check_password(password):
            login_user(user)
            # Redirect to home or the page they were trying to access
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('portal.home'))
        
        flash('Invalid username or password', 'danger')

    # Direct reference to the template we just fixed
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('portal.home'))