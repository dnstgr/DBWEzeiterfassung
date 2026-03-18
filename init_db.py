"""Datenbank-Initialisierungsskript.

Erstellt alle Tabellen und legt einen vordefinierten Testuser an.
Dieses Skript sollte einmalig beim ersten Setup ausgefuehrt werden.

Verwendung:
    python init_db.py
"""

from app import create_app, db
from app.models import User


def init_database():
    """Datenbank initialisieren und Testuser erstellen."""
    app = create_app()

    with app.app_context():
        # Alle Tabellen erstellen
        db.create_all()
        print('Datenbanktabellen erstellt.')

        # Pruefen ob Testuser bereits existiert
        testuser = User.query.filter_by(username='Testuser01').first()

        if testuser is None:
            # Testuser anlegen
            testuser = User(
                username='Testuser01',
                email='test@example.com'
            )
            testuser.set_password('TpW202600002235everglade')
            testuser.generate_api_token()

            db.session.add(testuser)
            db.session.commit()

            print(f'Testuser erstellt:')
            print(f'  Username:  Testuser01')
            print(f'  E-Mail:    test@example.com')
            print(f'  Passwort:  TpW202600002235everglade')
            print(f'  API-Token: {testuser.api_token}')
        else:
            print(f'Testuser "Testuser01" existiert bereits.')
            print(f'  API-Token: {testuser.api_token}')

        print('\nDatenbank-Initialisierung abgeschlossen.')


if __name__ == '__main__':
    init_database()
