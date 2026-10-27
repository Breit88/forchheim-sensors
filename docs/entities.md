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
- Zahl der aktiven Baustellen
- durchschnittliche Geschwindigkeit des aktuellen Verkehrsprofils in km/h
- Zahl der Beobachtungen im aktuellen Verkehrsprofil
- Entfernung zur nächsten Bushaltestelle in km
- Entfernung zur nächsten Bahnstation in km
- Entfernung zum nächsten Spielplatz in km
- Entfernung zur nächsten aktiven Baustelle in km

Die stadtweiten Zählwerte bleiben unabhängig von der Stationsauswahl und
beschreiben weiterhin alle öffentlich verfügbaren Stationen.

Die Entfernungssensoren enthalten zusätzliche Attribute wie Name, Adresse,
Koordinaten und bei Haltestellen die verfügbaren Linien. Der Baustellensensor
führt außerdem Details zu bis zu 20 aktiven Baustellen als Attribute.

## Abfalltermine

Wenn Abfalltermine aktiviert wurden, gibt es ein Gerät **Abfalltermine
Forchheim** mit einem Kalender und vier Datumssensoren für die jeweils nächste
Restmüll-, Bio-, Gelbe und Papiertonne. Weitere Terminarten bleiben im Kalender
sichtbar. Der ausgewählte Abfuhrbereich kann unter **Konfigurieren** geändert
werden. Siehe [Abfalltermine](waste.md).

## Bewusst nicht enthalten

E-Ladestationen werden seit Version 0.3.0 weder geladen noch als Entitäten
angelegt. Bei einem Update von 0.2.x entfernt die Migration die alten
Ladestations-Entitäten und -Geräte automatisch.

