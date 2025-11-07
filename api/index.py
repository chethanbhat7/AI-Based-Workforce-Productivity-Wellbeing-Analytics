"""
Single Serverless Function Entry Point for Vercel
This consolidates all API routes into ONE serverless function
"""
from main import app

# Export for Vercel - the ASGI app is automatically detected
__all__ = ['app']
