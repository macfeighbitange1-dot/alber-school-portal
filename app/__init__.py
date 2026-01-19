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
    # This checks Render's environment variable first, then DATABASE_URL, 
    # and finally falls back to a local sqlite file so it NEVER crashes.
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
    # Ensure these paths match your folder structure exactly
    from app.models.finance import Student, FeeTransaction
    
    # 4. Register Blueprints
    from app.routes import auth, portal, api, payments_bp
    
    app.register_blueprint(auth)
    app.register_blueprint(portal)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(payments_bp) 
    
    return app