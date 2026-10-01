"""Diagnostics for Digitales Forchheim."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import ForchheimConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ForchheimConfigEntry
) -> dict[str, Any]:
    """Return non-sensitive diagnostics for a config entry."""
    data = entry.runtime_data.data
    return {
        "entry": {"data": dict(entry.data), "options": dict(entry.options)},
        "last_update_success": entry.runtime_data.last_update_success,
        "stations": [
            {"uid": station.uid, "name": station.name, "category": station.category}
            for station in data.stations
        ],
        "measurement_station_count": len(data.measurements),
        "place_count": len(data.places),
        "playground_count": len(data.playgrounds),
        "transit_stop_count": len(data.transit_stops),
        "construction_site_count": len(data.construction_sites),
        "traffic_period": data.traffic.period,
        "temporarily_unavailable_sources": ["Raumbelegung"],
    }
