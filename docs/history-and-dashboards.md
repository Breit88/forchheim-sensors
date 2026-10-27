# Verlauf und Dashboards

## Aufzeichnung in Home Assistant

Die Integration speichert selbst keine Zeitreihen. Home Assistants
`recorder`-Integration zeichnet die Zustände auf. Alle numerischen Entitäten
von Digitales Forchheim besitzen die Zustandsklasse `measurement`; daraus
erzeugt Home Assistant zusätzlich Langzeitstatistiken.

Damit stehen zwei Arten von Diagrammen zur Verfügung:

- **Verlaufsdiagramm** zeigt die einzelnen aufgezeichneten Zustände aus dem
  Recorder.
- **Statistikdiagramm** zeigt verdichtete Langzeitstatistiken wie Mittelwert,
  Minimum und Maximum.

Die Integration ändert kein vorhandenes Dashboard automatisch. Ausgewählte
Messstationen erscheinen als eigene Geräte mit allen ihren Messwerten. Eine
abgewählte Station liefert keine Messwerte mehr. Für ein Dashboard, das sich
der Stationsauswahl automatisch anpasst, kann eine dynamische Karte verwendet
werden.

## Dynamische Karte nach Station

Die folgende Karte benötigt die zusätzliche HACS-Karte
[Auto Entities](https://github.com/thomasloven/lovelace-auto-entities). Füge sie
einmalig als manuelle Karte in den gewünschten Dashboard-Bereich ein. Sie
zeigt danach nur die aktiven Messsensoren dieser Integration und bündelt sie
mit Abschnittsüberschriften nach Station. Die Abfall- und stadtweiten
Zusammenfassungssensoren bleiben außerhalb dieser Karte.

```yaml
type: custom:auto-entities
show_empty: false
card:
  type: entities
  title: Stadt-Sensoren
filter:
  template: |
    {% set ns = namespace(last='') %}
    [
    {% for sensor in states.sensor
       | selectattr('entity_id', 'in', integration_entities('forchheim_sensors'))
       | selectattr('attributes.station_type', 'defined')
       | sort(attribute='attributes.station') %}
      {% if sensor.state not in ['unknown', 'unavailable'] %}
        {% if sensor.attributes.station != ns.last %}
          {"type": "section", "label": {{ sensor.attributes.station | to_json }}},
          {% set ns.last = sensor.attributes.station %}
        {% endif %}
        {"entity": {{ sensor.entity_id | to_json }}},
      {% endif %}
    {% endfor %}
    ]
```

Feste Karten mit einzeln eingetragenen Entitäts-IDs aktualisieren ihre Liste
nicht automatisch. Sie müssen einmalig ersetzt oder manuell gepflegt werden.

## Karte über die Oberfläche anlegen

1. Öffne das gewünschte Dashboard und wähle **Dashboard bearbeiten**.
2. Klicke auf **Karte hinzufügen**.
3. Wähle **Statistikdiagramm** für langfristige Auswertungen oder
   **Verlaufsdiagramm** für den genauen Zustandsverlauf.
4. Füge die gewünschten Entitäten von **Digitales Forchheim** hinzu.
5. Gruppiere möglichst nur Werte mit derselben Einheit in einer Karte, etwa
   Temperaturen gemeinsam und Luftfeuchtigkeit in einer eigenen Karte.

## YAML-Beispiele

Die tatsächlichen Entitäts-IDs findest du unter **Einstellungen → Geräte &
Dienste → Entitäten**. Ersetze die Beispiel-IDs durch die IDs deiner
Installation.

```yaml
type: statistics-graph
title: Temperaturen in Forchheim
chart_type: line
period: hour
days_to_show: 7
stat_types:
  - mean
  - min
  - max
entities:
  - sensor.digitales_forchheim_rathausplatz_temperatur
  - sensor.digitales_forchheim_lila_brucke_lufttemperatur
```

```yaml
type: history-graph
title: Luftfeuchtigkeit letzte 24 Stunden
hours_to_show: 24
entities:
  - sensor.digitales_forchheim_rathausplatz_luftfeuchtigkeit
```

Für Wind, Niederschlag, Luftdruck und Verkehr sollten getrennte Karten
verwendet werden, weil die Einheiten und Größenordnungen unterschiedlich sind.

## Wenn kein Verlauf erscheint

Nach der Ersteinrichtung muss mindestens eine erfolgreiche Aktualisierung
erfolgt sein. Langzeitstatistiken werden erst sichtbar, nachdem Home Assistant
genügend Werte verarbeitet hat. Prüfe außerdem:

- Die Entität ist nicht in deiner `recorder`-Konfiguration ausgeschlossen.
- Die Entität liefert einen numerischen Zustand und ist nicht `unavailable`.
- Unter **Entwicklerwerkzeuge → Statistik** wird kein Reparaturhinweis für die
  Entität angezeigt.
- Datum, Uhrzeit und Zeitzone des Home-Assistant-Systems stimmen.

Weitere Schritte stehen unter [Fehlerbehebung und Diagnose](troubleshooting.md).

