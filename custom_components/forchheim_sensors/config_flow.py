"""Config flow for Forchheim Sensors."""

from __future__ import annotations

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
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .api import ForchheimApiClient, ForchheimApiError
from .const import (
    CITY_UNIQUE_ID,
    CONF_SCAN_INTERVAL,
    CONF_STATIONS,
    CONF_WASTE_ENABLED,
    CONF_WASTE_LOCATION,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .models import Station
from .parser import ForchheimInvalidResponseError
from .waste import WasteLocation, suggest_waste_locations


def _schema(
    default: int,
    stations: list[Station],
    selected: list[str],
    waste_enabled: bool = False,
) -> vol.Schema:
    """Return the shared setup schema."""
    category_names = {
        "weather": "Wetterstation",
        "temperature": "Temperatur/Feuchte",
        "road": "Fahrbahnsensor",
    }
    station_choices = [
        {
            "value": station.uid,
            "label": (
                f"{category_names.get(station.category, 'Station')} · {station.name}"
            ),
        }
        for station in stations
    ]
    return vol.Schema(
        {
            vol.Required(CONF_SCAN_INTERVAL, default=default): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_SCAN_INTERVAL,
                    max=MAX_SCAN_INTERVAL,
                    step=60,
                    mode=NumberSelectorMode.BOX,
                    unit_of_measurement="s",
                )
            ),
            vol.Required(CONF_WASTE_ENABLED, default=waste_enabled): BooleanSelector(),
            vol.Required(CONF_STATIONS, default=selected): SelectSelector(
                SelectSelectorConfig(
                    options=station_choices,
                    mode=SelectSelectorMode.DROPDOWN,
                    multiple=True,
                )
            ),
        }
    )


class ForchheimSensorsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the Forchheim Sensors config flow."""

    VERSION = 4

    def __init__(self) -> None:
        super().__init__()
        self._setup_input: dict[str, Any] = {}
        self._waste_locations: list[WasteLocation] | None = None
        self._waste_default: str | None = None
        self._stations: list[Station] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up all public Forchheim data with one form."""
        await self.async_set_unique_id(CITY_UNIQUE_ID)
        self._abort_if_unique_id_configured()
        client = ForchheimApiClient(async_get_clientsession(self.hass))
        if self._stations is None:
            try:
                self._stations = await client.async_get_all_stations()
            except (ForchheimApiError, ForchheimInvalidResponseError):
                return self.async_abort(reason="cannot_connect")
        errors: dict[str, str] = {}
        if user_input is not None:
            station_uids = user_input[CONF_STATIONS]
            if not set(station_uids) <= {station.uid for station in self._stations}:
                errors[CONF_STATIONS] = "invalid_station"
            else:
                try:
                    if station_uids:
                        await client.async_get_station_measurements(station_uids)
                except ForchheimApiError:
                    errors["base"] = "cannot_connect"
                except ForchheimInvalidResponseError:
                    errors["base"] = "invalid_response"
            if not errors:
                if user_input[CONF_WASTE_ENABLED]:
                    self._setup_input = user_input
                    return await self.async_step_waste()
                return self.async_create_entry(
                    title="Digitales Forchheim",
                    data={},
                    options={
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                        CONF_STATIONS: station_uids,
                    },
                )
        return self.async_show_form(
            step_id="user",
            data_schema=_schema(
                DEFAULT_SCAN_INTERVAL,
                self._stations,
                [station.uid for station in self._stations],
            ),
            errors=errors,
        )

    async def async_step_waste(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm a suggested or manually chosen collection area."""
        client = ForchheimApiClient(async_get_clientsession(self.hass))
        if self._waste_locations is None:
            try:
                self._waste_locations = await client.async_get_waste_locations()
            except (ForchheimApiError, ForchheimInvalidResponseError):
                return self.async_abort(reason="waste_unavailable")
            try:
                address = await client.async_reverse_geocode(
                    self.hass.config.latitude, self.hass.config.longitude
                )
            except ForchheimApiError:
                address = {}
            suggestions = suggest_waste_locations(self._waste_locations, address)
            if len(suggestions) == 1:
                self._waste_default = suggestions[0].path
            self._waste_locations = suggestions + [
                location
                for location in self._waste_locations
                if location not in suggestions
            ]
        errors: dict[str, str] = {}
        if user_input is not None:
            location = next(
                (
                    item
                    for item in self._waste_locations
                    if item.path == user_input[CONF_WASTE_LOCATION]
                ),
                None,
            )
            if location is None:
                errors[CONF_WASTE_LOCATION] = "invalid_location"
            else:
                try:
                    await client.async_get_waste_events(location.path)
                except (ForchheimApiError, ForchheimInvalidResponseError):
                    errors["base"] = "waste_unavailable"
                else:
                    return self.async_create_entry(
                        title="Digitales Forchheim",
                        data={},
                        options={
                            CONF_SCAN_INTERVAL: self._setup_input[CONF_SCAN_INTERVAL],
                            CONF_STATIONS: self._setup_input[CONF_STATIONS],
                            CONF_WASTE_LOCATION: location.path,
                        },
                    )
        return self.async_show_form(
            step_id="waste",
            data_schema=_waste_schema(self._waste_locations, self._waste_default),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> ForchheimOptionsFlow:
        """Return the options flow."""
        return ForchheimOptionsFlow()


class ForchheimOptionsFlow(OptionsFlow):
    """Manage polling options."""

    def __init__(self) -> None:
        super().__init__()
        self._new_options: dict[str, Any] = {}
        self._waste_locations: list[WasteLocation] | None = None
        self._waste_default: str | None = None
        self._stations: list[Station] | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update the polling interval."""
        if self._stations is None:
            runtime_data = getattr(self.config_entry, "runtime_data", None)
            if runtime_data is not None:
                self._stations = list(runtime_data.data.stations)
            else:
                client = ForchheimApiClient(async_get_clientsession(self.hass))
                try:
                    self._stations = await client.async_get_all_stations()
                except (ForchheimApiError, ForchheimInvalidResponseError):
                    return self.async_abort(reason="cannot_connect")
        errors: dict[str, str] = {}
        if user_input is not None:
            selected = user_input[CONF_STATIONS]
            if not set(selected) <= {station.uid for station in self._stations}:
                errors[CONF_STATIONS] = "invalid_station"
            else:
                self._new_options = {
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    CONF_STATIONS: selected,
                }
                if user_input[CONF_WASTE_ENABLED]:
                    return await self.async_step_waste()
                return self.async_create_entry(data=self._new_options)
        current = int(
            self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        )
        return self.async_show_form(
            step_id="init",
            data_schema=_schema(
                current,
                self._stations,
                self.config_entry.options.get(
                    CONF_STATIONS, [station.uid for station in self._stations]
                ),
                bool(self.config_entry.options.get(CONF_WASTE_LOCATION)),
            ),
            errors=errors,
        )

    async def async_step_waste(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Update the collection area without changing city sensor settings."""
        client = ForchheimApiClient(async_get_clientsession(self.hass))
        if self._waste_locations is None:
            try:
                self._waste_locations = await client.async_get_waste_locations()
            except (ForchheimApiError, ForchheimInvalidResponseError):
                return self.async_abort(reason="waste_unavailable")
            self._waste_default = self.config_entry.options.get(CONF_WASTE_LOCATION)
            if self._waste_default is None:
                try:
                    address = await client.async_reverse_geocode(
                        self.hass.config.latitude, self.hass.config.longitude
                    )
                except ForchheimApiError:
                    address = {}
                suggestions = suggest_waste_locations(self._waste_locations, address)
                if len(suggestions) == 1:
                    self._waste_default = suggestions[0].path
                self._waste_locations = suggestions + [
                    location
                    for location in self._waste_locations
                    if location not in suggestions
                ]
        errors: dict[str, str] = {}
        if user_input is not None:
            path = user_input[CONF_WASTE_LOCATION]
            if not any(location.path == path for location in self._waste_locations):
                errors[CONF_WASTE_LOCATION] = "invalid_location"
            else:
                try:
                    await client.async_get_waste_events(path)
                except (ForchheimApiError, ForchheimInvalidResponseError):
                    errors["base"] = "waste_unavailable"
                else:
                    return self.async_create_entry(
                        data={**self._new_options, CONF_WASTE_LOCATION: path}
                    )
        return self.async_show_form(
            step_id="waste",
            data_schema=_waste_schema(
                self._waste_locations,
                self._waste_default,
            ),
            errors=errors,
        )


def _waste_schema(locations: list[WasteLocation], default: str | None) -> vol.Schema:
    """Return a searchable list of district collection areas."""
    choices = [
        {"value": location.path, "label": location.name} for location in locations
    ]
    key = (
        vol.Required(CONF_WASTE_LOCATION, default=default)
        if default in {location.path for location in locations}
        else vol.Required(CONF_WASTE_LOCATION)
    )
    return vol.Schema(
        {
            key: SelectSelector(
                SelectSelectorConfig(options=choices, mode=SelectSelectorMode.DROPDOWN)
            )
        }
    )
