from flask import Flask
from dotenv import load_dotenv
import os
import google.generativeai as genai
from app.email_service import init_app as init_mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Import db instance from models
from app.models import db

# Load environment variables
load_dotenv()

# Initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

def create_app():
    # Create the Flask app with explicit name to avoid lazy loading
    app = Flask("health_tracker", 
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"),
                static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"))
    
    # Configure the app
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-for-testing')
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'health_tracker.db'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configure Gemini API directly in the app initialization
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    app.config['GEMINI_API_KEY'] = gemini_api_key
    
    # Configure Open Router API - Use the API key from .env file with fallback
    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
    app.config['OPENROUTER_API_KEY'] = openrouter_api_key
    
    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Initialize login manager
    login_manager.init_app(app)
    
    # Configure Gemini API
    try:
        genai.configure(api_key=gemini_api_key)
        print(f"Gemini API configured in app with key: {gemini_api_key[:5]}...{gemini_api_key[-5:]}")
    except Exception as e:
        print(f"Error configuring Gemini API in app: {str(e)}")
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Register auth blueprint
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    # Initialize email service
    init_mail(app)
    
    # Print configuration status
    print(f"Flask app initialized with Open Router API key: {openrouter_api_key[:5]}...{openrouter_api_key[-5:]}")
    
    # Setup user loader
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        print("Database tables created or verified.")
    
    return app
