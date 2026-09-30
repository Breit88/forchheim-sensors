"""Tests for the response parsers."""

from datetime import UTC, datetime

from custom_components.forchheim_sensors.parser import (
    ForchheimInvalidResponseError,
    parse_measurements,
    parse_stations,
)


def test_parse_station() -> None:
    """A station is extracted from the GeoJSON properties."""
    payload = {
        "features": [
            {
                "properties": {
                    "Things/0/properties/thingUID": "19-843",
                    "Things/0/name": "Schleuseninsel",
                    "Things/0/properties/sensordata/sensorName": "WS-L1200-N",
                },
                "geometry": {"coordinates": [11.04788, 49.74302]},
            }
        ]
    }
    station = parse_stations(payload)[0]
    assert station.uid == "19-843"
    assert station.name == "Schleuseninsel"
    assert station.latitude == 49.74302


def test_parse_measurements_by_field_name() -> None:
    """Grafana fields are parsed independently of their column order."""
    payload = {
        "results": {
            "A": {
                "frames": [
                    {
                        "schema": {
                            "fields": [
                                {"name": "Event_Value"},
                                {"name": "Event_DateTime"},
                                {"name": "Datapoint_Title"},
                            ]
                        },
                        "data": {
                            "values": [
                                [21.5, 58],
                                [1_790_785_528_848, 1_790_785_528_848],
                                ["Temperatur", "Luftfeuchtigkeit (rel.)"],
                            ]
                        },
                    }
                ]
            }
        }
    }
    measurements = parse_measurements(payload)
    assert measurements["Temperatur"].value == 21.5
    assert measurements["Temperatur"].measured_at == datetime.fromtimestamp(
        1_790_785_528.848, tz=UTC
    )
    assert measurements["Luftfeuchtigkeit (rel.)"].value == 58


def test_reject_empty_measurements() -> None:
    """An empty Grafana response does not silently create unknown sensors."""
    payload = {
        "results": {
            "A": {
                "frames": [
                    {
                        "schema": {
                            "fields": [
                                {"name": "Datapoint_Title"},
                                {"name": "Event_Value"},
                                {"name": "Event_DateTime"},
                            ]
                        },
                        "data": {"values": [[], [], []]},
                    }
                ]
            }
        }
    }
    try:
        parse_measurements(payload)
    except ForchheimInvalidResponseError:
        pass
    else:
        raise AssertionError("Empty measurements must be rejected")
