# Forchheim Sensordaten für Home Assistant

Diese HACS-kompatible Custom Integration bindet die öffentlich sichtbaren
Wetterstationen des [Digitalen Zwillings der Stadt Forchheim](https://dz.forchheim.de/)
in Home Assistant ein.

## Funktionen

- Einrichtung vollständig über **Einstellungen → Geräte & Dienste**
- automatische Liste der verfügbaren Forchheimer Wetterstationen
- Sortierung nach Entfernung zum in Home Assistant eingestellten Zuhause
- eine gemeinsame, sparsame Abfrage für alle Sensoren
- konfigurierbares Aktualisierungsintervall von 60 bis 3600 Sekunden
- Wiederherstellung nach vorübergehenden Verbindungsfehlern
- Diagnoseinformationen über die Home-Assistant-Oberfläche

Die Integration stellt folgende Sensoren bereit:

| Sensor | Einheit |
|---|---:|
| Temperatur | °C |
| relative Luftfeuchtigkeit | % |
| Luftdruck | hPa |
| Windgeschwindigkeit | m/s |
| Windrichtung | ° |
| Taupunkt | °C |
| Niederschlag pro Stunde | mm/h |

## Installation mit HACS

1. Öffne HACS und wähle **Integrationen → Drei-Punkte-Menü → Benutzerdefinierte Repositorys**.
2. Trage `Breit88/forchheim-sensors` ein und wähle die Kategorie **Integration**.
3. Öffne danach **Forchheim Sensordaten** in HACS.
4. Installiere **Forchheim Sensordaten** und starte Home Assistant neu.
5. Öffne **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
6. Suche nach **Forchheim Sensordaten** und wähle eine Wetterstation.

Für eine manuelle Installation kopierst du
`custom_components/forchheim_sensors` nach
`/config/custom_components/forchheim_sensors` und startest Home Assistant neu.

## Datenaktualisierung

Standardmäßig werden die Werte alle fünf Minuten aktualisiert. Alle Entitäten
einer Station teilen sich dieselbe Abfrage. Das Intervall kann in den Optionen
der Integration geändert werden.

## Datenquelle und Grenzen

Die Messdaten stammen von der Stadt Forchheim und Smart Data Services. Die
Integration verwendet die öffentlich erreichbaren Endpunkte, die auch die Karte
und das öffentliche Wetter-Dashboard versorgen. Die Integration ist nicht mit
der Stadt Forchheim oder Smart Data Services verbunden. Änderungen an diesen
öffentlichen Endpunkten können ein Update der Integration erforderlich machen.

## Entfernen

Entferne zuerst den Eintrag unter **Einstellungen → Geräte & Dienste**. Danach
kann die Integration in HACS deinstalliert und Home Assistant neu gestartet
werden.
