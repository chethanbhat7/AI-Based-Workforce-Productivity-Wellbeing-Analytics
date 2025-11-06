"""
Token encryption utilities
"""
from cryptography.fernet import Fernet
from config import get_encryption_key
import base64

# Initialize Fernet cipher
_cipher = None


def get_cipher():
    """Get or create Fernet cipher"""
    global _cipher
    if _cipher is None:
        key = get_encryption_key()
        _cipher = Fernet(key)
    return _cipher


def encrypt_token(token: str) -> str:
    """Encrypt a token for secure storage"""
    if not token:
        return ""
    
    cipher = get_cipher()
    encrypted = cipher.encrypt(token.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a stored token"""
    if not encrypted_token:
        return ""
    
    try:
        cipher = get_cipher()
        encrypted_bytes = base64.b64decode(encrypted_token.encode())
        decrypted = cipher.decrypt(encrypted_bytes)
        return decrypted.decode()
    except Exception as e:
        raise ValueError(f"Failed to decrypt token: {e}")
