from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Mock user database
USERS = {
    'supervisor@example.com': {
        'id': 'sup001',
        'password': 'password123',
        'name': 'Supervisor User',
        'email': 'supervisor@example.com',
        'role': 'supervisor'
    },
    'employee@example.com': {
        'id': 'emp001',
        'password': 'password123',
        'name': 'Employee User',
        'email': 'employee@example.com',
        'role': 'employee'
    }
}

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user and return user data"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = USERS.get(email)
    
    if not user or user['password'] != password:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return jsonify({
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'role': user['role']
    }), 200

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Backend is running'}), 200

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(debug=True, port=port, host='0.0.0.0')

