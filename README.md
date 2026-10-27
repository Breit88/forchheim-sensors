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

- Messwerte der bei der Einrichtung ausgewählten Forchheimer Wetterstationen
- Temperatur und Luftfeuchtigkeit ausgewählter weiterer Stadt-Sensoren
- Luft- und Oberflächentemperatur des auswählbaren Fahrbahnsensors an der Lila Brücke
- zeitabhängige Verkehrsprofile für Werktage und Wochenenden
- Anzahl von Parkmöglichkeiten, Fahrradständern und Spielplätzen
- aktive Baustellen einschließlich Zeitraum und Adresse
- Entfernung zur nächsten Bus- und Bahnhaltestelle, Baustelle und zum nächsten
  Spielplatz, ausgehend von der Home-Assistant-Position
- Zustandsklassen für alle numerischen Messwerte, damit Recorder-Verläufe und
  Langzeitstatistiken in Diagrammen zur Verfügung stehen
- schonende Abfrage der öffentlichen Dienste durch gemeinsame Messwertabrufe
  und abgestufte Zwischenspeicherung
- optionaler Abfallkalender des Landkreises Forchheim mit Kalender-Entität und
  den nächsten Terminen für Singletonne, Restmüll, Bio, Papier und Kunststoff
  (in der Quelle „Gelbe Tonne“)

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
5. Wähle die gewünschten Messstationen. Alle Sensoren einer Station werden
   gemeinsam eingebunden. Anfangs sind alle Stationen vorausgewählt. Bestätige
   das Aktualisierungsintervall (300 Sekunden, erlaubt sind 60 bis 3600) und
   aktiviere bei Bedarf die Abfalltermine.
6. Wenn du Abfalltermine aktivierst, ermittelt die Integration anhand der
   Heimposition den passenden Straßeneintrag. Ein eindeutiger Treffer wird nach
   Prüfung des ICS-Kalenders automatisch übernommen. Bei geteilten Straßen oder
   fehlendem Treffer wähle den Abfuhrabschnitt manuell aus. Der Eintrag lässt
   sich später unter **Konfigurieren** ändern.

Es sind weder ein Benutzerkonto noch ein API-Schlüssel erforderlich. Pro
Home-Assistant-Installation kann die Integration einmal eingerichtet werden.
Stationen und Abfalltermine lassen sich später unter **Konfigurieren** ändern.
Andere bestehende ICS-Kalender werden nicht automatisch verändert.

Bei bestehenden Installationen nach dem HACS-Update und Neustart unter
**Einstellungen → Geräte & Dienste → Digitales Forchheim → Konfigurieren**
**Abfalltermine einbinden** aktivieren. Für eine Monatsansicht im Dashboard die
**Kalender-Karte** mit der neuen Kalenderentität hinzufügen.
[Details](docs/waste.md)

## Verlauf und Diagramme

Home Assistant zeichnet die Zustände der ausgewählten Sensoren über den Recorder
auf. Numerische Sensoren liefern zusätzlich `state_class: measurement`, sodass
Home Assistant daraus Langzeitstatistiken erstellt. Ein Dashboard wird nicht
automatisch verändert. Für eine Anzeige, die sich der Stationsauswahl anpasst,
steht eine [dynamische Karten-Vorlage](docs/history-and-dashboards.md#dynamische-karte-nach-station)
bereit. Sie verwendet die optionale HACS-Karte Auto Entities.

Beispiele und Hinweise zur sinnvollen Gruppierung nach Einheit stehen unter
[Verlauf und Dashboards](docs/history-and-dashboards.md).

## Dokumentation

- [Entitäten und Attribute](docs/entities.md)
- [Verlauf und Dashboards](docs/history-and-dashboards.md)
- [Datenquellen und Aktualisierung](docs/data-sources.md)
- [Abfalltermine](docs/waste.md)
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
- Die automatische Straßenzuordnung hängt von der Genauigkeit der
  Heimposition ab. Prüfe den gespeicherten Abfuhrbereich nach der Einrichtung;
  bei geteilten Straßen ist eine manuelle Auswahl erforderlich.

## Datenschutz und Verantwortung

Die Integration liest öffentliche Endpunkte. Zugangsdaten werden nicht
benötigt. Für den optionalen Straßenvorschlag sendet sie die Heimkoordinaten
**einmal beim Einrichten oder erstmaligen Aktivieren der Abfalltermine** an den
[Photon-Dienst von komoot](https://github.com/komoot/photon). Dieser Dienst
liefert einen Adressvorschlag aus OpenStreetMap-Daten. Danach wird nur der
ausgewählte Forchheimer Abfuhrbereich gespeichert und dessen ICS-Kalender
regelmäßig abgerufen. Ohne aktivierte Abfalltermine bleiben die Heimkoordinaten
wie bisher lokal für Entfernungssensoren.

Die Daten stammen von der Stadt Forchheim, Smart Data Services und bei
Haltestellen vom VGN. Dieses Projekt ist kein offizielles Angebot dieser
Organisationen. Änderungen an öffentlichen Endpunkten können ein Update der
Integration erforderlich machen.

Fehler und Verbesserungsvorschläge können über
[GitHub Issues](https://github.com/Breit88/forchheim-sensors/issues) gemeldet
werden. Bitte füge bei technischen Problemen die bereinigten
Diagnoseinformationen der Integration bei.
