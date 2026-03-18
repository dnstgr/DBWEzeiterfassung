/**
 * JavaScript-Funktionen fuer die Timer-Anzeige im Kanban-Board.
 *
 * Die eigentliche Zeitmessung passiert serverseitig ueber Start- und Endzeit.
 * Dieses Skript sorgt nur dafuer, dass laufende Karten im Browser jede Sekunde
 * eine sichtbar aktualisierte Dauer anzeigen, damit die Oberflaeche lebendig wirkt.
 */

/**
 * Blendet das Bearbeitungsformular eines Eintrags ein oder aus.
 *
 * @param {number} entryId - Die Datenbank-ID des Zeiteintrags.
 */
function toggleEdit(entryId) {
    const editForm = document.getElementById('edit-' + entryId);
    if (!editForm) {
        return;
    }

    editForm.style.display = editForm.style.display === 'none' ? 'block' : 'none';
}

/**
 * Formatiert eine Sekundenanzahl im Format HH:MM:SS.
 *
 * @param {number} totalSeconds - Anzahl Sekunden seit Timerstart.
 * @returns {string} Lesbare Darstellung der Dauer.
 */
function formatDuration(totalSeconds) {
    const safeSeconds = Math.max(0, Math.floor(totalSeconds));
    const hours = Math.floor(safeSeconds / 3600);
    const minutes = Math.floor((safeSeconds % 3600) / 60);
    const seconds = safeSeconds % 60;

    return (
        String(hours).padStart(2, '0') + ':' +
        String(minutes).padStart(2, '0') + ':' +
        String(seconds).padStart(2, '0')
    );
}

/**
 * Liest einen Zeitwert aus dem HTML und erstellt daraus ein Date-Objekt.
 * Falls der Wert ungueltig ist, wird null zurueckgegeben.
 *
 * @param {string} value - ISO-Zeitstempel aus dem data-start Attribut.
 * @returns {Date|null}
 */
function parseStartTime(value) {
    if (!value) {
        return null;
    }

    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? null : parsed;
}

/**
 * Aktualisiert alle laufenden Timer auf der Seite.
 *
 * Gesucht werden alle Elemente mit der CSS-Klasse "card-timer" und einem
 * data-start Attribut. Aus dem gespeicherten Startzeitpunkt wird die
 * verstrichene Dauer berechnet und in der Karte angezeigt.
 */
function updateTimers() {
    const timerElements = document.querySelectorAll('.card-timer[data-start]');

    timerElements.forEach(function(element) {
        const startTime = parseStartTime(element.getAttribute('data-start'));
        if (!startTime) {
            element.textContent = '--:--:--';
            return;
        }

        const now = new Date();
        const elapsedSeconds = Math.floor((now - startTime) / 1000);
        element.textContent = formatDuration(elapsedSeconds);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    updateTimers();
    setInterval(updateTimers, 1000);
});
