# Update und Migration

## Aktualisierung über HACS

1. Öffne HACS und wähle **Digitales Forchheim**.
2. Klicke auf **Aktualisieren** beziehungsweise **Erneut herunterladen**.
3. Wähle die aktuelle Version und starte Home Assistant anschließend neu.
4. Kontrolliere unter **Einstellungen → Geräte & Dienste**, ob die Integration
   erfolgreich geladen wurde.

Die Konfiguration wird beim Start automatisch auf die aktuelle Version
migriert. Ein Löschen und erneutes Einrichten ist nicht erforderlich.

## Von Version 0.1.x

Die ursprüngliche einzelne Wetterstation wird auf die stadtweite Einrichtung
umgestellt. Vorhandene Wetter-Entitäten behalten ihre eindeutigen IDs, damit
Dashboards und Recorder-Verläufe weiter funktionieren.

## Von Version 0.2.x

Version 0.3.0 entfernt E-Ladestationen aus dem Funktionsumfang. Beim ersten
Start nach dem Update entfernt die Migration die früheren Ladestations-
Entitäten und -Geräte aus der Entity- und Device-Registry. Wetter-, Klima-,
Fahrbahn-, Verkehrs- und übrige Stadtsensoren bleiben bestehen.

## Vor einem Downgrade

Ein Downgrade wird nicht empfohlen, weil ältere Versionen die aktuelle
Konfigurationsversion möglicherweise nicht kennen. Sichere vor manuellen
Änderungen eine Home-Assistant-Sicherung. Bei Problemen sollten zuerst die
aktuelle Version erneut über HACS installiert und die Protokolle geprüft
werden.

