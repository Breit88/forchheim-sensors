# Datenquellen und Aktualisierung

Die Integration fasst mehrere öffentlich erreichbare Angebote zusammen. Sie
benötigt keine Zugangsdaten.

| Daten | Öffentliche Quelle | Verwendung |
| --- | --- | --- |
| Stationsverzeichnis und Messwerte | [SensorThings-Endpunkt des Digitalen Zwillings](https://dz.forchheim.de/datasource-data/sensorthings/Locations/) und [SDS-Dashboard-API](https://dashboard-public.sds.community/) | Wetter-, Klima- und Fahrbahnsensoren |
| Orte | [Ortsinformationen der Stadt](https://dz.forchheim.de/datasource-data/ortsinfo/ortsinfo.json) | Parkmöglichkeiten und Fahrradständer |
| Spielplätze | Digitaler Zwilling Forchheim | Anzahl und nächste Entfernung |
| Baustellen | [Geoportal Forchheim](https://geodb.forchheim.de/Api/Baustellen/GeoJson/) | aktive Baustellen und nächste Entfernung |
| Haltestellen | öffentlicher VGN-Datensatz über den Digitalen Zwilling | nächste Bus- und Bahnstation |
| Verkehrsprofile | Floating-Car-Data des Digitalen Zwillings | Durchschnittsgeschwindigkeit und Beobachtungszahl |

## Aktualisierungsrhythmus

| Datenart | Aktualisierung beziehungsweise Cache |
| --- | ---: |
| aktuelle Stationsmesswerte | konfiguriertes Intervall, standardmäßig 300 Sekunden |
| Stationsverzeichnis | 6 Stunden |
| Orte, Spielplätze und Haltestellen | 6 Stunden |
| Verkehrsprofile | 6 Stunden je Profil |
| Baustellen | 15 Minuten |

Das Messintervall kann in den Optionen der Integration auf 60 bis 3600
Sekunden eingestellt werden. Die längeren Caches entlasten die öffentlichen
Server; eine kürzere Einstellung des Messintervalls verkürzt diese Caches
nicht.

## Bedeutung der Verkehrsdaten

Die Verkehrsdaten sind vorab aggregierte Floating-Car-Profile. Die Integration
wählt anhand des aktuellen Zeitpunkts automatisch das passende Profil aus:

- Werktag oder Wochenende
- 00:00–06:00 Uhr
- 06:00–10:00 Uhr
- 10:00–15:00 Uhr
- 15:00–19:00 Uhr
- 19:00–24:00 Uhr

Die Werte eignen sich zum Vergleich typischer Verkehrslagen, sind aber keine
Live-Stau- oder Fahrzeugdaten.

## Verhalten bei Ausfällen

Die aktuellen Stationsmesswerte sind die zentrale Datenquelle. Schlägt ihre
Abfrage fehl, meldet Home Assistant die Aktualisierung als fehlgeschlagen.
Fallen optionale Quellen wie Orte, Baustellen oder Verkehr zeitweise aus,
bleiben vorhandene Werte erhalten. Der Fehler erscheint in den
Diagnoseinformationen, damit ein Ausfall der Quelle von einem Fehler der
Integration unterschieden werden kann.

Die Heimkoordinaten aus Home Assistant werden ausschließlich lokal für die
Entfernungssensoren verwendet und nicht an diese Quellen gesendet.

