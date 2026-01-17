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
    
    # 1. Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 2. Initialize Plugins
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 3. Import Models (Critical for database visibility)
    from app.models.finance import Student, FeeTransaction
    
    # 4. Register Blueprints
    # We import the objects from app.routes
    from app.routes import auth, portal, api, payments_bp
    
    app.register_blueprint(auth)
    app.register_blueprint(portal)
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(payments_bp) 
    
    return app