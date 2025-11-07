"""
Single Serverless Function Entry Point for Vercel
This consolidates all API routes into ONE serverless function
"""
from main import app

# Vercel will call this handler for all /api/* requests
def handler(request, response):
    """Single handler for all API requests"""
    return app(request, response)
