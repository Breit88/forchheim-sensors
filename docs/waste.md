# Abfalltermine

Der optionale Abfallkalender liest die öffentliche Orts- und Straßenauswahl von
[abfalltermine-forchheim.de](https://www.abfalltermine-forchheim.de/Forchheim/Landkreis/Forchheim).
Er funktioniert für jede Home-Assistant-Installation unabhängig von einer
bestimmten Adresse. Der gewählte Eintrag wird als Option dieser Installation
gespeichert.

Bei der erstmaligen Aktivierung fragt die Integration mit den Heimkoordinaten
einmalig [Photon](https://github.com/komoot/photon) nach einem Adressvorschlag.
Die Antwort wird mit der aktuellen Auswahlliste des Landkreises abgeglichen.
Ein eindeutiger Straßentreffer wird nach Prüfung seines ICS-Kalenders
automatisch übernommen. Bei mehreren Abfuhrabschnitten derselben Straße oder
fehlendem Treffer erscheint die Auswahlliste. Ein unbekannter Straßenname
wird nicht auf einen beliebigen Kalender derselben Gemeinde umgebogen.

Nach der Auswahl liest die Integration den ICS-Kalender des Landkreises. Es
entstehen eine Kalender-Entität und fünf Datumssensoren für die jeweils nächste
Restmülltonne, Singletonne, Biotonne, Papiertonne und Kunststoffsammlung
(in der Quelle „Gelbe Tonne“). Der Kalender enthält auch zusätzliche
Abfallarten, falls die Quelle sie anbietet. Die ICS-Daten werden höchstens alle
sechs Stunden neu abgerufen. Bei einem vorübergehenden Ausfall bleiben die
zuletzt erfolgreich geladenen Termine erhalten.

Bei einer bereits eingerichteten Integration: Die aktuelle Version über HACS
herunterladen und Home Assistant neu starten. Danach unter **Einstellungen →
Geräte & Dienste → Digitales Forchheim → Konfigurieren** die Option
**Abfalltermine einbinden** aktivieren. Nach erfolgreicher Zuordnung erscheint
eine Kalenderentität und fünf Datumssensoren. Die Entitäts-ID kann abweichen,
falls bereits eine gleichnamige Entität existiert.

Für eine sichtbare Monatsansicht im Dashboard eine **Kalender-Karte** hinzufügen
und die neue Forchheim-Kalenderentität auswählen. Sie kann auch in Home
Assistants Kalenderansicht eingeblendet werden. Wenn die automatische
Straßenzuordnung nicht passt, lässt sich der Abfuhrbereich unter
**Konfigurieren** manuell ändern.

Die Integration ändert keine vorhandenen Abfallkalender oder Dashboards. Wenn
bereits eine ICS-Einbindung besteht, prüfe nach Aktivierung der neuen Entitäten,
welche davon du im Dashboard und in Erinnerungen verwenden möchtest.
