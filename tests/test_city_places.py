"""Forchheim-wide place selection and map entities."""

from dataclasses import replace
from unittest.mock import MagicMock, patch

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.forchheim_sensors.api import ForchheimApiClient
from custom_components.forchheim_sensors.const import (
    CITY_UNIQUE_ID,
    CONSTRUCTION_URL,
    DOMAIN,
    ORTSINFO_URL,
    PLAYGROUNDS_URL,
    TRANSIT_URLS,
)
from custom_components.forchheim_sensors.geography import is_in_forchheim
from custom_components.forchheim_sensors.models import Place, TrafficSnapshot

CITY = (11.06, 49.72)
OUTSIDE = (11.005, 49.59)


def _point(name: str, coordinates: tuple[float, float], art: str) -> dict:
    return {
        "type": "Feature",
        "properties": {"name": name, "stop_name": name, "art": art},
        "geometry": {"type": "Point", "coordinates": list(coordinates)},
    }


async def test_public_feeds_keep_all_city_places_and_exclude_region() -> None:
    """A nearby home address cannot narrow the public citywide feeds."""
    assert is_in_forchheim(CITY[1], CITY[0])
    assert not is_in_forchheim(OUTSIDE[1], OUTSIDE[0])
    client = ForchheimApiClient(MagicMock())
    replies = {
        ORTSINFO_URL: {"features": []},
        PLAYGROUNDS_URL: {
            "features": [
                _point("Stadtpark", CITY, "playground"),
                _point("Anderer Ort", OUTSIDE, "playground"),
            ]
        },
        TRANSIT_URLS["bus"]: {
            "features": [
                _point("Paradeplatz", CITY, "BUS"),
                _point("Erlangen", OUTSIDE, "BUS"),
            ]
        },
        TRANSIT_URLS["rail"]: {"features": []},
        TRANSIT_URLS["sbahn"]: {"features": []},
        CONSTRUCTION_URL: {
            "features": [
                _point("Sperrung", CITY, "construction"),
                _point("Andere Sperrung", OUTSIDE, "construction"),
            ]
        },
    }

    async def request(method: str, url: str, **kwargs: object) -> dict:
        return replies[url]

    with patch.object(client, "_async_request_json", side_effect=request):
        _, playgrounds, transit = await client.async_get_public_places()
        construction = await client.async_get_construction_sites()
    assert [place.name for place in playgrounds] == ["Stadtpark"]
    assert [place.name for place in transit] == ["Paradeplatz"]
    assert [place.name for place in construction] == ["Sperrung"]


async def test_all_city_places_appear_on_map_and_in_summary(
    hass: HomeAssistant,
) -> None:
    """All available city places appear even when home is elsewhere."""
    hass.config.latitude = OUTSIDE[1]
    hass.config.longitude = OUTSIDE[0]
    bus = Place("bus_1", "BUS", "Paradeplatz", CITY[1], CITY[0])
    playground = Place("play_1", "playground", "Stadtpark", CITY[1], CITY[0])
    construction = [
        Place(
            f"build_{number}",
            "construction",
            f"Sperrung {number}",
            CITY[1] + number / 100000,
            CITY[0],
        )
        for number in range(25)
    ]
    entry = MockConfigEntry(domain=DOMAIN, version=4, unique_id=CITY_UNIQUE_ID)
    entry.add_to_hass(hass)
    with (
        patch(
            "custom_components.forchheim_sensors.api."
            "ForchheimApiClient.async_get_all_stations",
            return_value=[],
        ),
        patch(
            "custom_components.forchheim_sensors.api."
            "ForchheimApiClient.async_get_public_places",
            return_value=([], [playground], [bus]),
        ),
        patch(
            "custom_components.forchheim_sensors.api."
            "ForchheimApiClient.async_get_construction_sites",
            return_value=construction,
        ),
        patch(
            "custom_components.forchheim_sensors.api."
            "ForchheimApiClient.async_get_traffic",
            return_value=TrafficSnapshot("werktag_10-15", 30, 10, 1),
        ),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    points = hass.states.async_all("geo_location")
    assert len(points) == 27
    assert {state.attributes["source"] for state in points} == {
        "forchheim_sensors_bus",
        "forchheim_sensors_playground",
        "forchheim_sensors_construction",
    }
    entities = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    bus_count = next(e for e in entities if e.unique_id == "city_bus_stop_count")
    assert hass.states.get(bus_count.entity_id).state == "1"
    assert hass.states.get(bus_count.entity_id).attributes["stops"] == ["Paradeplatz"]
    playground_count = next(
        e for e in entities if e.unique_id == "city_playground_count"
    )
    assert hass.states.get(playground_count.entity_id).attributes["sites"] == [
        "Stadtpark"
    ]
    construction_count = next(
        e for e in entities if e.unique_id == "city_construction_count"
    )
    assert len(hass.states.get(construction_count.entity_id).attributes["sites"]) == 25

    entry.runtime_data.async_set_updated_data(
        replace(entry.runtime_data.data, construction_sites=())
    )
    await hass.async_block_till_done()
    assert {
        state.attributes["source"] for state in hass.states.async_all("geo_location")
    } == {
        "forchheim_sensors_bus",
        "forchheim_sensors_playground",
    }
    assert await hass.config_entries.async_unload(entry.entry_id)
