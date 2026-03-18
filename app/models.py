"""Datenbankmodelle fuer die Zeiterfassungs-Anwendung.

Die Modelle bilden die fachliche Grundlage der Anwendung:
- User speichert Kontodaten, Passwort-Hash und API-Token.
- TimeEntry speichert einzelne Zeiteintraege eines Benutzers.

Die Methoden in den Klassen kapseln wiederkehrende Logik direkt dort,
wo die Daten definiert sind. Dadurch bleibt der restliche Code uebersichtlich.
"""

import secrets
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager


class User(UserMixin, db.Model):
    """Modell fuer Benutzerkonten.

    UserMixin liefert Standardfunktionen fuer Flask-Login, damit Benutzer
    in einer Session angemeldet bleiben koennen. Das Passwort wird nicht im
    Klartext gespeichert, sondern nur als sicherer Hashwert.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    api_token = db.Column(db.String(64), unique=True, index=True)

    # Ein Benutzer kann mehrere Zeiteintraege besitzen.
    # "delete-orphan" sorgt dafuer, dass untergeordnete Eintraege sauber
    # entfernt werden, falls der Benutzer geloescht wird.
    time_entries = db.relationship(
        'TimeEntry',
        backref='user',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        """Erzeugt aus dem uebergebenen Passwort einen Hashwert."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vergleicht ein eingegebenes Passwort mit dem gespeicherten Hash."""
        return check_password_hash(self.password_hash, password)

    def generate_api_token(self):
        """Erstellt einen neuen zufaelligen API-Token fuer externe Zugriffe."""
        self.api_token = secrets.token_hex(32)
        return self.api_token

    def __repr__(self):
        return f'<User {self.username}>'


class TimeEntry(db.Model):
    """Modell fuer einzelne Zeiteintraege.

    Ein Eintrag startet in der Regel mit dem Status "InProgress".
    Sobald der Timer gestoppt wird, werden Endzeit, Dauer und Status
    entsprechend aktualisiert.
    """
    __tablename__ = 'time_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    description = db.Column(db.String(500), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    end_time = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='InProgress')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def stop_timer(self):
        """Beendet den laufenden Timer und berechnet die Dauer in Sekunden.

        Die Methode arbeitet bewusst mit UTC-Zeit und achtet darauf,
        dass beide Zeitwerte vergleichbar sind. Das verhindert Probleme,
        falls ein Wert einmal ohne Zeitzoneninformation gespeichert wurde.
        """
        now = datetime.now(timezone.utc)
        self.end_time = now

        start = self.start_time
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)

        end = self.end_time
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)

        delta = end - start
        self.duration_seconds = max(0, int(delta.total_seconds()))
        self.status = 'Done'

    def to_dict(self):
        """Gibt den Datensatz in einem API-freundlichen Format zurueck."""
        return {
            'id': self.id,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f'<TimeEntry {self.id}: {self.description[:30]}...>'


@login_manager.user_loader
def load_user(user_id):
    """Laedt den Benutzer fuer eine bestehende Session anhand seiner ID."""
    return db.session.get(User, int(user_id))
