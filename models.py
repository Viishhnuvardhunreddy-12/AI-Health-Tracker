import os
import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.ensemble import IsolationForest
import numpy as np
import pandas as pd

# Initialize SQLAlchemy
db = SQLAlchemy()

# Legacy data file path for migration purposes
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'vitals.json')
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

# User model for authentication
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationship with vitals data
    vitals = db.relationship('VitalsData', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

# Vitals data model
class VitalsData(db.Model):
    __tablename__ = 'vitals_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    heart_rate = db.Column(db.Integer)
    sleep_hours = db.Column(db.Float)
    steps = db.Column(db.Integer)
    mood = db.Column(db.Integer)
    stress_level = db.Column(db.Integer, nullable=True)
    date = db.Column(db.Date, default=datetime.date.today)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return f'<VitalsData {self.id} for user {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'heart_rate': self.heart_rate,
            'sleep_hours': self.sleep_hours,
            'steps': self.steps,
            'mood': self.mood,
            'stress_level': self.stress_level,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

def save_vitals(vitals_data):
    """Save vitals data to database"""
    # Check if user exists (by email)
    user = None
    if 'email' in vitals_data and vitals_data['email']:
        user = User.query.filter_by(email=vitals_data['email']).first()
    
    # If no user found and we have enough info, create a temporary user
    if not user and 'email' in vitals_data and vitals_data['email']:
        user = User(
            username=vitals_data['email'].split('@')[0],  # Use part before @ as username
            email=vitals_data['email'],
            name=vitals_data.get('name', 'Anonymous')
        )
        if 'phone' in vitals_data:
            user.phone = vitals_data['phone']
        
        # Add temporary password (user will need to reset)
        user.set_password('temporary')
        db.session.add(user)
        db.session.commit()
    
    # Create vitals record
    vitals = VitalsData(
        heart_rate=vitals_data.get('heart_rate', 0),
        sleep_hours=vitals_data.get('sleep_hours', 0),
        steps=vitals_data.get('steps', 0),
        mood=int(vitals_data.get('mood', 0)) if isinstance(vitals_data.get('mood'), str) else vitals_data.get('mood', 0),
        stress_level=vitals_data.get('stress_level'),
        date=datetime.datetime.now().date(),
        timestamp=datetime.datetime.now()
    )
    
    # Associate with user if we have one
    if user:
        vitals.user_id = user.id
    
    db.session.add(vitals)
    db.session.commit()
    
    # Return the data in the expected format for compatibility
    result = vitals.to_dict()
    if user:
        result['name'] = user.name
        result['email'] = user.email
        result['phone'] = user.phone
    
    return result

def get_recent_vitals(days=7, user_id=None):
    """Get recent vitals data from database"""
    cutoff_date = (datetime.datetime.now() - datetime.timedelta(days=days)).date()
    
    query = VitalsData.query.filter(VitalsData.date >= cutoff_date)
    
    # Filter by user if specified
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    # Order by date
    query = query.order_by(VitalsData.date)
    
    # Convert to list of dictionaries
    vitals_list = [v.to_dict() for v in query.all()]
    
    # Add user info to each record
    for vital in vitals_list:
        if vital['user_id']:
            user = User.query.get(vital['user_id'])
            if user:
                vital['name'] = user.name
                vital['email'] = user.email
                if hasattr(user, 'phone'):
                    vital['phone'] = user.phone
    
    return vitals_list

def analyze_vitals(vitals_data):
    """Analyze vitals data using machine learning to detect anomalies"""
    if not vitals_data:
        return {"anomalies": []}
    
    # Convert to DataFrame
    df = pd.DataFrame(vitals_data)
    
    # Select numerical features
    features = ['heart_rate', 'sleep_hours', 'steps', 'mood']
    
    # Check if all features exist in the data
    if not all(feature in df.columns for feature in features):
        return {"anomalies": []}
    
    X = df[features].values
    
    # Train isolation forest model
    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X)
    
    # Predict anomalies
    predictions = model.predict(X)
    anomaly_indices = np.where(predictions == -1)[0]
    
    # Get anomalies
    anomalies = []
    for idx in anomaly_indices:
        anomaly_date = df.iloc[idx]['date']
        anomaly_data = {k: df.iloc[idx][k] for k in features if k in df.iloc[idx]}
        
        # Determine which vital is most anomalous
        anomaly_type = None
        if 'heart_rate' in df.iloc[idx] and (df.iloc[idx]['heart_rate'] > 100 or df.iloc[idx]['heart_rate'] < 50):
            anomaly_type = 'heart_rate'
        elif 'sleep_hours' in df.iloc[idx] and df.iloc[idx]['sleep_hours'] < 6:
            anomaly_type = 'sleep_hours'
        elif 'mood' in df.iloc[idx] and df.iloc[idx]['mood'] <= 2:
            anomaly_type = 'mood'
        
        anomalies.append({
            'date': anomaly_date,
            'data': anomaly_data,
            'type': anomaly_type
        })
    
    return {"anomalies": anomalies}

# Function to get user by ID
def get_user_by_id(user_id):
    return User.query.get(user_id)

# Function to get user by email
def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

# Function to migrate legacy data to database
def migrate_legacy_data():
    """Migrate data from JSON file to database"""
    if not os.path.exists(DATA_FILE):
        return 0
    
    try:
        with open(DATA_FILE, 'r') as f:
            all_data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return 0
    
    # Track users created/updated
    users_created = 0
    records_migrated = 0
    
    for data in all_data:
        # Check if user exists
        user = None
        if 'email' in data and data['email']:
            user = User.query.filter_by(email=data['email']).first()
        
        # Create user if not exists
        if not user and 'email' in data and data['email']:
            username = data['email'].split('@')[0]
            # Check if username exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                username = f"{username}_{users_created}"
            
            user = User(
                username=username,
                email=data['email'],
                name=data.get('name', 'Anonymous')
            )
            if 'phone' in data:
                user.phone = data['phone']
            
            # Set temporary password
            user.set_password('temporary')
            db.session.add(user)
            db.session.commit()
            users_created += 1
        
        # Create vitals record
        if 'date' in data and data['date']:
            try:
                record_date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
            except ValueError:
                record_date = datetime.date.today()
        else:
            record_date = datetime.date.today()
            
        if 'timestamp' in data and data['timestamp']:
            try:
                record_timestamp = datetime.datetime.fromisoformat(data['timestamp'])
            except ValueError:
                record_timestamp = datetime.datetime.now()
        else:
            record_timestamp = datetime.datetime.now()
        
        vitals = VitalsData(
            heart_rate=data.get('heart_rate', 0),
            sleep_hours=data.get('sleep_hours', 0),
            steps=data.get('steps', 0),
            mood=data.get('mood', 0),
            stress_level=data.get('stress_level'),
            date=record_date,
            timestamp=record_timestamp
        )
        
        # Associate with user if we have one
        if user:
            vitals.user_id = user.id
        
        db.session.add(vitals)
        records_migrated += 1
    
    db.session.commit()
    return records_migrated