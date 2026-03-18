"""Zentrale Erstellung und Grundkonfiguration der Flask-Anwendung.

In dieser Datei werden die wichtigsten Flask-Erweiterungen einmal zentral
vorbereitet und spaeter mit der konkreten App-Instanz verbunden.
Das entspricht dem Application-Factory-Muster. Der Vorteil davon ist,
dass die Anwendung sauber aufgebaut ist und spaeter einfacher getestet,
erweitert oder in verschiedenen Umgebungen gestartet werden kann.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Die Erweiterungen werden hier zuerst ohne konkrete App-Instanz erstellt.
# So koennen sie spaeter innerhalb der Factory mit jeder neuen App verbunden werden.
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Falls ein nicht angemeldeter Benutzer eine geschuetzte Seite aufruft,
# leitet Flask-Login automatisch auf diese Route weiter.
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Bitte melde dich an, um diese Seite zu sehen.'


def create_app(config_class=Config):
    """Erstellt eine neue Flask-App und registriert alle Bestandteile.

    Args:
        config_class: Konfigurationsklasse mit den benoetigten Einstellungen
            wie Secret Key und Datenbankverbindung.

    Returns:
        Flask: Vollstaendig konfigurierte Flask-Anwendung.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Erweiterungen an die konkrete App binden.
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Blueprints importieren und registrieren.
    # Die Imports stehen absichtlich hier, damit es keine zirkulaeren
    # Importprobleme zwischen App, Modellen und Blueprints gibt.
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    from app.main import main_bp
    app.register_blueprint(main_bp)

    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
