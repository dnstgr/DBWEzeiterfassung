# Zeiterfassung - Flask Webapplikation

Meine erste Zeiterfassungs-Webapplikation mit Flask und PostgreSQL.
Die Anwendung bietet eine Weboberflaeche im Kanban-Stil sowie eine kleine REST-API.

# Funktionen

- Kanban-Board mit zwei Spalten: "InProgress" und "Done"
- Timer-Funktion mit automatischer Dauerberechnung
- Zeiteintraege erstellen, bearbeiten und loeschen
- Rapport-Seite mit Datumsfilter und Tagessummen
- Benutzer-Authentifizierung mit Login und Registrierung
- REST-API mit Bearer-Token

# Technologie-Stack

- Python 3.9+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Login
- PostgreSQL
- Gunicorn

# Rtart im Entwicklungsmodus

```bash
python run.py
```

Danach ist die Anwendung standardmaessig unter `http://localhost:5000` erreichbar.

## Produktion mit Gunicorn

```bash
gunicorn wsgi:app --bind 0.0.0.0:20201 --workers 3
```
