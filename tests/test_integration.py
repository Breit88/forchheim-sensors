"""Runtime tests for the Digitales Forchheim integration."""

from datetime import UTC, date, datetime, timedelta
from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.forchheim_sensors import (
    _sync_station_entities,
    async_migrate_entry,
)
from custom_components.forchheim_sensors.const import (
    CITY_UNIQUE_ID,
    CONF_SCAN_INTERVAL,
    CONF_STATIONS,
    CONF_WASTE_ENABLED,
    CONF_WASTE_LOCATION,
    DOMAIN,
)
from custom_components.forchheim_sensors.models import (
    Measurement,
    Station,
    TrafficSnapshot,
    WasteEvent,
)
from custom_components.forchheim_sensors.waste import WasteLocation

STATION = Station(
    uid="19-843",
    name="Schleuseninsel",
    latitude=49.74302,
    longitude=11.04788,
    model="WS-L1200-N",
    category="weather",
)
OTHER_STATION = Station(
    uid="19-844",
    name="Rathausplatz",
    latitude=49.72,
    longitude=11.05,
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
WASTE_PATH = "/Forchheim/Landkreis/Forchheim - Ringstraße"


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
    assert entry.version == 4
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
        assert result["options"][CONF_STATIONS] == [STATION.uid]

        duplicate = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        assert duplicate["type"] is FlowResultType.ABORT
        assert duplicate["reason"] == "already_configured"


async def test_waste_setup_suggests_but_requires_confirmation(
    hass: HomeAssistant,
) -> None:
    """Each HA instance chooses its own collection area in the setup flow."""
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
        patch(
            "custom_components.forchheim_sensors.config_flow."
            "ForchheimApiClient.async_get_waste_locations",
            return_value=[WasteLocation(WASTE_PATH, "Forchheim - Ringstraße")],
        ),
        patch(
            "custom_components.forchheim_sensors.config_flow."
            "ForchheimApiClient.async_reverse_geocode",
            return_value={"city": "Forchheim", "street": "Ringstraße"},
        ),
        patch(
            "custom_components.forchheim_sensors.config_flow."
            "ForchheimApiClient.async_get_waste_events",
            return_value=(WasteEvent(date(2026, 10, 28), "Biotonne"),),
        ),
    ):
        form = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": "user"}
        )
        waste_form = await hass.config_entries.flow.async_configure(
            form["flow_id"],
            {CONF_SCAN_INTERVAL: 300, CONF_WASTE_ENABLED: True},
        )
        assert waste_form["type"] is FlowResultType.FORM
        assert waste_form["step_id"] == "waste"
        result = await hass.config_entries.flow.async_configure(
            form["flow_id"], {CONF_WASTE_LOCATION: WASTE_PATH}
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["options"][CONF_WASTE_LOCATION] == WASTE_PATH
    assert result["options"][CONF_STATIONS] == [STATION.uid]


async def test_options_allow_deselecting_all_stations(hass: HomeAssistant) -> None:
    """Station selection can be changed without reinstalling the integration."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=4,
        unique_id=CITY_UNIQUE_ID,
        data={},
        options={CONF_SCAN_INTERVAL: 300, CONF_STATIONS: [STATION.uid]},
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.forchheim_sensors.config_flow."
        "ForchheimApiClient.async_get_all_stations",
        return_value=[STATION],
    ):
        form = await hass.config_entries.options.async_init(entry.entry_id)
        assert form["type"] is FlowResultType.FORM
        result = await hass.config_entries.options.async_configure(
            form["flow_id"],
            {
                CONF_SCAN_INTERVAL: 600,
                CONF_STATIONS: [],
                CONF_WASTE_ENABLED: False,
            },
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_STATIONS] == []


async def test_entry_setup_creates_citywide_sensors(hass: HomeAssistant) -> None:
    """A citywide entry loads measurement and summary sensor entities."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=3,
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
    assert len(entities) == 19
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

    for entity in entities:
        state = hass.states.get(entity.entity_id)
        assert state is not None
        assert state.attributes["state_class"] == "measurement"

    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_selected_station_and_waste_entities(hass: HomeAssistant) -> None:
    """Only chosen stations are queried; waste entities use the chosen area."""
    next_day = date.today() + timedelta(days=1)
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=4,
        unique_id=CITY_UNIQUE_ID,
        title="Digitales Forchheim",
        data={},
        options={
            CONF_SCAN_INTERVAL: 300,
            CONF_STATIONS: [STATION.uid],
            CONF_WASTE_LOCATION: WASTE_PATH,
        },
    )
    entry.add_to_hass(hass)
    with (
        patch(
            "custom_components.forchheim_sensors.api."
            "ForchheimApiClient.async_get_all_stations",
            return_value=[STATION, OTHER_STATION],
        ),
        patch(
            "custom_components.forchheim_sensors.api."
            "ForchheimApiClient.async_get_station_measurements",
            return_value={STATION.uid: MEASUREMENTS},
        ) as measurement_request,
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
        patch(
            "custom_components.forchheim_sensors.api."
            "ForchheimApiClient.async_get_waste_events",
            return_value=(WasteEvent(next_day, "Biotonne"),),
        ) as waste_request,
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    measurement_request.assert_awaited_once_with([STATION.uid])
    waste_request.assert_awaited_once_with(WASTE_PATH)
    entities = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    assert not any(
        entity.unique_id.startswith(OTHER_STATION.uid) for entity in entities
    )
    assert sum(entity.domain == "calendar" for entity in entities) == 1
    bio = next(entity for entity in entities if entity.unique_id == "waste_bio")
    assert hass.states.get(bio.entity_id).state == next_day.isoformat()
    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_migrate_removes_legacy_charging_entities(hass: HomeAssistant) -> None:
    """The 0.3 migration removes only the former charging entities and devices."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        unique_id=CITY_UNIQUE_ID,
        title="Digitales Forchheim",
        data={},
    )
    entry.add_to_hass(hass)
    entity_registry = er.async_get(hass)
    entity_registry.async_get_or_create(
        "sensor",
        DOMAIN,
        "charging_old_site",
        suggested_object_id="old_charging_site",
        config_entry=entry,
    )
    entity_registry.async_get_or_create(
        "sensor",
        DOMAIN,
        "19-843_temperature",
        suggested_object_id="weather_temperature",
        config_entry=entry,
    )
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, "charging_old_site")},
        name="Old charging site",
    )

    assert await async_migrate_entry(hass, entry)
    assert entry.version == 4
    entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
    assert [entity.unique_id for entity in entities] == ["19-843_temperature"]
    assert not any(
        identifier.startswith("charging_")
        for device in dr.async_entries_for_config_entry(device_registry, entry.entry_id)
        for domain, identifier in device.identifiers
        if domain == DOMAIN
    )


async def test_station_choice_preserves_entity_id(hass: HomeAssistant) -> None:
    """Deselecting hides a station; reselecting restores its registered ID."""
    entry = MockConfigEntry(domain=DOMAIN, version=4, unique_id=CITY_UNIQUE_ID)
    entry.add_to_hass(hass)
    registry = er.async_get(hass)
    entity = registry.async_get_or_create(
        "sensor",
        DOMAIN,
        "19-843_temperature",
        suggested_object_id="schleuseninsel_temperature",
        config_entry=entry,
    )
    _sync_station_entities(hass, entry, set())
    assert (
        registry.async_get(entity.entity_id).disabled_by
        is er.RegistryEntryDisabler.INTEGRATION
    )
    _sync_station_entities(hass, entry, {STATION.uid})
    assert registry.async_get(entity.entity_id).disabled_by is None
