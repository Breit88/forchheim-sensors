"""Config flow for Forchheim Sensors."""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)

from .api import ForchheimApiClient, ForchheimApiError
from .const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_SCAN_INTERVAL,
    CONF_STATION,
    CONF_STATION_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .models import Station
from .parser import ForchheimInvalidResponseError


def _distance_km(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    """Calculate great-circle distance between two positions."""
    radius = 6371.0
    lat_a = radians(latitude_a)
    lat_b = radians(latitude_b)
    delta_lat = radians(latitude_b - latitude_a)
    delta_lon = radians(longitude_b - longitude_a)
    value = sin(delta_lat / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(delta_lon / 2) ** 2
    return 2 * radius * asin(sqrt(value))


def _station_label(
    station: Station, home_latitude: float, home_longitude: float
) -> str:
    """Return a station label including its distance from home."""
    distance = _distance_km(
        home_latitude,
        home_longitude,
        station.latitude,
        station.longitude,
    )
    return f"{station.name} ({distance:.1f} km)"


class ForchheimSensorsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the Forchheim Sensors config flow."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the flow."""
        self._stations: dict[str, Station] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}
        if not self._stations:
            try:
                client = ForchheimApiClient(async_get_clientsession(self.hass))
                stations = await client.async_get_stations()
            except ForchheimApiError:
                errors["base"] = "cannot_connect"
                stations = []
            except ForchheimInvalidResponseError:
                errors["base"] = "invalid_response"
                stations = []
            self._stations = {station.uid: station for station in stations}

        if user_input is not None and not errors:
            station = self._stations.get(user_input[CONF_STATION])
            if station is None:
                errors["base"] = "invalid_station"
            else:
                client = ForchheimApiClient(async_get_clientsession(self.hass))
                try:
                    await client.async_get_measurements(station.uid)
                except ForchheimApiError:
                    errors["base"] = "cannot_connect"
                except ForchheimInvalidResponseError:
                    errors["base"] = "invalid_response"
                else:
                    await self.async_set_unique_id(station.uid)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"Forchheim – {station.name}",
                        data={
                            CONF_STATION: station.uid,
                            CONF_STATION_NAME: station.name,
                            CONF_LATITUDE: station.latitude,
                            CONF_LONGITUDE: station.longitude,
                        },
                        options={CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL]},
                    )

        sorted_stations = sorted(
            self._stations.values(),
            key=lambda station: _distance_km(
                self.hass.config.latitude,
                self.hass.config.longitude,
                station.latitude,
                station.longitude,
            ),
        )
        options = [
            SelectOptionDict(
                value=station.uid,
                label=_station_label(
                    station,
                    self.hass.config.latitude,
                    self.hass.config.longitude,
                ),
            )
            for station in sorted_stations
        ]
        default_station = options[0]["value"] if options else None
        schema_fields: dict[vol.Marker, Any] = {}
        if options:
            schema_fields[vol.Required(CONF_STATION, default=default_station)] = (
                SelectSelector(SelectSelectorConfig(options=options))
            )
            schema_fields[
                vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL)
            ] = NumberSelector(
                NumberSelectorConfig(
                    min=MIN_SCAN_INTERVAL,
                    max=MAX_SCAN_INTERVAL,
                    step=60,
                    mode=NumberSelectorMode.BOX,
                    unit_of_measurement="s",
                )
            )

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(schema_fields), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> ForchheimOptionsFlow:
        """Return the options flow."""
        return ForchheimOptionsFlow()


class ForchheimOptionsFlow(OptionsFlow):
    """Manage polling options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update the polling interval."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current = int(
            self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SCAN_INTERVAL, default=current): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_SCAN_INTERVAL,
                            max=MAX_SCAN_INTERVAL,
                            step=60,
                            mode=NumberSelectorMode.BOX,
                            unit_of_measurement="s",
                        )
                    )
                }
            ),
        )
