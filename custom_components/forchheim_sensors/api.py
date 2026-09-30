"""Async API client for the public Forchheim sensor services."""

from __future__ import annotations

import re
import time
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import GRAFANA_QUERY_URL, LOCATIONS_URL, TENANT_UID
from .models import Measurement, Station
from .parser import parse_measurements, parse_stations

_STATION_UID_PATTERN = re.compile(r"^[0-9]+-[0-9]+$")


class ForchheimApiError(Exception):
    """Base error raised by the Forchheim API client."""


class ForchheimConnectionError(ForchheimApiError):
    """Raised when a public endpoint cannot be reached."""


class ForchheimApiClient:
    """Client for the public Forchheim GeoJSON and Grafana endpoints."""

    def __init__(self, session: ClientSession) -> None:
        """Initialize the client with Home Assistant's shared session."""
        self._session = session

    async def async_get_stations(self) -> list[Station]:
        """Return all active public Forchheim weather stations."""
        params = {
            "$resultFormat": "GeoJSON",
            "$filter": (
                "description eq 'Wetterstation_Forchheim' and "
                f"properties/tenantUID eq '{TENANT_UID}' and "
                "properties/deletedFlag eq 'False' and "
                "properties/activeFlag eq 'True'"
            ),
            "$expand": "Things",
        }
        payload = await self._async_request_json("GET", LOCATIONS_URL, params=params)
        return parse_stations(payload)

    async def async_get_measurements(self, station_uid: str) -> dict[str, Measurement]:
        """Return the latest measurements for one station."""
        if not _STATION_UID_PATTERN.fullmatch(station_uid):
            raise ForchheimApiError("Invalid station identifier")

        query = (
            "fact_events_niotix_fullview(2)\n"
            f'| where DTwin_DTwinID =~ "{station_uid}"\n'
            "| summarize arg_max(Event_DateTime, *) by Datapoint_Title\n"
            "| project Datapoint_Title, Event_Value, Event_DateTime\n"
            "| order by Datapoint_Title asc"
        )
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
        payload = await self._async_request_json(
            "POST", GRAFANA_QUERY_URL, json=request
        )
        return parse_measurements(payload)

    async def _async_request_json(
        self, method: str, url: str, **kwargs: Any
    ) -> dict[str, Any]:
        """Request and validate one JSON object."""
        try:
            async with self._session.request(
                method, url, timeout=20, **kwargs
            ) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (ClientError, TimeoutError, ValueError) as err:
            raise ForchheimConnectionError(str(err)) from err
        if not isinstance(payload, dict):
            raise ForchheimConnectionError("Endpoint did not return a JSON object")
        return payload
