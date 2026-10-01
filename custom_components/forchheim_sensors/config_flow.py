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
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)

from .api import ForchheimApiClient, ForchheimApiError
from .const import (
    CITY_UNIQUE_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from .parser import ForchheimInvalidResponseError


def _schema(default: int) -> vol.Schema:
    """Return the shared polling interval schema."""
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
            )
        }
    )


class ForchheimSensorsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the Forchheim Sensors config flow."""

    VERSION = 3

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Set up all public Forchheim data with one form."""
        await self.async_set_unique_id(CITY_UNIQUE_ID)
        self._abort_if_unique_id_configured()
        errors: dict[str, str] = {}
        if user_input is not None:
            client = ForchheimApiClient(async_get_clientsession(self.hass))
            try:
                stations = await client.async_get_all_stations()
                await client.async_get_station_measurements(
                    [station.uid for station in stations]
                )
            except ForchheimApiError:
                errors["base"] = "cannot_connect"
            except ForchheimInvalidResponseError:
                errors["base"] = "invalid_response"
            else:
                return self.async_create_entry(
                    title="Digitales Forchheim",
                    data={},
                    options={CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL]},
                )
        return self.async_show_form(
            step_id="user",
            data_schema=_schema(DEFAULT_SCAN_INTERVAL),
            errors=errors,
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
        return self.async_show_form(step_id="init", data_schema=_schema(current))
