"""Blueprint fuer Anmeldung, Registrierung und Abmeldung.

Die HTML-Oberflaeche verwendet eine klassische Session-Anmeldung mit
Flask-Login. Nach erfolgreichem Login merkt sich Flask die Sitzung des
Benutzers ueber Cookies, sodass geschuetzte Seiten aufgerufen werden koennen.
"""

from urllib.parse import urlsplit
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

# Eigener Blueprint fuer alle Authentifizierungsrouten.
auth_bp = Blueprint('auth', __name__)


def is_safe_redirect_url(target):
    """Prueft, ob eine Weiterleitungs-URL innerhalb der eigenen Anwendung bleibt.

    Damit wird verhindert, dass ein manipulierter "next"-Parameter den Benutzer
    nach dem Login auf eine fremde externe Seite umleitet.
    """
    if not target:
        return False

    target_parts = urlsplit(target)
    return target_parts.scheme == '' and target_parts.netloc == ''


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Zeigt das Login-Formular an und verarbeitet die Anmeldung."""
    if current_user.is_authenticated:
        return redirect(url_for('main.kanban'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash('Ungültiger Benutzername oder Passwort.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user)
        flash(f'Willkommen, {user.username}!', 'success')

        next_page = request.args.get('next')
        if is_safe_redirect_url(next_page):
            return redirect(next_page)

        return redirect(url_for('main.kanban'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Meldet den aktuellen Benutzer sauber aus der Session ab."""
    logout_user()
    flash('Du wurdest erfolgreich abgemeldet.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Zeigt das Registrierungsformular an und legt neue Benutzer an."""
    if current_user.is_authenticated:
        return redirect(url_for('main.kanban'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        errors = []

        if not username or len(username) < 3:
            errors.append('Benutzername muss mindestens 3 Zeichen lang sein.')
        if not email or '@' not in email:
            errors.append('Bitte eine gültige E-Mail-Adresse eingeben.')
        if not password or len(password) < 8:
            errors.append('Passwort muss mindestens 8 Zeichen lang sein.')
        if password != password_confirm:
            errors.append('Passwörter stimmen nicht überein.')

        if User.query.filter_by(username=username).first():
            errors.append('Dieser Benutzername ist bereits vergeben.')
        if User.query.filter_by(email=email).first():
            errors.append('Diese E-Mail-Adresse ist bereits registriert.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email)
        user.set_password(password)
        user.generate_api_token()

        db.session.add(user)
        db.session.commit()

        flash('Registrierung erfolgreich! Du kannst dich jetzt anmelden.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')
