"""Runtime tests for the Digitales Forchheim integration."""

from datetime import UTC, datetime
from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.forchheim_sensors import async_migrate_entry
from custom_components.forchheim_sensors.const import (
    CITY_UNIQUE_ID,
    CONF_SCAN_INTERVAL,
    DOMAIN,
)
from custom_components.forchheim_sensors.models import (
    Measurement,
    Station,
    TrafficSnapshot,
)

STATION = Station(
    uid="19-843",
    name="Schleuseninsel",
    latitude=49.74302,
    longitude=11.04788,
    model="WS-L1200-N",
    category="weather",
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
TRAFFIC = TrafficSnapshot("werktag_10-15", 31.2, 1234, 42)


async def test_migrate_single_station_entry(hass: HomeAssistant) -> None:
    """A 0.1.x station entry becomes the single citywide entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=1,
        unique_id=STATION.uid,
        title="Forchheim – Schleuseninsel",
        data={"station": STATION.uid},
    )
    entry.add_to_hass(hass)
    assert await async_migrate_entry(hass, entry)
    assert entry.version == 2
    assert entry.unique_id == CITY_UNIQUE_ID
    assert entry.title == "Digitales Forchheim"
    assert dict(entry.data) == {}


async def test_config_flow_and_duplicate_protection(hass: HomeAssistant) -> None:
    """The UI flow validates the sources and creates one citywide entry."""
    with (
        patch(
            "custom_components.forchheim_sensors.config_flow."
            "ForchheimApiClient.async_get_all_stations",
            return_value=[STATION],
        ),
        patch(
            "custom_components.forchheim_sensors.config_flow."
            "ForchheimApiClient.async_get_station_measurements",
            return_value={STATION.uid: MEASUREMENTS},
        ),
    ):
        form = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        assert form["type"] is FlowResultType.FORM

        result = await hass.config_entries.flow.async_configure(
            form["flow_id"], {CONF_SCAN_INTERVAL: 300}
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["title"] == "Digitales Forchheim"
        assert result["options"][CONF_SCAN_INTERVAL] == 300

        duplicate = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        assert duplicate["type"] is FlowResultType.ABORT
        assert duplicate["reason"] == "already_configured"


async def test_entry_setup_creates_citywide_sensors(hass: HomeAssistant) -> None:
    """A citywide entry loads measurement and summary sensor entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id=CITY_UNIQUE_ID,
        title="Digitales Forchheim",
        data={},
        options={CONF_SCAN_INTERVAL: 300},
    )
    entry.add_to_hass(hass)

    with (
        patch(
            "custom_components.forchheim_sensors.api."
            "ForchheimApiClient.async_get_all_stations",
            return_value=[STATION],
        ),
        patch(
            "custom_components.forchheim_sensors.api."
            "ForchheimApiClient.async_get_station_measurements",
            return_value={STATION.uid: MEASUREMENTS},
        ),
        patch(
            "custom_components.forchheim_sensors.api."
            "ForchheimApiClient.async_get_public_places",
            return_value=([], [], []),
        ),
        patch(
            "custom_components.forchheim_sensors.api."
            "ForchheimApiClient.async_get_construction_sites",
            return_value=[],
        ),
        patch(
            "custom_components.forchheim_sensors.api."
            "ForchheimApiClient.async_get_traffic",
            return_value=TRAFFIC,
        ),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    registry = er.async_get(hass)
    entities = er.async_entries_for_config_entry(registry, entry.entry_id)
    assert len(entities) == 21
    assert {entity.domain for entity in entities} == {"sensor"}

    temperature = next(
        entity for entity in entities if entity.unique_id == "19-843_temperature"
    )
    state = hass.states.get(temperature.entity_id)
    assert state is not None
    assert state.state == "21.5"
    assert state.attributes["unit_of_measurement"] == "°C"
    assert state.attributes["station"] == STATION.name

    traffic = next(
        entity
        for entity in entities
        if entity.unique_id == "city_traffic_average_speed"
    )
    traffic_state = hass.states.get(traffic.entity_id)
    assert traffic_state is not None
    assert traffic_state.state == "31.2"

    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state is ConfigEntryState.NOT_LOADED
