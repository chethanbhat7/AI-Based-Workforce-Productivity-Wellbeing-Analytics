from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database Configuration - PostgreSQL (default) or SQLite (development)
database_url = os.getenv('DATABASE_URL', None)

# If no DATABASE_URL is set, use SQLite for development
if not database_url or database_url.startswith('sqlite'):
    database_url = 'sqlite:///workforce.db'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Supervisor Model
class Supervisor(db.Model):
    __tablename__ = 'supervisors'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': 'supervisor',
            'department': self.department,
            'phone': self.phone,
            'is_active': self.is_active,
        }

# Member Model
class Member(db.Model):
    __tablename__ = 'members'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': 'member',
            'phone': self.phone,
            'is_active': self.is_active,
        }

# Initialize database
with app.app_context():
    db.create_all()

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user (Supervisor or Member) and return user data"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Try to find supervisor first
    supervisor = Supervisor.query.filter_by(email=email).first()
    if supervisor and supervisor.check_password(password):
        return jsonify(supervisor.to_dict()), 200
    
    # Try to find member
    member = Member.query.filter_by(email=email).first()
    if member and member.check_password(password):
        return jsonify(member.to_dict()), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user (Supervisor or Member)"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', 'member')  # 'supervisor' or 'member'
    phone = data.get('phone', '')
    department = data.get('department', '')
    
    # Check if user already exists in either table
    existing_supervisor = Supervisor.query.filter_by(email=email).first()
    existing_member = Member.query.filter_by(email=email).first()
    
    if existing_supervisor or existing_member:
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user based on role
    if role == 'supervisor':
        new_user = Supervisor(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            department=department,
            phone=phone,
            is_active=True
        )
    else:  # member
        new_user = Member(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            phone=phone,
            is_active=True
        )
    
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully', 'user': new_user.to_dict()}), 201

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Backend is running'}), 200

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=True, port=port, host='0.0.0.0')

