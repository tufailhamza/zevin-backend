"""
Vercel serverless function entry point for FastAPI application
"""
import sys
import os

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Vercel expects the handler to be named 'handler' or 'app'
# For FastAPI, we can export the app directly
handler = app

