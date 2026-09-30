"""Runtime tests for the Forchheim Sensors integration."""

from datetime import UTC, datetime
from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.forchheim_sensors.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_SCAN_INTERVAL,
    CONF_STATION,
    CONF_STATION_NAME,
    DOMAIN,
)
from custom_components.forchheim_sensors.models import Measurement, Station

STATION = Station(
    uid="19-843",
    name="Schleuseninsel",
    latitude=49.74302,
    longitude=11.04788,
    model="WS-L1200-N",
)
MEASUREMENTS = {
    "Temperatur": Measurement(21.5, datetime(2026, 9, 30, 12, tzinfo=UTC)),
    "Luftfeuchtigkeit (rel.)": Measurement(58.0, None),
    "Luftdruck": Measurement(1007.2, None),
    "Windgeschwindigkeit": Measurement(1.4, None),
    "Windrichtung": Measurement(143.0, None),
    "Taupunkt": Measurement(12.8, None),
    "Niederschlag pro h": Measurement(0.0, None),
}


async def test_config_flow_and_duplicate_protection(hass: HomeAssistant) -> None:
    """The UI flow discovers, validates, and uniquely stores a station."""
    with (
        patch(
            "custom_components.forchheim_sensors.config_flow."
            "ForchheimApiClient.async_get_stations",
            return_value=[STATION],
        ),
        patch(
            "custom_components.forchheim_sensors.config_flow."
            "ForchheimApiClient.async_get_measurements",
            return_value=MEASUREMENTS,
        ),
    ):
        form = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        assert form["type"] is FlowResultType.FORM

        result = await hass.config_entries.flow.async_configure(
            form["flow_id"],
            {CONF_STATION: STATION.uid, CONF_SCAN_INTERVAL: 300},
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["data"][CONF_STATION] == STATION.uid
        assert result["options"][CONF_SCAN_INTERVAL] == 300

        duplicate = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        duplicate = await hass.config_entries.flow.async_configure(
            duplicate["flow_id"],
            {CONF_STATION: STATION.uid, CONF_SCAN_INTERVAL: 300},
        )
        assert duplicate["type"] is FlowResultType.ABORT
        assert duplicate["reason"] == "already_configured"


async def test_entry_setup_creates_all_sensors(hass: HomeAssistant) -> None:
    """A configured station loads and creates all seven sensor entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=STATION.uid,
        title="Forchheim – Schleuseninsel",
        data={
            CONF_STATION: STATION.uid,
            CONF_STATION_NAME: STATION.name,
            CONF_LATITUDE: STATION.latitude,
            CONF_LONGITUDE: STATION.longitude,
        },
        options={CONF_SCAN_INTERVAL: 300},
    )
    entry.add_to_hass(hass)

    with patch(
        "custom_components.forchheim_sensors.api."
        "ForchheimApiClient.async_get_measurements",
        return_value=MEASUREMENTS,
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    registry = er.async_get(hass)
    entities = er.async_entries_for_config_entry(registry, entry.entry_id)
    assert len(entities) == 7
    assert {entity.domain for entity in entities} == {"sensor"}
    assert all(hass.states.get(entity.entity_id) is not None for entity in entities)

    temperature = next(
        entity for entity in entities if entity.unique_id.endswith("temperature")
    )
    state = hass.states.get(temperature.entity_id)
    assert state is not None
    assert state.state == "21.5"
    assert state.attributes["unit_of_measurement"] == "°C"
    assert state.attributes["station"] == STATION.name

    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state is ConfigEntryState.NOT_LOADED
