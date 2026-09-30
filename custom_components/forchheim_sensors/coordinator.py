"""Data update coordinator for Forchheim Sensors."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ForchheimApiClient, ForchheimApiError
from .const import CONF_SCAN_INTERVAL, CONF_STATION, DEFAULT_SCAN_INTERVAL, DOMAIN
from .models import Measurement
from .parser import ForchheimInvalidResponseError

_LOGGER = logging.getLogger(__name__)


class ForchheimDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Measurement]]):
    """Coordinate a single request shared by all station entities."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: ForchheimApiClient,
    ) -> None:
        """Initialize the coordinator."""
        self.config_entry = entry
        self.client = client
        interval = int(entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"{DOMAIN}_{entry.data[CONF_STATION]}",
            update_interval=timedelta(seconds=interval),
        )

    async def _async_update_data(self) -> dict[str, Measurement]:
        """Fetch current data from the public service."""
        try:
            return await self.client.async_get_measurements(
                self.config_entry.data[CONF_STATION]
            )
        except (
            ForchheimApiError,
            ForchheimInvalidResponseError,
        ) as err:
            raise UpdateFailed(
                f"Unable to update Forchheim sensor data: {err}"
            ) from err
