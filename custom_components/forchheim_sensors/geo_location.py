"""Map public bus stops, playgrounds, construction and weather stations."""

from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ForchheimConfigEntry
from .geography import distance_km
from .icon_assets import PLACE_PICTURES
from .models import CityData, Place

PARALLEL_UPDATES = 0

SOURCES = {
    "bus": "forchheim_sensors_bus",
    "playground": "forchheim_sensors_playground",
    "construction": "forchheim_sensors_construction",
    "weather": "forchheim_sensors_weather",
}


def _visible_places(data: CityData) -> dict[str, tuple[str, str, Place]]:
    """Return each distinct city point and weather station."""
    result: dict[str, tuple[str, str, Place]] = {}
    groups = (
        (
            "bus",
            "Bushaltestelle",
            (p for p in data.transit_stops if p.category == "BUS"),
        ),
        ("playground", "Spielplatz", iter(data.playgrounds)),
        ("construction", "Baustelle", iter(data.construction_sites)),
        (
            "weather",
            "Wetterstation",
            (
                Place(
                    station.uid,
                    "weather",
                    station.name,
                    station.latitude,
                    station.longitude,
                    note=station.model,
                )
                for station in data.stations
                if station.category == "weather"
            ),
        ),
    )
    for category, label, places in groups:
        for place in places:
            key = f"{category}:{place.name}:{place.latitude:.7f}:{place.longitude:.7f}"
            result[key] = (SOURCES[category], label, place)
    return result


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ForchheimConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Track all city points as the public feeds change."""
    coordinator = entry.runtime_data
    known: dict[str, ForchheimPlaceEvent] = {}
    lock = asyncio.Lock()

    async def sync_places() -> None:
        async with lock:
            if coordinator.data is None:
                return
            current = _visible_places(coordinator.data)
            for key in set(known) - set(current):
                await known.pop(key).async_remove(force_remove=True)
            new_entities: list[ForchheimPlaceEvent] = []
            for key, (source, label, place) in current.items():
                if key in known:
                    known[key].update_from_place(place)
                    known[key].async_write_ha_state()
                else:
                    entity = ForchheimPlaceEvent(
                        source,
                        label,
                        place,
                        hass.config.latitude,
                        hass.config.longitude,
                    )
                    known[key] = entity
                    new_entities.append(entity)
            if new_entities:
                async_add_entities(new_entities)

    def schedule_sync() -> None:
        hass.async_create_task(sync_places())

    entry.async_on_unload(coordinator.async_add_listener(schedule_sync))
    await sync_places()


class ForchheimPlaceEvent(GeolocationEvent):
    """One public place visible on Home Assistant's map."""

    _attr_should_poll = False
    _attr_unit_of_measurement = UnitOfLength.KILOMETERS

    def __init__(
        self,
        source: str,
        label: str,
        place: Place,
        home_latitude: float,
        home_longitude: float,
    ) -> None:
        self._attr_source = source
        kind = source.removeprefix("forchheim_sensors_")
        self._attr_entity_picture = PLACE_PICTURES.get(kind)
        self._attr_icon = {
            "bus": "mdi:bus-stop",
            "playground": "mdi:slide",
            "construction": "mdi:traffic-cone",
            "weather": "mdi:weather-windy",
        }.get(kind)
        self._label = label
        self._home_latitude = home_latitude
        self._home_longitude = home_longitude
        self.update_from_place(place)

    def update_from_place(self, place: Place) -> None:
        """Refresh the visible details for this point."""
        self._attr_name = f"{self._label} {place.name}"
        self._attr_latitude = place.latitude
        self._attr_longitude = place.longitude
        self._attr_distance = round(
            distance_km(
                self._home_latitude,
                self._home_longitude,
                place.latitude,
                place.longitude,
            ),
            2,
        )
        attributes: dict[str, Any] = {
            "address": place.address,
            "description": place.note,
            "type": place.category,
            **place.extra,
        }
        self._attr_extra_state_attributes = {
            key: value for key, value in attributes.items() if value is not None
        }
