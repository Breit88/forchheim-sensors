"""Response parsers for Forchheim Sensors."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .models import Measurement, Station


class ForchheimInvalidResponseError(ValueError):
    """Raised when a remote response does not have the expected structure."""


def parse_stations(payload: dict[str, Any]) -> list[Station]:
    """Parse the GeoJSON station list returned by the digital twin."""
    stations: list[Station] = []
    try:
        features = payload["features"]
    except (KeyError, TypeError) as err:
        raise ForchheimInvalidResponseError("Station list has no features") from err

    if not isinstance(features, list):
        raise ForchheimInvalidResponseError("Station features are not a list")

    for feature in features:
        try:
            properties = feature["properties"]
            longitude, latitude = feature["geometry"]["coordinates"][:2]
            uid = properties["Things/0/properties/thingUID"]
            name = properties["Things/0/name"]
        except (KeyError, TypeError, ValueError) as err:
            raise ForchheimInvalidResponseError(
                "A station is missing required fields"
            ) from err

        stations.append(
            Station(
                uid=str(uid),
                name=str(name),
                latitude=float(latitude),
                longitude=float(longitude),
                model=properties.get("Things/0/properties/sensordata/sensorName"),
            )
        )

    if not stations:
        raise ForchheimInvalidResponseError("No active weather stations found")
    return stations


def parse_measurements(payload: dict[str, Any]) -> dict[str, Measurement]:
    """Parse Grafana data frames into measurements keyed by source title."""
    try:
        frames = payload["results"]["A"]["frames"]
        frame = frames[0]
        field_names = [field["name"] for field in frame["schema"]["fields"]]
        columns = frame["data"]["values"]
        title_index = field_names.index("Datapoint_Title")
        value_index = field_names.index("Event_Value")
        time_index = field_names.index("Event_DateTime")
    except (KeyError, IndexError, TypeError, ValueError) as err:
        raise ForchheimInvalidResponseError(
            "Measurement response has an unexpected data-frame layout"
        ) from err

    if not columns or any(not isinstance(column, list) for column in columns):
        raise ForchheimInvalidResponseError("Measurement columns are invalid")

    row_count = len(columns[title_index])
    if any(len(column) != row_count for column in columns):
        raise ForchheimInvalidResponseError("Measurement columns have unequal lengths")

    result: dict[str, Measurement] = {}
    for row in range(row_count):
        title = columns[title_index][row]
        raw_value = columns[value_index][row]
        raw_time = columns[time_index][row]
        if title is None or raw_value is None:
            continue

        measured_at: datetime | None = None
        if isinstance(raw_time, (int, float)):
            measured_at = datetime.fromtimestamp(raw_time / 1000, tz=UTC)
        elif isinstance(raw_time, str):
            try:
                measured_at = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
            except ValueError:
                measured_at = None

        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            continue
        result[str(title)] = Measurement(value=value, measured_at=measured_at)

    if not result:
        raise ForchheimInvalidResponseError("No current measurements found")
    return result
