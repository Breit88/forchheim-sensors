# Fehlerbehebung und Diagnose

## Die Integration erscheint nach dem HACS-Download nicht

Prüfe, ob HACS das Repository als Typ **Integration** hinzugefügt hat und ob
das Verzeichnis `custom_components/forchheim_sensors` vorhanden ist. Starte
Home Assistant nach dem Download vollständig neu. Die Mindestversion ist Home
Assistant 2026.9.0.

## Die Einrichtung schlägt fehl

Während der Einrichtung prüft die Integration das Stationsverzeichnis und die
aktuellen Messwerte. Beide öffentlichen Dienste müssen von Home Assistant aus
über HTTPS erreichbar sein. Prüfe DNS, Internetzugang, Systemzeit und das
Home-Assistant-Protokoll. Ein Benutzerkonto oder API-Schlüssel ist nicht nötig.

## Einzelne Entitäten sind `unavailable`

Eine öffentliche Messstelle kann zeitweise keine aktuellen Werte liefern. Das
betrifft nicht zwingend die übrigen Stationen. Warte die nächste Aktualisierung
ab und prüfe anschließend den Zeitstempel der Messung in den Attributen.

## Änderungen erscheinen nicht sofort

Messwerte werden im eingestellten Intervall von 60 bis 3600 Sekunden
aktualisiert. Stationslisten, Orte, Haltestellen und Verkehrsprofile werden bis
zu sechs Stunden gecacht; Baustellen bis zu 15 Minuten.

## Diagramme bleiben leer

Prüfe, ob die gewählte Entität einen numerischen Wert liefert und nicht in der
`recorder`-Konfiguration ausgeschlossen ist. Neue Langzeitstatistiken benötigen
etwas Zeit. Ausführliche Hinweise und Kartenbeispiele stehen unter
[Verlauf und Dashboards](history-and-dashboards.md).

## Die Verkehrswerte wirken nicht live

Das ist erwartetes Verhalten. Die Quelle stellt historische Profile für
Tagesart und Zeitfenster bereit. Die Integration wählt das passende Profil,
liefert aber keine sekundengenauen Staumeldungen.

## Ladestationen fehlen

E-Ladestationen wurden mit Version 0.3.0 auf Wunsch aus der Integration
entfernt. Dies ist kein Ladefehler.

## Diagnose herunterladen

1. Öffne **Einstellungen → Geräte & Dienste**.
2. Wähle bei **Digitales Forchheim** das Drei-Punkte-Menü.
3. Klicke auf **Diagnose herunterladen**.

Die Diagnose enthält Konfiguration, Aktualisierungsstatus, erkannte Stationen,
Anzahlen der geladenen Datensätze, das aktive Verkehrsprofil und zeitweise
nicht verfügbare Quellen. Zugangsdaten sind nicht enthalten, weil die
Integration keine verwendet. Prüfe die Datei trotzdem vor einer öffentlichen
Veröffentlichung.

Wenn das Problem danach weiter besteht, öffne ein
[GitHub Issue](https://github.com/Breit88/forchheim-sensors/issues) mit:

- Home-Assistant-Version
- Version der Integration
- Zeitpunkt des Fehlers
- relevantem Protokollausschnitt
- bereinigter Diagnosedatei

