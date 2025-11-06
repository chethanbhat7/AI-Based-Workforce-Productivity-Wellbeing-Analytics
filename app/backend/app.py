from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime
import re

load_dotenv()

# ==================== INPUT VALIDATION UTILITIES ====================

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password (minimal validation - just non-empty)
    """
    errors = []
    
    if not password or len(password.strip()) == 0:
        errors.append('Password is required')
    
    return len(errors) == 0, errors

def validate_phone(phone):
    """Validate phone number (basic format)"""
    if not phone:
        return True  # Phone is optional
    # Allow digits, spaces, dashes, and parentheses
    pattern = r'^[\d\s\-\+\(\)]{10,}$'
    return re.match(pattern, phone) is not None

def validate_name(name):
    """Validate name format"""
    if not name or len(name.strip()) == 0:
        return False, "Name cannot be empty"
    if len(name) > 120:
        return False, "Name cannot exceed 120 characters"
    # Allow letters, spaces, hyphens, and apostrophes
    if not re.match(r'^[a-zA-Z\s\-\']+$', name):
        return False, "Name can only contain letters, spaces, hyphens, and apostrophes"
    return True, None

def validate_string_field(value, field_name, max_length=120, required=False):
    """Generic string field validation"""
    if not value or len(str(value).strip()) == 0:
        if required:
            return False, f"{field_name} is required"
        return True, None
    
    if len(str(value)) > max_length:
        return False, f"{field_name} cannot exceed {max_length} characters"
    
    return True, None

app = Flask(__name__)
CORS(app)

# Ensure all responses are JSON
@app.before_request
def before_request():
    pass

@app.after_request
def after_request(response):
    # Ensure Content-Type is JSON for all responses
    if response.status_code >= 400:
        if response.content_type and 'application/json' not in response.content_type:
            response.data = jsonify({'error': response.get_json() or 'An error occurred'}).get_data()
            response.content_type = 'application/json'
    return response

# Error handler for bad requests
@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request'}), 400

# Error handler for not found
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

# Error handler for server errors
@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

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
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        # Validate email and password are provided
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Email should not exceed reasonable length
        if len(email) > 120:
            return jsonify({'error': 'Email is too long'}), 400
        
        # Try to find supervisor first
        supervisor = Supervisor.query.filter_by(email=email).first()
        if supervisor and supervisor.check_password(password):
            return jsonify(supervisor.to_dict()), 200
        
        # Try to find member
        member = Member.query.filter_by(email=email).first()
        if member and member.check_password(password):
            return jsonify(member.to_dict()), 200
        
        # Generic error message for security (don't reveal if email exists)
        return jsonify({'error': 'Invalid email or password'}), 401
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user (Supervisor or Member)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        name = data.get('name', '').strip()
        role = data.get('role', 'member').lower()  # 'supervisor' or 'member'
        phone = data.get('phone', '').strip()
        department = data.get('department', '').strip()
        
        # ==================== VALIDATION ====================
        
        # Validate email
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format. Please enter a valid email address'}), 400
        if len(email) > 120:
            return jsonify({'error': 'Email cannot exceed 120 characters'}), 400
        
        # Validate name
        name_valid, name_error = validate_name(name)
        if not name_valid:
            return jsonify({'error': name_error}), 400
        
        # Validate password
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        password_valid, password_errors = validate_password(password)
        if not password_valid:
            return jsonify({'error': 'Password requirements: ' + ', '.join(password_errors)}), 400
        
        # Validate phone (if provided)
        if phone and not validate_phone(phone):
            return jsonify({'error': 'Invalid phone number format'}), 400
        if len(phone) > 20:
            return jsonify({'error': 'Phone number cannot exceed 20 characters'}), 400
        
        # Validate department (supervisor only)
        if role == 'supervisor':
            dept_valid, dept_error = validate_string_field(department, 'Department', max_length=120, required=False)
            if not dept_valid:
                return jsonify({'error': dept_error}), 400
        
        # Validate role
        if role not in ['supervisor', 'member']:
            return jsonify({'error': 'Invalid role. Must be "supervisor" or "member"'}), 400
        
        # Check if user already exists in either table
        existing_supervisor = Supervisor.query.filter_by(email=email).first()
        existing_member = Member.query.filter_by(email=email).first()
        
        if existing_supervisor or existing_member:
            return jsonify({'error': 'This email is already registered. Please use a different email or try logging in'}), 409
        
        # ==================== CREATE USER ====================
        
        try:
            if role == 'supervisor':
                new_user = Supervisor(
                    id=str(uuid.uuid4()),
                    name=name,
                    email=email,
                    department=department if department else None,
                    phone=phone if phone else None,
                    is_active=True
                )
            else:  # member
                new_user = Member(
                    id=str(uuid.uuid4()),
                    name=name,
                    email=email,
                    phone=phone if phone else None,
                    is_active=True
                )
            
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({
                'message': 'User registered successfully',
                'user': new_user.to_dict()
            }), 201
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to create user. Please try again.'}), 500
    
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Backend is running'}), 200

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=True, port=port, host='0.0.0.0')

