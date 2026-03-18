"""Konfigurationsdatei fuer die Flask-Applikation.

Laedt Einstellungen aus Umgebungsvariablen (.env-Datei)
und stellt sie der Applikation zur Verfuegung.
"""

import os
from dotenv import load_dotenv

# .env-Datei laden (falls vorhanden)
load_dotenv()


class Config:
    """Basis-Konfigurationsklasse.

    Alle Konfigurationswerte werden aus Umgebungsvariablen gelesen.
    Standardwerte sind fuer die Entwicklung vorgesehen.
    """

    # Geheimer Schluessel fuer Session-Cookies und CSRF-Schutz
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-bitte-aendern')

    # Datenbankverbindung (PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://zeiterfassung_user:sicheres_passwort@localhost:5432/zeiterfassung_db'
    )

    # SQLAlchemy-Einstellungen
    SQLALCHEMY_TRACK_MODIFICATIONS = False
