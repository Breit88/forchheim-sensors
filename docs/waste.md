# Abfalltermine

Der optionale Abfallkalender liest die öffentliche Orts- und Straßenauswahl von
[abfalltermine-forchheim.de](https://www.abfalltermine-forchheim.de/Forchheim/Landkreis/Forchheim).
Er funktioniert für jede Home-Assistant-Installation unabhängig von einer
bestimmten Adresse. Der gewählte Eintrag wird als Option dieser Installation
gespeichert.

Bei der erstmaligen Aktivierung fragt die Integration mit den Heimkoordinaten
einmalig [Photon](https://github.com/komoot/photon) nach einem Adressvorschlag.
Die Antwort wird mit der aktuellen Auswahlliste des Landkreises abgeglichen.
Ein genauer Treffer wird vorausgewählt, muss aber bestätigt werden. Mehrere
Abfuhrabschnitte derselben Straße werden zur Auswahl angeboten. Bei fehlendem
oder unpassendem Vorschlag kann jeder Eintrag manuell ausgewählt werden.

Nach der Auswahl liest die Integration den ICS-Kalender des Landkreises. Es
entstehen eine Kalender-Entität und vier Datumssensoren für die jeweils nächste
Restmüll-, Bio-, Gelbe und Papiertonne. Der Kalender enthält auch zusätzliche
Abfallarten, falls die Quelle sie anbietet. Die ICS-Daten werden höchstens alle
sechs Stunden neu abgerufen. Bei einem vorübergehenden Ausfall bleiben die
zuletzt erfolgreich geladenen Termine erhalten.

Die Integration ändert keine vorhandenen Abfallkalender oder Dashboards. Wenn
bereits eine ICS-Einbindung besteht, prüfe nach Aktivierung der neuen Entitäten,
welche davon du im Dashboard und in Erinnerungen verwenden möchtest.
