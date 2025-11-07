"""
Firebase Admin SDK Configuration
"""
import firebase_admin
from firebase_admin import credentials, firestore
from pathlib import Path
import os
import json

# Initialize Firebase Admin SDK
_app = None
_db = None

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global _app, _db
    
    if _app is not None:
        return _db
    
    # Try to find service account key
    possible_paths = [
        Path(__file__).parent / "firebase-service-account.json",
        Path(__file__).parent.parent / "firebase-service-account.json",
        Path.home() / ".firebase" / "service-account.json",
    ]
    
    # Also check environment variable
    env_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
    if env_path:
        possible_paths.insert(0, Path(env_path))
    
    # Try each path
    cred = None
    for path in possible_paths:
        if path.exists():
            try:
                cred = credentials.Certificate(str(path))
                print(f"✅ Found Firebase service account key at: {path}")
                break
            except Exception as e:
                print(f"⚠️  Failed to load Firebase credentials from {path}: {e}")
                continue
    
    # If no file found, try environment variable with JSON
    if cred is None:
        env_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if env_json:
            try:
                service_account_info = json.loads(env_json)
                cred = credentials.Certificate(service_account_info)
                print("✅ Loaded Firebase credentials from environment variable")
            except Exception as e:
                print(f"⚠️  Failed to load Firebase credentials from env variable: {e}")
    
    if cred is None:
        print("⚠️  Firebase service account key not found - will use local storage fallback")
        return None
    
    # Initialize the app
    try:
        _app = firebase_admin.initialize_app(cred)
        _db = firestore.client()
        print("✅ Firebase Admin SDK initialized successfully")
        return _db
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Firebase Admin SDK: {e}")


def get_firestore_db():
    """Get Firestore database instance"""
    global _db
    if _db is None:
        _db = initialize_firebase()
    return _db


# Auto-initialize on import
try:
    initialize_firebase()
except Exception as e:
    print(f"⚠️  Firebase initialization will be attempted on first use: {e}")
