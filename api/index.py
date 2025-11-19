"""
Vercel serverless function entry point for FastAPI application
"""
import sys
import os

# Add the parent directory to the path so we can import app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app.main import app

# Vercel Python runtime expects the handler to be named 'handler'
handler = app

