"""Parse and match the Landkreis Forchheim waste calendar."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from urllib.parse import unquote

from .models import WasteEvent
from .parser import ForchheimInvalidResponseError


@dataclass(frozen=True, slots=True)
class WasteLocation:
    """One selectable collection area on the district website."""

    path: str
    name: str


class _LocationParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_select = False
        self.path: str | None = None
        self.label: list[str] = []
        self.locations: list[WasteLocation] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "select" and attributes.get("id") == "streets-selection":
            self.in_select = True
        elif tag == "option" and self.in_select:
            self.path = attributes.get("value")
            self.label = []

    def handle_data(self, data: str) -> None:
        if self.path is not None:
            self.label.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "option" and self.path is not None:
            name = " ".join("".join(self.label).split())
            path = unquote(self.path)
            if path.startswith("/Forchheim/Landkreis/") and name:
                self.locations.append(WasteLocation(path, name))
            self.path = None
        elif tag == "select":
            self.in_select = False


def parse_waste_locations(html: str) -> list[WasteLocation]:
    """Read selectable collection areas without depending on page layout."""
    parser = _LocationParser()
    parser.feed(html)
    if not parser.locations:
        raise ForchheimInvalidResponseError("Waste location list is empty")
    return parser.locations


def _normalized(value: str) -> str:
    return (
        value.casefold()
        .replace("ß", "ss")
        .replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("str.", "strasse")
        .replace("straße", "strasse")
        .strip()
    )


def suggest_waste_locations(
    locations: list[WasteLocation], address: dict[str, str]
) -> list[WasteLocation]:
    """Suggest exact street matches; leave divided streets for user confirmation."""
    city = address.get("city") or address.get("town") or address.get("village")
    street = address.get("street")
    district = address.get("district")
    if not city:
        return []
    municipality = _normalized(city)
    candidates = [
        location
        for location in locations
        if _normalized(location.name.split(" - ", 1)[0]) == municipality
    ]
    if street:
        road = _normalized(street)
        matches = [
            location
            for location in candidates
            if " - " in location.name
            and (
                _normalized(location.name.split(" - ", 1)[1]) == road
                or _normalized(location.name.split(" - ", 1)[1]).startswith(road + " (")
            )
        ]
        if matches:
            return matches
    if district:
        area = _normalized(district)
        matches = [
            location
            for location in candidates
            if " - " in location.name
            and _normalized(location.name.split(" - ", 1)[1]) == area
        ]
        if matches:
            return matches
    return candidates if len(candidates) == 1 else []


def parse_waste_ics(payload: str) -> tuple[WasteEvent, ...]:
    """Read all-day collection dates from the official ICS feed."""
    if "BEGIN:VCALENDAR" not in payload:
        raise ForchheimInvalidResponseError("Waste calendar is not ICS")
    unfolded: list[str] = []
    for line in payload.splitlines():
        if line.startswith((" ", "\t")) and unfolded:
            unfolded[-1] += line[1:]
        else:
            unfolded.append(line)
    events: list[WasteEvent] = []
    current: dict[str, str] | None = None
    for line in unfolded:
        if line == "BEGIN:VEVENT":
            current = {}
        elif line == "END:VEVENT" and current is not None:
            raw_day = current.get("DTSTART")
            kind = current.get("SUMMARY")
            if raw_day and kind and current.get("STATUS") != "CANCELLED":
                try:
                    day = date.fromisoformat(raw_day)
                except ValueError as err:
                    raise ForchheimInvalidResponseError("Invalid waste date") from err
                events.append(WasteEvent(day, kind))
            current = None
        elif current is not None and ":" in line:
            key, value = line.split(":", 1)
            key = key.split(";", 1)[0]
            if key == "DTSTART" and re.fullmatch(r"\d{8}", value):
                current[key] = value
            elif key in ("SUMMARY", "STATUS"):
                current[key] = value.replace("\\,", ",").replace("\\;", ";")
    if not events:
        raise ForchheimInvalidResponseError("Waste calendar has no events")
    return tuple(sorted(events, key=lambda event: (event.day, event.kind)))
