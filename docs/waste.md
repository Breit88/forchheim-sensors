# Abfalltermine

Der optionale Abfallkalender liest die öffentliche Orts- und Straßenauswahl von
[abfalltermine-forchheim.de](https://www.abfalltermine-forchheim.de/Forchheim/Landkreis/Forchheim).
Er funktioniert für jede Home-Assistant-Installation unabhängig von einer
bestimmten Adresse. Die gewählten Einträge werden als Optionen dieser
Installation gespeichert.

Im Einrichtungsdialog und unter **Einstellungen → Geräte & Dienste → Digitales
Forchheim → Konfigurieren** kann zwischen automatischer und manueller
Straßenauswahl gewählt werden. Bei manueller Auswahl zeigt die Integration alle
Straßen und Ortschaften des Landkreises als durchsuchbare Liste. Es können auch
mehrere Einträge ausgewählt werden, etwa für zwei Wohnungen. Beispiel:
**Forchheim - Im Grund**. Dabei werden keine Heimkoordinaten an einen
Adressdienst gesendet.

Bei automatischer Auswahl fragt die Integration mit den Heimkoordinaten einmalig
[Photon](https://github.com/komoot/photon) nach einem Adressvorschlag.
Die Antwort wird mit der aktuellen Auswahlliste des Landkreises abgeglichen.
Ein eindeutiger Straßentreffer wird in der Auswahlliste vorausgewählt und vor
dem Speichern bestätigt. Weitere Adressen können ergänzt werden. Bei mehreren
Abfuhrabschnitten derselben Straße oder fehlendem Treffer bleibt die Auswahl
offen. Ein unbekannter Straßenname wird nicht auf einen beliebigen Kalender
derselben Gemeinde umgebogen.

Ein `webcal://`-Link wie der für **Forchheim - Im Grund** bezeichnet denselben
ICS-Kalender. In der Integration wird die Straße aus der Liste ausgewählt; ein
Link muss nicht eingefügt werden. Die Parameter `RESTMUELL`, `BIO`,
`YELLOW_SACK` und `PAPER` filtern einen heruntergeladenen Kalender. Die
Integration lädt den vollständigen ICS-Kalender des gewählten Abfuhrbereichs,
damit auch Termine der Singletonne verfügbar bleiben.

Für jeden ausgewählten Abfuhrbereich liest die Integration einen eigenen
ICS-Kalender. Es entstehen eine Kalender-Entität und fünf Datumssensoren für
die jeweils nächste Restmülltonne, Singletonne, Biotonne, Papiertonne und
Kunststoffsammlung (in der Quelle „Gelbe Tonne“). Der Kalender enthält auch
zusätzliche Abfallarten, falls die Quelle sie anbietet. Die ICS-Daten werden
alle sechs Stunden neu abgerufen. Der Abruf läuft unabhängig von den
Messstationen. Bei einem vorübergehenden Ausfall bleiben die zuletzt
erfolgreich geladenen Termine erhalten. Zwei Diagnose-Sensoren zeigen den
aktuellen Abrufstatus und den letzten erfolgreichen Abruf seit dem Start von
Home Assistant.

Bei einer bereits eingerichteten Integration: Die aktuelle Version über HACS
herunterladen und Home Assistant neu starten. Danach unter **Einstellungen →
Geräte & Dienste → Digitales Forchheim → Konfigurieren** die Option
**Abfalltermine einbinden** aktivieren. Für eine feste Straßenauswahl
**Straße manuell auswählen** wählen und einen oder mehrere Abfuhrbereiche
suchen. Nach erfolgreicher Zuordnung erscheinen pro Bereich ein Kalender,
fünf Datumssensoren und zwei Diagnose-Sensoren. Bestehende Entitäts-IDs für
den bisherigen Abfuhrbereich bleiben erhalten. Die Entitäts-ID neuer Bereiche
kann abweichen, falls bereits eine gleichnamige Entität existiert.

Für eine sichtbare Monatsansicht im Dashboard eine **Kalender-Karte** hinzufügen
und eine oder mehrere Forchheim-Kalenderentitäten auswählen. Sie können auch in Home
Assistants Kalenderansicht eingeblendet werden. Wenn die automatische
Straßenzuordnung nicht passt, lässt sich der Abfuhrbereich unter
**Konfigurieren** manuell ändern.

## Erinnerung am Vorabend

Die Datei
[`blueprints/automation/forchheim_sensors/waste_reminder.yaml`](../blueprints/automation/forchheim_sensors/waste_reminder.yaml)
ist eine Vorlage für eine Home-Assistant-Automation. Sie wird nicht automatisch
mit einer HACS-Integration in Home Assistant installiert. Kopiere sie in deiner
Home-Assistant-Konfiguration nach
`blueprints/automation/forchheim_sensors/waste_reminder.yaml`, lade die
Automationsvorlagen neu und erstelle daraus eine Automation. Wähle den Kalender,
die Abfallarten und eine Benachrichtigungsaktion. Im Nachrichtentext kannst du
`{{ trigger.calendar_event.summary }}` für die Abfallart verwenden. Der
voreingestellte Versatz `-05:00:00` löst um 19 Uhr am Vortag aus. Bei mehreren
Adressen kann je Kalender eine eigene Automation angelegt werden.

Die Integration ändert keine vorhandenen Abfallkalender oder Dashboards. Wenn
bereits eine ICS-Einbindung besteht, prüfe nach Aktivierung der neuen Entitäten,
welche davon du im Dashboard und in Erinnerungen verwenden möchtest.
