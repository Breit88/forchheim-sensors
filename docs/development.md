# Entwicklung und Tests

## Projektaufbau

| Pfad | Inhalt |
| --- | --- |
| `custom_components/forchheim_sensors/` | Integration, API-Client, Coordinator, Sensoren und Übersetzungen |
| `tests/` | Tests für Konfiguration, Sensoraufbau, Aktualisierung und Migration |
| `.github/workflows/validate.yml` | HACS-Prüfung, Ruff und Home-Assistant-Tests |

## Lokale Entwicklungsumgebung

Die Tests verwenden Python 3.14 und die Testwerkzeuge für benutzerdefinierte
Home-Assistant-Komponenten.

```bash
python3.14 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install pytest-homeassistant-custom-component==0.13.367 ruff
```

Anschließend können dieselben wesentlichen Prüfungen wie in GitHub Actions
ausgeführt werden:

```bash
ruff format --check .
ruff check .
pytest -q
```

## Beiträge

Änderungen sollten die öffentlichen Dienste sparsam abfragen, vorhandene
eindeutige Entitäts-IDs erhalten und Ausfälle optionaler Quellen abfangen. Für
neues Verhalten sind passende Tests erforderlich. Pull Requests sollten kurz
erklären, welche Datenquelle oder welches Verhalten sich ändert und wie die
Änderung geprüft wurde.

Die Integrationsversion steht in
`custom_components/forchheim_sensors/manifest.json`. Funktionale Releases
werden zusätzlich im [Änderungsverlauf](../CHANGELOG.md) dokumentiert.
