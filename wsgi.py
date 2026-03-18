"""WSGI Entry Point fuer Gunicorn.

Diese Datei wird von Gunicorn verwendet, um die Flask-App zu starten.
Beispiel: gunicorn wsgi:app --bind 0.0.0.0:20201
"""

from app import create_app

# Flask-App-Instanz erstellen
app = create_app()
