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
    
    # Standardize Postgres URL for SQLAlchemy 1.4+
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
    login_manager.login_view = 'auth.login'  # Matches the 'auth' blueprint + 'login' function
    login_manager.login_message_category = "info"
    
    # 3. Import Models
    from app.models.finance import Student, User, Notification, FeeTransaction

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 4. Register Blueprints (Fixed Explicit Imports)
    # We import the actual Blueprint objects from the route files
    from app.routes.auth import auth as auth_bp
    from app.routes.portal import portal as portal_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(portal_bp)

    # Optional: Register API and Payments if files exist
    try:
        from app.routes import api as api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
    except ImportError:
        pass

    try:
        from app.routes import payments_bp
        app.register_blueprint(payments_bp)
    except ImportError:
        pass

    # 5. Database Initialization & Seeding logic
    with app.app_context():
        try:
            db.create_all()
            
            # Create Admin if missing
            if not User.query.filter_by(role='admin').first():
                admin = User(username="admin", role="admin")
                admin.set_password("admin123")
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin created: admin/admin123")

            # Create Students if missing
            if not Student.query.first():
                s1_user = User(username="john_doe", role="student")
                s1_user.set_password("student123")
                
                s2_user = User(username="jane_smith", role="student")
                s2_user.set_password("student123")

                db.session.add_all([s1_user, s2_user])
                db.session.flush() 

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
                
                note = Notification(
                    title="Term 1 Opening",
                    message="Welcome to Alber School Kutus! Please clear your fees.",
                    target_role="student"
                )

                db.session.add_all([s1, s2, note])
                db.session.commit()
                print("✅ Seeded fake data!")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Startup Error: {e}")
    
    return app