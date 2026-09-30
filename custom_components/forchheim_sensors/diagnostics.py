"""Diagnostics for Forchheim Sensors."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import ForchheimConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ForchheimConfigEntry
) -> dict[str, Any]:
    """Return non-sensitive diagnostics for a config entry."""
    return {
        "entry": {
            "data": dict(entry.data),
            "options": dict(entry.options),
        },
        "last_update_success": entry.runtime_data.last_update_success,
        "measurements": {
            key: {
                "value": measurement.value,
                "measured_at": (
                    measurement.measured_at.isoformat()
                    if measurement.measured_at
                    else None
                ),
            }
            for key, measurement in entry.runtime_data.data.items()
        },
    }
