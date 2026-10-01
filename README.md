# Digitales Forchheim für Home Assistant

[![Validate](https://github.com/Breit88/forchheim-sensors/actions/workflows/validate.yml/badge.svg)](https://github.com/Breit88/forchheim-sensors/actions/workflows/validate.yml)
[![GitHub Release](https://img.shields.io/github/v/release/Breit88/forchheim-sensors)](https://github.com/Breit88/forchheim-sensors/releases/latest)
[![License](https://img.shields.io/github/license/Breit88/forchheim-sensors)](LICENSE)

Diese benutzerdefinierte Home-Assistant-Integration bindet öffentliche Daten
des [Digitalen Zwillings der Stadt Forchheim](https://dz.forchheim.de/) ein.
Sie richtet Wetter-, Klima-, Fahrbahn-, Verkehrs- und Stadtinformationssensoren
über einen einzigen Konfigurationsdialog ein.

[![In HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Breit88&repository=forchheim-sensors&category=integration)

Nach Download und Neustart:

[![Integration hinzufügen](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=forchheim_sensors)

## Funktionen

- Messwerte aller vier vollständigen Forchheimer Wetterstationen
- Temperatur und Luftfeuchtigkeit von 16 weiteren Stadt-Sensoren
- Luft- und Oberflächentemperatur des Fahrbahnsensors an der Lila Brücke
- zeitabhängige Verkehrsprofile für Werktage und Wochenenden
- Anzahl von Parkmöglichkeiten, Fahrradständern und Spielplätzen
- aktive Baustellen einschließlich Zeitraum und Adresse
- Entfernung zur nächsten Bus- und Bahnhaltestelle, Baustelle und zum nächsten
  Spielplatz, ausgehend von der Home-Assistant-Position
- Zustandsklassen für alle numerischen Messwerte, damit Recorder-Verläufe und
  Langzeitstatistiken in Diagrammen zur Verfügung stehen
- schonende Abfrage der öffentlichen Dienste durch gemeinsame Messwertabrufe
  und abgestufte Zwischenspeicherung

E-Ladestationen gehören seit Version 0.3.0 ausdrücklich nicht mehr zum
Funktionsumfang. Beim Update werden alte Ladestations-Entitäten automatisch aus
der Integration entfernt.

## Installation über HACS

Voraussetzung ist Home Assistant 2026.9.0 oder neuer.

1. Öffne über die Schaltfläche **In HACS öffnen** dieses Repository. Alternativ
   wählst du in HACS **Benutzerdefinierte Repositories** und trägst
   `https://github.com/Breit88/forchheim-sensors` als Typ **Integration** ein.
2. Klicke in HACS auf **Herunterladen** und wähle die aktuelle Version.
3. Starte Home Assistant neu.
4. Öffne **Einstellungen → Geräte & Dienste → Integration hinzufügen** und
   suche nach **Digitales Forchheim**.
5. Bestätige das Aktualisierungsintervall. Der Standardwert beträgt 300
   Sekunden; erlaubt sind 60 bis 3600 Sekunden.

Es sind weder ein Benutzerkonto noch ein API-Schlüssel erforderlich. Pro
Home-Assistant-Installation kann die Integration einmal eingerichtet werden.

## Verlauf und Diagramme

Home Assistant zeichnet die Zustände der erzeugten Sensoren über den Recorder
auf. Numerische Sensoren liefern zusätzlich `state_class: measurement`, sodass
Home Assistant daraus Langzeitstatistiken erstellt. Ein Dashboard wird nicht
automatisch verändert; du kannst die gewünschten Entitäten mit den eingebauten
Karten **Statistikdiagramm** und **Verlaufsdiagramm** darstellen.

Beispiele und Hinweise zur sinnvollen Gruppierung nach Einheit stehen unter
[Verlauf und Dashboards](docs/history-and-dashboards.md).

## Dokumentation

- [Entitäten und Attribute](docs/entities.md)
- [Verlauf und Dashboards](docs/history-and-dashboards.md)
- [Datenquellen und Aktualisierung](docs/data-sources.md)
- [Update und Migration](docs/migration.md)
- [Fehlerbehebung und Diagnose](docs/troubleshooting.md)
- [Entwicklung und Tests](docs/development.md)
- [Änderungsverlauf](CHANGELOG.md)

## Bekannte Einschränkungen

- Die Floating-Car-Verkehrsdaten sind historische Profile passend zu Tagesart
  und Tageszeit. Sie bilden keine sekundengenauen Live-Staumeldungen ab.
- Die Raumbelegung des Rathaussaals wird auf der Stadtkarte angeboten, der
  separate Quelldienst ist derzeit jedoch nicht zuverlässig öffentlich
  erreichbar. Die Diagnose meldet ihn deshalb als vorübergehend nicht
  verfügbar.
- Einzelne Stationen können zeitweise keine aktuellen Messwerte liefern. Die
  Integration behält dann den letzten erfolgreichen Datenstand, soweit dieser
  bereits verfügbar ist.

## Datenschutz und Verantwortung

Die Integration liest ausschließlich öffentliche Endpunkte. Zugangsdaten
werden nicht benötigt. Die in Home Assistant hinterlegte Heimposition wird nur
lokal verwendet, um Entfernungen zu berechnen, und nicht an die Datenquellen
übermittelt.

Die Daten stammen von der Stadt Forchheim, Smart Data Services und bei
Haltestellen vom VGN. Dieses Projekt ist kein offizielles Angebot dieser
Organisationen. Änderungen an öffentlichen Endpunkten können ein Update der
Integration erforderlich machen.

Fehler und Verbesserungsvorschläge können über
[GitHub Issues](https://github.com/Breit88/forchheim-sensors/issues) gemeldet
werden. Bitte füge bei technischen Problemen die bereinigten
Diagnoseinformationen der Integration bei.
