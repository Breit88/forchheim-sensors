"""Tests for the public waste calendar format and street matching."""

from datetime import date

import pytest

from custom_components.forchheim_sensors.parser import ForchheimInvalidResponseError
from custom_components.forchheim_sensors.waste import (
    WasteLocation,
    parse_waste_ics,
    parse_waste_locations,
    suggest_waste_locations,
)


def test_parse_locations_and_divided_street() -> None:
    """Only the actual street selector is parsed and both sections survive."""
    html = (
        '<select id="streets-selection">'
        '<option value="/Forchheim/Landkreis/Forchheim%20-%20Ringstra%C3%9Fe">'
        "Forchheim - Ringstraße</option>"
        '<option value="/Forchheim/Landkreis/Forchheim%20-%20Adenauerallee%20'
        '(westlich%20des%20Kanals)">'
        "Forchheim - Adenauerallee (westlich des Kanals)</option>"
        '<option value="/Forchheim/Landkreis/Forchheim%20-%20Adenauerallee%20'
        '(%C3%B6stlich%20des%20Kanals)">'
        "Forchheim - Adenauerallee (östlich des Kanals)</option>"
        "</select>"
    )
    locations = parse_waste_locations(html)
    assert len(locations) == 3
    assert locations[0].path.endswith("Ringstraße")
    assert suggest_waste_locations(
        locations, {"city": "Forchheim", "street": "Ringstraße"}
    ) == [locations[0]]
    assert (
        suggest_waste_locations(
            locations, {"city": "Forchheim", "street": "Adenauerallee"}
        )
        == locations[1:]
    )
    assert (
        suggest_waste_locations(locations, {"city": "Erlangen", "street": "Ringstraße"})
        == []
    )


def test_match_single_locality_without_street() -> None:
    locations = [
        WasteLocation("/Forchheim/Landkreis/Dormitz - Dormitz", "Dormitz - Dormitz")
    ]
    assert suggest_waste_locations(locations, {"city": "Dormitz"}) == locations


def test_parse_ics_all_day_events_and_ignore_cancelled() -> None:
    ics = (
        "BEGIN:VCALENDAR\r\n"
        "BEGIN:VEVENT\r\nSUMMARY;LANGUAGE=de-de:Restmülltonne\r\n"
        "DTSTART;VALUE=DATE:20261028\r\nEND:VEVENT\r\n"
        "BEGIN:VEVENT\r\nSUMMARY:Gelbe Ton\r\n ne\r\n"
        "DTSTART;VALUE=DATE:20261030\r\nEND:VEVENT\r\n"
        "BEGIN:VEVENT\r\nSUMMARY:Biotonne\r\nSTATUS:CANCELLED\r\n"
        "DTSTART;VALUE=DATE:20261029\r\nEND:VEVENT\r\nEND:VCALENDAR"
    )
    events = parse_waste_ics(ics)
    assert [(event.day, event.kind) for event in events] == [
        (date(2026, 10, 28), "Restmülltonne"),
        (date(2026, 10, 30), "Gelbe Tonne"),
    ]


def test_invalid_ics_fails_loudly() -> None:
    with pytest.raises(ForchheimInvalidResponseError):
        parse_waste_ics("<html>error</html>")
