from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # 1. Configuration logic
    database_url = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI')
    # Fix for Render/Heroku postgres URLs (they often start with postgres:// instead of postgresql://)
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
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
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = "info"
    
    # 3. Import Models (Ensures they are registered with SQLAlchemy)
    from app.models.finance import Student, User, Notification, FeeTransaction

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 4. Register Blueprints
    from app.routes import auth, portal, api, payments_bp
    app.register_blueprint(auth)
    app.register_blueprint(portal)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(payments_bp) 

    # 5. Database Initialization & Seeding logic
    with app.app_context():
        try:
            db.create_all()
            
            # Create an Admin if none exists
            if not User.query.filter_by(role='admin').first():
                admin = User(username="admin", role="admin")
                admin.set_password("admin123")
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin created: admin/admin123")

            # Create Fake Students if none exist
            if not Student.query.first():
                # Create Student User Accounts
                s1_user = User(username="john_doe", role="student")
                s1_user.set_password("student123")
                
                s2_user = User(username="jane_smith", role="student")
                s2_user.set_password("student123")

                db.session.add_all([s1_user, s2_user])
                db.session.flush() # Flushes to get IDs for the profiles

                # Create the Student Profiles linked to Users
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
                
                # Create a welcome notification
                note = Notification(
                    title="Term 1 Opening",
                    message="Welcome to Alber School Kutus! Please check your fee balance for Term 1.",
                    target_role="student"
                )

                db.session.add_all([s1, s2, note])
                db.session.commit()
                print("✅ Seeded fake data (Students & Notifications)")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Database error on startup: {e}")
    
    return app