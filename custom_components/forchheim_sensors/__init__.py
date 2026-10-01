"""Forchheim Sensors integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ForchheimApiClient
from .const import CITY_UNIQUE_ID, DOMAIN
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
            version=3,
        )
    if entry.version == 2:
        entity_registry = er.async_get(hass)
        legacy_unique_ids = {
            "city_car_charging_count",
            "city_bike_charging_count",
        }
        for entity in er.async_entries_for_config_entry(
            entity_registry, entry.entry_id
        ):
            if entity.unique_id.startswith("charging_") or entity.unique_id in (
                legacy_unique_ids
            ):
                entity_registry.async_remove(entity.entity_id)

        device_registry = dr.async_get(hass)
        for device in dr.async_entries_for_config_entry(
            device_registry, entry.entry_id
        ):
            if any(
                domain == DOMAIN and identifier.startswith("charging_")
                for domain, identifier in device.identifiers
            ):
                device_registry.async_remove_device(device.id)

        hass.config_entries.async_update_entry(entry, version=3)
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
