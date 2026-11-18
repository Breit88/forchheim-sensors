# Entitäten und Attribute

Die Integration legt ausgewählte Messstellen als Home-Assistant-Geräte an. Die
Entitätsnamen werden aus Stationsname und Messgröße gebildet; Home Assistant
erzeugt daraus die jeweilige `entity_id`. Deshalb können die IDs je nach
Sprache und bereits vorhandenen Entitäten leicht abweichen.

Stationen werden als Einheit ausgewählt: Alle ihre Messsensoren werden gemeinsam
eingebunden. Eine abgewählte Station wird nicht abgefragt und ihre Entitäten
werden deaktiviert. Bei Wiederwahl behalten sie ihre registrierten IDs.

## Messstellen

| Bereich | Umfang | Typische Sensoren |
| --- | ---: | --- |
| Wetterstationen | 4 Stationen | Temperatur, Luftfeuchtigkeit, Luftdruck, Windgeschwindigkeit, Windrichtung, Taupunkt, Niederschlag |
| Temperatur-/Feuchtestationen | 16 Stationen | Temperatur, Luftfeuchtigkeit, Taupunkt; Batterie ist standardmäßig deaktiviert |
| Fahrbahnsensor | 1 Station | Lufttemperatur, Fahrbahnoberflächentemperatur; Batteriespannung ist standardmäßig deaktiviert |

Jede Messwert-Entität enthält, soweit die Quelle die Angaben liefert, folgende
Attribute:

- Zeitpunkt der Messung
- Stationsname und Stationstyp
- Breiten- und Längengrad

Über den Link **Besuchen** auf der Geräteseite gelangst du zum passenden
öffentlichen Dashboard der Datenquelle.

## Einheiten und Geräteklassen

| Messgröße | Einheit | Home-Assistant-Geräteklasse |
| --- | --- | --- |
| Temperatur, Taupunkt, Fahrbahnoberfläche | °C | `temperature` |
| Luftfeuchtigkeit | % | `humidity` |
| Luftdruck | hPa | `atmospheric_pressure` |
| Windgeschwindigkeit | m/s | `wind_speed` |
| Windrichtung | ° | keine |
| Niederschlag pro Stunde | mm/h | `precipitation_intensity` |
| Batterie | % | `battery` |
| Batteriespannung | V | `voltage` |

Alle numerischen Sensoren verwenden die Zustandsklasse `measurement`. Damit
kann Home Assistant ihre Zustände aufzeichnen und Langzeitstatistiken bilden.

## Stadtinformationen

Zusätzlich gibt es zusammenfassende Sensoren für:

- Zahl der Wetterstationen
- Zahl der Temperatur-/Feuchtestationen
- Zahl der Parkmöglichkeiten
- Zahl der Fahrradständer
- Zahl der Spielplätze
- Zahl der Bushaltestellen
- Zahl der aktiven Baustellen
- durchschnittliche Geschwindigkeit des aktuellen Verkehrsprofils in km/h
- Zahl der Beobachtungen im aktuellen Verkehrsprofil
- Entfernung zur nächsten Bushaltestelle in km
- Entfernung zur nächsten Bahnstation in km
- Entfernung zum nächsten Spielplatz in km
- Entfernung zur nächsten aktiven Baustelle in km

Die stadtweiten Zählwerte bleiben unabhängig von der Stationsauswahl. Für
Bushaltestellen, Spielplätze und Baustellen zählen sie alle Orte innerhalb der
Stadtgrenze Forchheims, unabhängig von deiner Home-Assistant-Position.

Die Entfernungssensoren enthalten zusätzliche Attribute wie Name, Adresse,
Koordinaten und bei Haltestellen die verfügbaren Linien. Die Zählsensoren für
Bushaltestellen und Spielplätze enthalten vollständige Namenslisten; der
Baustellen-Zählsensor enthält die Details aller aktiven Baustellen.

Zusätzlich legt die Integration für jede Bushaltestelle, jeden Spielplatz, jede
aktive Baustelle und jede Wetterstation mit Koordinaten eine
`geo_location`-Entität an. Sie sind
auf der Home-Assistant-Karte oder einer Karten-Karte sichtbar. Ihre Quellen
heißen `forchheim_sensors_bus`, `forchheim_sensors_playground` und
`forchheim_sensors_construction` sowie `forchheim_sensors_weather`.
Baustellen, Spielplätze und Wetterstationen verwenden die bereitgestellten
Bildsymbole. Wenn ein Ort aus der öffentlichen Quelle
verschwindet, entfernt die Integration seinen Kartenpunkt. Die bestehenden
Entfernungssensoren zeigen weiterhin den jeweils nächstgelegenen Ort.

Für eine eigene Karten-Karte können die vier Quellen direkt ausgewählt werden:

```yaml
type: map
geo_location_sources:
  - forchheim_sensors_bus
  - forchheim_sensors_playground
  - forchheim_sensors_construction
  - forchheim_sensors_weather
```

Bei den drei Bildquellen die Standard-Beschriftung beibehalten; die
Karten-Karte verwendet dann das jeweilige Bildsymbol.

## Abfalltermine

Für jeden ausgewählten Abfuhrbereich gibt es ein eigenes Gerät mit fünf
Datumssensoren für die jeweils nächste Singletonne,
Restmülltonne, Biotonne, Papiertonne und Gelbe Tonne (Kunststoffsammlung).
Zwei Diagnose-Sensoren zeigen den Abrufstatus und den Zeitpunkt des letzten
erfolgreichen Abrufs. Die Abfuhrbereiche können unter **Konfigurieren** geändert
werden. Der Kalender bleibt als eigenständige Kalenderentität für Karten und
Automationen verfügbar. Sein Ja/Nein-Zustand wird nicht auf der Geräteseite
angezeigt. Siehe [Abfalltermine](waste.md).

Die fünf Abholtermin-Sensoren verwenden Tonnenbilder in Schwarz (Restmüll und
Singletonne), Gelb (Kunststoff), Blau (Papier) und Grün (Bio). Die Bilder
werden von Home Assistant lokal bereitgestellt.

## Bewusst nicht enthalten

E-Ladestationen werden seit Version 0.3.0 weder geladen noch als Entitäten
angelegt. Bei einem Update von 0.2.x entfernt die Migration die alten
Ladestations-Entitäten und -Geräte automatisch.

