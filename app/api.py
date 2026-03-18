"""REST-API fuer Zeiteintraege.

Die API verwendet Bearer-Token im Authorization-Header.
Damit koennen Zeiteintraege auch von externen Tools oder spaeteren
Erweiterungen aus angesprochen werden, ohne die normale Weboberflaeche zu nutzen.
"""

from functools import wraps
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from app import db
from app.models import User, TimeEntry

api_bp = Blueprint('api', __name__)


def parse_iso_datetime(value):
    """Parst einen ISO-Zeitwert und normalisiert ihn nach UTC.

    Akzeptiert sowohl Werte mit Zeitzone als auch naive Zeitwerte.
    Naive Werte werden als UTC behandelt, damit die Anwendung konsistent bleibt.
    """
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def token_required(f):
    """Decorator fuer Bearer-Token-Authentifizierung.

    Wenn der Header fehlt oder der Token nicht zu einem Benutzer passt,
    wird die Anfrage direkt mit HTTP 401 abgewiesen.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization', '')

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()

        if not token:
            return jsonify({'error': 'Token fehlt. Bitte Authorization-Header setzen.'}), 401

        user = User.query.filter_by(api_token=token).first()
        if not user:
            return jsonify({'error': 'Ungültiger Token.'}), 401

        return f(user, *args, **kwargs)

    return decorated


@api_bp.route('/login', methods=['POST'])
def api_login():
    """Prueft Benutzername und Passwort und liefert den API-Token zurueck."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON-Body erwartet.'}), 400

    username = data.get('username', '')
    password = data.get('password', '')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Ungültiger Benutzername oder Passwort.'}), 401

    if not user.api_token:
        user.generate_api_token()
        db.session.commit()

    return jsonify({
        'message': 'Login erfolgreich.',
        'token': user.api_token,
        'username': user.username
    })


@api_bp.route('/timeentries', methods=['GET'])
@token_required
def get_timeentries(user):
    """Liefert alle Zeiteintraege des authentifizierten Benutzers."""
    entries = TimeEntry.query.filter_by(user_id=user.id)         .order_by(TimeEntry.start_time.desc()).all()

    return jsonify({
        'timeentries': [entry.to_dict() for entry in entries],
        'count': len(entries)
    })


@api_bp.route('/timeentries', methods=['POST'])
@token_required
def create_timeentry(user):
    """Erstellt einen neuen Zeiteintrag ueber die API."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON-Body erwartet.'}), 400

    description = data.get('description', '').strip()
    if not description:
        return jsonify({'error': 'Beschreibung ist erforderlich.'}), 400

    start_time_str = data.get('start_time')
    if start_time_str:
        try:
            start_time = parse_iso_datetime(start_time_str)
        except ValueError:
            return jsonify({'error': 'Ungültiges Datumsformat für start_time (ISO-Format erwartet).'}), 400
    else:
        start_time = datetime.now(timezone.utc)

    entry = TimeEntry(
        user_id=user.id,
        description=description,
        start_time=start_time,
        status='InProgress'
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({
        'message': 'Zeiteintrag erstellt.',
        'timeentry': entry.to_dict()
    }), 201


@api_bp.route('/timeentries/<int:entry_id>', methods=['PUT'])
@token_required
def update_timeentry(user, entry_id):
    """Aktualisiert Beschreibung oder Status eines bestehenden Eintrags."""
    entry = db.session.get(TimeEntry, entry_id)
    if entry is None:
        return jsonify({'error': 'Eintrag nicht gefunden.'}), 404

    if entry.user_id != user.id:
        return jsonify({'error': 'Zugriff verweigert.'}), 403

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'JSON-Body erwartet.'}), 400

    if 'description' in data:
        description = str(data['description']).strip()
        if not description:
            return jsonify({'error': 'Beschreibung darf nicht leer sein.'}), 400
        entry.description = description

    if data.get('status') == 'Done' and entry.status == 'InProgress':
        entry.stop_timer()

    db.session.commit()

    return jsonify({
        'message': 'Zeiteintrag aktualisiert.',
        'timeentry': entry.to_dict()
    })


@api_bp.route('/timeentries/<int:entry_id>', methods=['DELETE'])
@token_required
def delete_timeentry(user, entry_id):
    """Loescht einen Zeiteintrag des authentifizierten Benutzers."""
    entry = db.session.get(TimeEntry, entry_id)
    if entry is None:
        return jsonify({'error': 'Eintrag nicht gefunden.'}), 404

    if entry.user_id != user.id:
        return jsonify({'error': 'Zugriff verweigert.'}), 403

    db.session.delete(entry)
    db.session.commit()

    return jsonify({'message': 'Zeiteintrag gelöscht.'})
