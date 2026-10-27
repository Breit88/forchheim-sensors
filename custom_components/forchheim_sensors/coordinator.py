"""Data update coordinator for Forchheim Sensors."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import ForchheimApiClient, ForchheimApiError
from .const import (
    CONF_SCAN_INTERVAL,
    CONF_STATIONS,
    CONF_WASTE_LOCATION,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .models import CityData, TrafficSnapshot
from .parser import ForchheimInvalidResponseError

_LOGGER = logging.getLogger(__name__)


class ForchheimDataUpdateCoordinator(DataUpdateCoordinator[CityData]):
    """Coordinate shared requests for all public city data."""

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
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )

    async def _async_update_data(self) -> CityData:
        """Fetch current readings and cached public city data."""
        try:
            stations = await self.client.async_get_all_stations()
            selected = self.config_entry.options.get(CONF_STATIONS)
            station_uids = [
                station.uid
                for station in stations
                if selected is None or station.uid in selected
            ]
            now = dt_util.now()
            waste_location = self.config_entry.options.get(CONF_WASTE_LOCATION)
            waste_request = (
                self.client.async_get_waste_events(waste_location)
                if waste_location
                else asyncio.sleep(0, result=())
            )
            results = await asyncio.gather(
                self.client.async_get_station_measurements(station_uids)
                if station_uids
                else asyncio.sleep(0, result={}),
                self.client.async_get_public_places(),
                self.client.async_get_construction_sites(),
                self.client.async_get_traffic(now.weekday() >= 5, now.hour),
                waste_request,
                return_exceptions=True,
            )
            (
                measurements_result,
                places_result,
                construction_result,
                traffic_result,
                waste_result,
            ) = results
            if isinstance(measurements_result, Exception):
                raise measurements_result

            previous = self.data
            if isinstance(places_result, Exception):
                _LOGGER.warning("Unable to update public places: %s", places_result)
                places = list(previous.places) if previous else []
                playgrounds = list(previous.playgrounds) if previous else []
                transit = list(previous.transit_stops) if previous else []
            else:
                places, playgrounds, transit = places_result
            if isinstance(construction_result, Exception):
                _LOGGER.warning(
                    "Unable to update construction sites: %s", construction_result
                )
                construction = list(previous.construction_sites) if previous else []
            else:
                construction = construction_result
            if isinstance(traffic_result, Exception):
                _LOGGER.warning("Unable to update traffic profile: %s", traffic_result)
                traffic = (
                    previous.traffic
                    if previous
                    else TrafficSnapshot("unavailable", 0.0, 0, 0)
                )
            else:
                traffic = traffic_result
            if isinstance(waste_result, Exception):
                _LOGGER.warning("Unable to update waste calendar: %s", waste_result)
                waste_events = previous.waste_events if previous else ()
            else:
                waste_events = waste_result
            places = [place for place in places if "Ladesäule" not in place.category]
            return CityData(
                stations=tuple(stations),
                measurements=measurements_result,
                places=tuple(places),
                playgrounds=tuple(playgrounds),
                transit_stops=tuple(transit),
                construction_sites=tuple(construction),
                traffic=traffic,
                waste_events=waste_events,
            )
        except (ForchheimApiError, ForchheimInvalidResponseError) as err:
            raise UpdateFailed(
                f"Unable to update Forchheim public data: {err}"
            ) from err
