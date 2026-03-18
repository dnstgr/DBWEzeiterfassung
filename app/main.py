"""Blueprint fuer die normalen Webseiten der Anwendung.

Hier liegen die Routen fuer das Kanban-Board und den Rapport.
Alle fachlichen Aktionen wie Erstellen, Stoppen, Bearbeiten und Loeschen
von Zeiteintraegen werden serverseitig verarbeitet.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
from app import db
from app.models import TimeEntry

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Leitet je nach Login-Status auf die passende Startseite weiter."""
    if current_user.is_authenticated:
        return redirect(url_for('main.kanban'))
    return redirect(url_for('auth.login'))


@main_bp.route('/kanban')
@login_required
def kanban():
    """Zeigt alle Eintraege des aktuellen Benutzers im Kanban-Layout an."""
    entries = TimeEntry.query.filter_by(user_id=current_user.id)         .order_by(TimeEntry.start_time.desc()).all()

    in_progress = [entry for entry in entries if entry.status == 'InProgress']
    done = [entry for entry in entries if entry.status == 'Done']

    return render_template('kanban.html', in_progress=in_progress, done=done)


@main_bp.route('/kanban/create', methods=['POST'])
@login_required
def create_entry():
    """Erstellt einen neuen Zeiteintrag und startet den Timer sofort."""
    description = request.form.get('description', '').strip()

    if not description:
        flash('Bitte eine Beschreibung eingeben.', 'error')
        return redirect(url_for('main.kanban'))

    entry = TimeEntry(
        user_id=current_user.id,
        description=description,
        start_time=datetime.now(timezone.utc),
        status='InProgress'
    )
    db.session.add(entry)
    db.session.commit()

    flash('Zeiteintrag erstellt und Timer gestartet.', 'success')
    return redirect(url_for('main.kanban'))


@main_bp.route('/kanban/stop/<int:entry_id>', methods=['POST'])
@login_required
def stop_entry(entry_id):
    """Stoppt einen laufenden Eintrag des aktuell angemeldeten Benutzers."""
    entry = db.session.get(TimeEntry, entry_id)
    if entry is None:
        flash('Eintrag wurde nicht gefunden.', 'error')
        return redirect(url_for('main.kanban'))

    if entry.user_id != current_user.id:
        flash('Zugriff verweigert.', 'error')
        return redirect(url_for('main.kanban'))

    if entry.status == 'Done':
        flash('Dieser Timer wurde bereits gestoppt.', 'error')
        return redirect(url_for('main.kanban'))

    entry.stop_timer()
    db.session.commit()

    flash('Timer gestoppt.', 'success')
    return redirect(url_for('main.kanban'))


@main_bp.route('/kanban/edit/<int:entry_id>', methods=['POST'])
@login_required
def edit_entry(entry_id):
    """Aktualisiert die Beschreibung eines vorhandenen Zeiteintrags."""
    entry = db.session.get(TimeEntry, entry_id)
    if entry is None:
        flash('Eintrag wurde nicht gefunden.', 'error')
        return redirect(url_for('main.kanban'))

    if entry.user_id != current_user.id:
        flash('Zugriff verweigert.', 'error')
        return redirect(url_for('main.kanban'))

    description = request.form.get('description', '').strip()
    if not description:
        flash('Beschreibung darf nicht leer sein.', 'error')
        return redirect(url_for('main.kanban'))

    entry.description = description
    db.session.commit()

    flash('Eintrag aktualisiert.', 'success')
    return redirect(url_for('main.kanban'))


@main_bp.route('/kanban/delete/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    """Loescht einen Zeiteintrag, sofern er dem aktuellen Benutzer gehoert."""
    entry = db.session.get(TimeEntry, entry_id)
    if entry is None:
        flash('Eintrag wurde nicht gefunden.', 'error')
        return redirect(url_for('main.kanban'))

    if entry.user_id != current_user.id:
        flash('Zugriff verweigert.', 'error')
        return redirect(url_for('main.kanban'))

    db.session.delete(entry)
    db.session.commit()

    flash('Eintrag gelöscht.', 'success')
    return redirect(url_for('main.kanban'))


@main_bp.route('/rapport')
@login_required
def rapport():
    """Zeigt abgeschlossene Eintraege eines Datumsbereichs als Rapport an."""
    today = datetime.now(timezone.utc).date()
    date_from_str = request.args.get('date_from', '')
    date_to_str = request.args.get('date_to', '')

    try:
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d').date() if date_from_str else today - timedelta(days=6)
    except ValueError:
        date_from = today - timedelta(days=6)

    try:
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d').date() if date_to_str else today
    except ValueError:
        date_to = today

    # Falls der Benutzer die Werte vertauscht hat, werden sie automatisch korrigiert.
    if date_from > date_to:
        date_from, date_to = date_to, date_from

    start_dt = datetime.combine(date_from, datetime.min.time()).replace(tzinfo=timezone.utc)
    end_dt = datetime.combine(date_to + timedelta(days=1), datetime.min.time()).replace(tzinfo=timezone.utc)

    entries = TimeEntry.query.filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.status == 'Done',
        TimeEntry.start_time >= start_dt,
        TimeEntry.start_time < end_dt
    ).order_by(TimeEntry.start_time.desc()).all()

    days = {}
    for entry in entries:
        day_key = entry.start_time.date().isoformat()
        if day_key not in days:
            days[day_key] = {'entries': [], 'total_seconds': 0}

        days[day_key]['entries'].append(entry)
        if entry.duration_seconds:
            days[day_key]['total_seconds'] += entry.duration_seconds

    sorted_days = dict(sorted(days.items(), reverse=True))

    return render_template(
        'rapport.html',
        days=sorted_days,
        date_from=date_from.isoformat(),
        date_to=date_to.isoformat()
    )
