# Änderungsverlauf

Alle veröffentlichten Änderungen dieses Projekts werden hier zusammengefasst.

## 0.5.0 – 2026-11-03

- automatische oder manuelle Straßenauswahl im Einrichtungs- und Optionsdialog
  unter Geräte & Dienste ausdrücklich auswählbar gemacht
- bei manueller Auswahl keine Abfrage der Heimkoordinaten bei Photon
- Auswahl von „Forchheim - Im Grund“ anhand des öffentlichen ICS-Kalenders
  geprüft und dokumentiert
- unabhängigen Abfallkalender-Abgleich ergänzt; Ausfälle der Messdatenabfrage
  unterbrechen bereits geladene Abfalltermine nicht
- überlappende ganztägige Termine bei Kalenderabfragen korrigiert
- Abrufstatus und Zeitpunkt des letzten erfolgreichen Abrufs als Diagnose-Sensoren
  ergänzt
- Vorlage für Erinnerungen vor der Abholung hinzugefügt
- mehrere Straßen oder Ortschaften mit eigenem Kalender und Terminsensoren
  auswählbar gemacht; bestehende Entitäts-IDs bleiben erhalten

## 0.4.1 – 2026-10-27

- eindeutige Straßentreffer bei der Abfallkalender-Einrichtung automatisch
  zugeordnet und den zugehörigen ICS-Kalender vorher geprüft
- bei unklarer Straße weiterhin eine manuelle Auswahl angeboten
- Aktivierung in bestehenden Installationen und Kalenderanzeige dokumentiert
- Datumssensor für die Singletonne ergänzt und die Gelbe Tonne als
  Kunststoffsammlung bezeichnet; bestehende Entitäts-ID bleibt erhalten

## 0.4.0 – 2026-10-27

- Messstationen im Einrichtungsdialog und später in den Optionen auswählbar;
  alle Sensoren einer Station bleiben zusammen
- bestehende Installationen behalten ihre Stationsauswahl und Entitäts-IDs
- dynamische Dashboard-Karte für die Anzeige ausgewählter Stationen dokumentiert
- optionalen Abfallkalender mit Straßenvorschlag, manueller Auswahl,
  Kalender-Entität und vier Termin-Sensoren ergänzt
- gewählten Abfuhrbereich in den Integrationsoptionen änderbar gemacht

## 0.3.0 – 2026-10-01

- E-Ladestationen vollständig aus Datenabruf und Entitäten entfernt
- automatische Migration für alte Ladestations-Entitäten und -Geräte ergänzt
- Zustandsklassen aller verbleibenden numerischen Sensoren vereinheitlicht,
  damit Recorder-Verläufe und Langzeitstatistiken genutzt werden können
- Migration und Sensorverhalten mit zusätzlichen Tests abgesichert

## 0.2.0 – 2026-09-30

- alle öffentlichen Wetter-, Temperatur- und Feuchtestationen eingebunden
- Fahrbahnsensor der Lila Brücke ergänzt
- Verkehrsprofile, Baustellen, Parkmöglichkeiten, Fahrradständer und
  Spielplätze ergänzt
- Entfernungssensoren für Bus, Bahn, Baustellen und Spielplätze ergänzt
- Datenabrufe gebündelt und große Datensätze zwischengespeichert

## 0.1.1 – 2026-09-30

- HACS-Branding ergänzt
- Abhängigkeiten der GitHub-Actions-Prüfungen korrigiert

## 0.1.0 – 2026-09-30

- erste Veröffentlichung mit Forchheimer Wetterstationsdaten
