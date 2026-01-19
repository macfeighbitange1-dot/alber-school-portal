from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # 1. Configuration
    database_url = os.environ.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('DATABASE_URL')
    if not database_url:
        database_url = 'sqlite:///school.db'
        
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 2. Initialize Plugins
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Setup Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Redirects users here if they aren't logged in
    login_manager.login_message_category = "info"
    
    # 3. Import Models
    from app.models.finance import Student, User, Notification, FeeTransaction

    # User Loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)
    
    # 4. Register Blueprints
    from app.routes import auth, portal, api, payments_bp
    app.register_blueprint(auth)
    app.register_blueprint(portal)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(payments_bp) 

    # 5. Database Initialization & Seeding
    with app.app_context():
        try:
            db.create_all()
            
            # --- SEEDING FAKE DATA ---
            # Create an Admin if none exists
            if not User.query.filter_by(role='admin').first():
                admin = User(username="admin", role="admin")
                admin.set_password("admin123") # Default password
                db.session.add(admin)
                print("✅ Created Admin: user: admin, pass: admin123")

            # Create Fake Students if none exist
            if not Student.query.first():
                # Create User Accounts for Students
                s1_user = User(username="john_doe", role="student")
                s1_user.set_password("student123")
                
                s2_user = User(username="jane_smith", role="student")
                s2_user.set_password("student123")

                db.session.add_all([s1_user, s2_user])
                db.session.flush() # Gets the IDs for the relationships

                # Create Student Profiles
                s1 = Student(
                    full_name="John Doe", 
                    admission_no="2026/001", 
                    cbc_grade=4, 
                    parent_phone="0711222333",
                    user_id=s1_user.id
                )
                s2 = Student(
                    full_name="Jane Smith", 
                    admission_no="2026/002", 
                    cbc_grade=5, 
                    parent_phone="0722333444",
                    user_id=s2_user.id
                )
                
                # Add a Fake Notification
                note = Notification(
                    title="Term 1 Opening",
                    message="Welcome back! School reopens on Jan 5th. Please clear your fees.",
                    target_role="student"
                )

                db.session.add_all([s1, s2, note])
                db.session.commit()
                print("✅ Seeded fake students and notifications!")

        except Exception as e:
            print(f"❌ Error during startup: {e}")
    
    return app