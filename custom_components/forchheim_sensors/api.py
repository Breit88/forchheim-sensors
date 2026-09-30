"""Async API client for the public Forchheim data services."""

from __future__ import annotations

import asyncio
import re
import time
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import (
    CONSTRUCTION_URL,
    GRAFANA_QUERY_URL,
    LOCATIONS_URL,
    ORTSINFO_URL,
    PLAYGROUNDS_URL,
    STATION_CATEGORIES,
    TENANT_UID,
    TRAFFIC_BASE_URL,
    TRANSIT_URLS,
)
from .models import Measurement, Place, Station, TrafficSnapshot
from .parser import (
    parse_places,
    parse_station_measurements,
    parse_stations,
    parse_traffic,
)

_STATION_UID_PATTERN = re.compile(r"^[0-9]+-[0-9]+$")


class ForchheimApiError(Exception):
    """Base error raised by the Forchheim API client."""


class ForchheimConnectionError(ForchheimApiError):
    """Raised when a public endpoint cannot be reached."""


class ForchheimApiClient:
    """Client for public Forchheim GeoJSON and Grafana endpoints."""

    def __init__(self, session: ClientSession) -> None:
        """Initialize the client with Home Assistant's shared session."""
        self._session = session
        self._cache: dict[str, tuple[float, Any]] = {}

    async def async_get_stations(self, category: str = "weather") -> list[Station]:
        """Return active public stations from one sensor category."""
        description = STATION_CATEGORIES[category]
        params = {
            "$resultFormat": "GeoJSON",
            "$filter": (
                f"description eq '{description}' and "
                f"properties/tenantUID eq '{TENANT_UID}' and "
                "properties/deletedFlag eq 'False' and "
                "properties/activeFlag eq 'True'"
            ),
            "$expand": "Things",
        }
        payload = await self._async_request_json("GET", LOCATIONS_URL, params=params)
        return parse_stations(payload, category)

    async def async_get_all_stations(self) -> list[Station]:
        """Return all weather, climate, and road stations."""
        cached = self._get_cached("stations", 21_600)
        if cached is not None:
            return cached
        groups = await asyncio.gather(
            *(self.async_get_stations(category) for category in STATION_CATEGORIES)
        )
        stations = [station for group in groups for station in group]
        self._set_cached("stations", stations)
        return stations

    async def async_get_measurements(self, station_uid: str) -> dict[str, Measurement]:
        """Return the latest measurements for one station."""
        result = await self.async_get_station_measurements([station_uid])
        return result.get(station_uid, {})

    async def async_get_station_measurements(
        self, station_uids: list[str]
    ) -> dict[str, dict[str, Measurement]]:
        """Return latest values for several stations in one request."""
        if not station_uids or any(
            not _STATION_UID_PATTERN.fullmatch(uid) for uid in station_uids
        ):
            raise ForchheimApiError("Invalid station identifier")
        uid_list = ", ".join(f'"{uid}"' for uid in station_uids)
        query = (
            "fact_events_niotix_fullview(2)\n"
            f"| where DTwin_DTwinID in~ ({uid_list})\n"
            "| summarize arg_max(Event_DateTime, *) "
            "by DTwin_DTwinID, Datapoint_Title\n"
            "| project DTwin_DTwinID, Datapoint_Title, Event_Value, "
            "Event_DateTime\n"
            "| order by DTwin_DTwinID asc, Datapoint_Title asc"
        )
        payload = await self._async_grafana_query(query)
        return parse_station_measurements(payload)

    async def async_get_public_places(
        self,
    ) -> tuple[list[Place], list[Place], list[Place]]:
        """Return civic places, playgrounds, and public transport stops."""
        cached = self._get_cached("places", 21_600)
        if cached is not None:
            return cached
        payloads = await asyncio.gather(
            self._async_request_json("GET", ORTSINFO_URL),
            self._async_request_json("GET", PLAYGROUNDS_URL),
            *(self._async_request_json("GET", url) for url in TRANSIT_URLS.values()),
        )
        places = parse_places(payloads[0], "place")
        playgrounds = parse_places(payloads[1], "playground")
        transit: list[Place] = []
        for source, payload in zip(TRANSIT_URLS, payloads[2:], strict=True):
            transit.extend(parse_places(payload, source))
        result = (places, playgrounds, transit)
        self._set_cached("places", result)
        return result

    async def async_get_construction_sites(self) -> list[Place]:
        """Return current road and utility construction sites."""
        cached = self._get_cached("construction", 900)
        if cached is not None:
            return cached
        payload = await self._async_request_json("GET", CONSTRUCTION_URL)
        result = parse_places(payload, "construction")
        self._set_cached("construction", result)
        return result

    async def async_get_traffic(self, weekend: bool, hour: int) -> TrafficSnapshot:
        """Return the matching citywide floating-car traffic profile."""
        day = "wochenende" if weekend else "werktag"
        slot = next(
            name
            for start, end, name in (
                (0, 6, "0-6"),
                (6, 10, "6-10"),
                (10, 15, "10-15"),
                (15, 19, "15-19"),
                (19, 24, "19-24"),
            )
            if start <= hour < end
        )
        period = f"{day}_{slot}"
        cached = self._get_cached(period, 21_600)
        if cached is not None:
            return cached
        url = f"{TRAFFIC_BASE_URL}/{period}.geojson"
        payload = await self._async_request_json("GET", url)
        result = parse_traffic(payload, period)
        self._set_cached(period, result)
        return result

    async def _async_grafana_query(self, query: str) -> dict[str, Any]:
        """Execute one public Grafana KQL query."""
        now_ms = int(time.time() * 1000)
        request = {
            "queries": [
                {
                    "refId": "A",
                    "datasource": {
                        "type": "grafana-azure-data-explorer-datasource",
                        "uid": "BSsVoLa4z",
                    },
                    "database": "sds_core_silver",
                    "query": query,
                    "querySource": "raw",
                    "queryType": "KQL",
                    "rawMode": True,
                    "resultFormat": "table",
                }
            ],
            "from": str(now_ms - 86_400_000),
            "to": str(now_ms),
        }
        return await self._async_request_json("POST", GRAFANA_QUERY_URL, json=request)

    def _get_cached(self, key: str, max_age: int) -> Any | None:
        """Return a cached value if it is still fresh."""
        cached = self._cache.get(key)
        if cached is None or time.monotonic() - cached[0] > max_age:
            return None
        return cached[1]

    def _set_cached(self, key: str, value: Any) -> None:
        """Store a value in the in-memory cache."""
        self._cache[key] = (time.monotonic(), value)

    async def _async_request_json(
        self, method: str, url: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Request and validate one JSON object."""
        try:
            async with self._session.request(
                method, url, timeout=30, **kwargs
            ) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (ClientError, TimeoutError, ValueError) as err:
            raise ForchheimConnectionError(str(err)) from err
        if not isinstance(payload, dict):
            raise ForchheimConnectionError("Endpoint did not return a JSON object")
        return payload
