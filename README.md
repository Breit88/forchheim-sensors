# Digitales Forchheim für Home Assistant

Diese HACS-Integration bindet die öffentlich verfügbaren Daten des
[Digitalen Zwillings der Stadt Forchheim](https://dz.forchheim.de/) in Home
Assistant ein. Ein gemeinsamer Coordinator fragt Live-Daten sparsam ab; große
GeoJSON-Datensätze werden mehrere Stunden zwischengespeichert.

[![In HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Breit88&repository=forchheim-sensors&category=integration)

Nach der Installation und einem Neustart:

[![Integration hinzufügen](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=forchheim_sensors)

## Enthaltene Daten

- alle 4 vollständigen Forchheimer Wetterstationen
- alle 16 öffentlichen Temperatur- und Feuchtesensoren
- Fahrbahnsensor Lila Brücke mit Luft- und Oberflächentemperatur
- Verkehrsprofile passend zu Werktag/Wochenende und aktueller Tageszeit mit
  Durchschnittsgeschwindigkeit und Zahl der Messungen
- aktive Baustellen mit Zeitraum und Adresse
- Anzahl der Parkmöglichkeiten, Fahrradständer und Spielplätze
- Entfernung und Details zur nächsten Bushaltestelle, Bahnstation, Baustelle
  und zum nächsten Spielplatz

Die Raumbelegung des Rathaussaals wird auf der Stadtkarte angeboten, der dafür
verwendete separate Server ist derzeit öffentlich nicht erreichbar. Die Quelle
wird in den Diagnoseinformationen ausgewiesen und kann ergänzt werden, sobald
sie wieder zuverlässig antwortet.

## Installation

1. Klicke auf **In HACS öffnen** oder füge `Breit88/forchheim-sensors` als
   benutzerdefiniertes HACS-Repository vom Typ **Integration** hinzu.
2. Klicke in HACS auf **Herunterladen**.
3. Starte Home Assistant neu.
4. Klicke auf **Integration hinzufügen** und bestätige das
   Aktualisierungsintervall. Alle Datenquellen werden automatisch eingerichtet.

Eine bestehende Version 0.1.x wird automatisch auf die stadtweite Einrichtung
migriert. Vorhandene Wetter-Entitäten behalten ihre eindeutigen IDs.

## Datenaktualisierung

Live-Messwerte werden standardmäßig alle fünf Minuten in einer gemeinsamen
Abfrage aktualisiert. Das Intervall ist zwischen 60 und 3600 Sekunden
konfigurierbar. Orts-, Haltestellen- und Verkehrsdateien werden intern gecacht,
um die öffentlichen Server nicht unnötig zu belasten.

Alle numerischen Wetter-, Klima-, Fahrbahn- und Verkehrswerte besitzen eine
Home-Assistant-Zustandsklasse. Der Recorder zeichnet ihre Zustände auf und
Home Assistant erzeugt Langzeitstatistiken, sodass die Werte direkt in
Verlaufs- und Statistikdiagrammen verwendet werden können.

Die Floating-Car-Verkehrsdaten sind zeitabhängige Verkehrsprofile der Stadt und
keine sekundengenauen Live-Staumeldungen.

## Datenquelle

Die Daten stammen von der Stadt Forchheim, Smart Data Services und bei den
Haltestellen vom VGN. Diese Integration ist kein offizielles Angebot dieser
Organisationen. Änderungen an öffentlichen Endpunkten können ein Update der
Integration erforderlich machen.
