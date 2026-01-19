from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # 1. Smarter Configuration
    database_url = os.environ.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('DATABASE_URL')
    
    if not database_url:
        database_url = 'sqlite:///school.db'
        
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 2. Initialize Plugins
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 3. Import Models (Critical for database visibility)
    from app.models.finance import Student, FeeTransaction
    
    # 4. Register Blueprints
    from app.routes import auth, portal, api, payments_bp
    
    app.register_blueprint(auth)
    app.register_blueprint(portal)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(payments_bp) 

    # 5. AUTO-CREATE TABLES (The Fix for Internal Server Error)
    # This block runs every time the app starts and ensures 
    # the database tables exist without manual commands.
    with app.app_context():
        try:
            db.create_all()
            print("Database tables initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    return app