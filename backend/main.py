"""
Main entry point for uvicorn.
This file imports the app from app.main to allow running with 'uvicorn main:app'
"""
from app.main import app

__all__ = ["app"]
