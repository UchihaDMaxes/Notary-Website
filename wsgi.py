"""WSGI entry point for production servers.

    gunicorn wsgi:app            (Linux / macOS – Render, Railway, VPS)
    pythonanywhere WSGI config   ->  from wsgi import app as application

Local development should keep using `python app.py`.
"""
from app import create_app

application = create_app()
app = application
