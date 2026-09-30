"""Forchheim Sensors integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ForchheimApiClient
from .const import CITY_UNIQUE_ID
from .coordinator import ForchheimDataUpdateCoordinator

PLATFORMS = [Platform.SENSOR]

type ForchheimConfigEntry = ConfigEntry[ForchheimDataUpdateCoordinator]


async def async_migrate_entry(hass: HomeAssistant, entry: ForchheimConfigEntry) -> bool:
    """Migrate a single-station entry to the citywide data entry."""
    if entry.version == 1:
        hass.config_entries.async_update_entry(
            entry,
            data={},
            title="Digitales Forchheim",
            unique_id=CITY_UNIQUE_ID,
            version=2,
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ForchheimConfigEntry) -> bool:
    """Set up Forchheim Sensors from a config entry."""
    client = ForchheimApiClient(async_get_clientsession(hass))
    coordinator = ForchheimDataUpdateCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ForchheimConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: ForchheimConfigEntry) -> None:
    """Reload after an options change."""
    await hass.config_entries.async_reload(entry.entry_id)
