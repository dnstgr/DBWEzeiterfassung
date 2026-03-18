"""Development Server.

Startet die Flask-Applikation im Entwicklungsmodus.
Nur fuer lokale Entwicklung verwenden, nicht fuer Produktion!
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Debug-Modus aktivieren fuer automatisches Neuladen bei Aenderungen
    app.run(debug=True, host='0.0.0.0', port=5000)
