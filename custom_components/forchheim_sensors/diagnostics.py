"""Diagnostics for Digitales Forchheim."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import ForchheimConfigEntry
from .const import CONF_WASTE_LOCATION


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ForchheimConfigEntry
) -> dict[str, Any]:
    """Return non-sensitive diagnostics for a config entry."""
    data = entry.runtime_data.data
    options = dict(entry.options)
    if CONF_WASTE_LOCATION in options:
        options[CONF_WASTE_LOCATION] = "<redacted>"
    waste_coordinators = entry.runtime_data.waste_coordinators
    return {
        "entry": {"data": dict(entry.data), "options": options},
        "last_update_success": entry.runtime_data.last_update_success,
        "stations": [
            {"uid": station.uid, "name": station.name, "category": station.category}
            for station in (data.stations if data else ())
        ],
        "measurement_station_count": len(data.measurements) if data else 0,
        "place_count": len(data.places) if data else 0,
        "playground_count": len(data.playgrounds) if data else 0,
        "transit_stop_count": len(data.transit_stops) if data else 0,
        "construction_site_count": len(data.construction_sites) if data else 0,
        "traffic_period": data.traffic.period if data else None,
        "waste_event_count": sum(
            len(item.data or ()) for item in waste_coordinators.values()
        ),
        "waste_sources": [
            {
                "last_update_success": item.last_update_success,
                "last_successful_update": (
                    item.last_successful_update.isoformat()
                    if item.last_successful_update
                    else None
                ),
            }
            for item in waste_coordinators.values()
        ],
        "temporarily_unavailable_sources": ["Raumbelegung"],
    }
