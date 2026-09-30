"""Response parsers for Forchheim Sensors."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .models import Measurement, Place, Station, TrafficSnapshot


class ForchheimInvalidResponseError(ValueError):
    """Raised when a remote response does not have the expected structure."""


def parse_stations(payload: dict[str, Any], category: str = "weather") -> list[Station]:
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
                category=category,
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


def parse_station_measurements(
    payload: dict[str, Any],
) -> dict[str, dict[str, Measurement]]:
    """Parse one Grafana frame containing measurements for several stations."""
    try:
        frame = payload["results"]["A"]["frames"][0]
        field_names = [field["name"] for field in frame["schema"]["fields"]]
        columns = frame["data"]["values"]
        station_index = field_names.index("DTwin_DTwinID")
        title_index = field_names.index("Datapoint_Title")
        value_index = field_names.index("Event_Value")
        time_index = field_names.index("Event_DateTime")
    except (KeyError, IndexError, TypeError, ValueError) as err:
        raise ForchheimInvalidResponseError(
            "Batch response has an unexpected data-frame layout"
        ) from err

    row_count = len(columns[station_index])
    if any(
        not isinstance(column, list) or len(column) != row_count for column in columns
    ):
        raise ForchheimInvalidResponseError("Batch measurement columns are invalid")

    result: dict[str, dict[str, Measurement]] = {}
    for row in range(row_count):
        station_uid = columns[station_index][row]
        title = columns[title_index][row]
        raw_value = columns[value_index][row]
        raw_time = columns[time_index][row]
        if station_uid is None or title is None or raw_value is None:
            continue
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            continue
        measured_at = _parse_datetime(raw_time)
        result.setdefault(str(station_uid), {})[str(title)] = Measurement(
            value=value, measured_at=measured_at
        )
    if not result:
        raise ForchheimInvalidResponseError("No current station measurements found")
    return result


def _parse_datetime(raw_time: Any) -> datetime | None:
    """Parse a Grafana timestamp."""
    if isinstance(raw_time, (int, float)):
        return datetime.fromtimestamp(raw_time / 1000, tz=UTC)
    if isinstance(raw_time, str):
        try:
            return datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


def _point_coordinates(
    geometry: dict[str, Any] | None,
) -> tuple[float, float] | None:
    """Return the first usable longitude/latitude pair from a geometry."""
    if geometry is None:
        return None
    coordinates = geometry.get("coordinates")
    while isinstance(coordinates, list) and coordinates:
        if (
            len(coordinates) >= 2
            and isinstance(coordinates[0], (int, float))
            and isinstance(coordinates[1], (int, float))
        ):
            return float(coordinates[0]), float(coordinates[1])
        coordinates = coordinates[0]
    return None


def parse_places(payload: dict[str, Any], source: str) -> list[Place]:
    """Parse public GeoJSON features into stable place records."""
    features = payload.get("features")
    if not isinstance(features, list):
        raise ForchheimInvalidResponseError(f"{source} data has no feature list")
    result: list[Place] = []
    for index, feature in enumerate(features):
        properties = feature.get("properties", {})
        point = _point_coordinates(feature.get("geometry", {}))
        if point is None or not isinstance(properties, dict):
            continue
        longitude, latitude = point
        category = str(
            properties.get("art")
            or properties.get("category")
            or properties.get("ebene")
            or source
        )
        name = str(
            properties.get("name")
            or properties.get("beschreibung")
            or properties.get("stop_name")
            or category
        )
        street = properties.get("street") or properties.get("strasse")
        number = properties.get("house_number") or properties.get("hausnr")
        address = " ".join(str(value) for value in (street, number) if value)
        uid = str(
            properties.get("fid")
            or properties.get("id")
            or properties.get("laufnummer")
            or f"{source}_{index}"
        )
        result.append(
            Place(
                uid=f"{source}_{uid}",
                category=category,
                name=name,
                latitude=latitude,
                longitude=longitude,
                address=address or None,
                note=properties.get("bemerkung") or properties.get("description"),
                url=properties.get("http"),
                extra={
                    key: properties[key]
                    for key in ("route_short_name", "route_long_name", "start", "end")
                    if properties.get(key) is not None
                },
            )
        )
    return result


def parse_traffic(payload: dict[str, Any], period: str) -> TrafficSnapshot:
    """Aggregate floating-car GeoJSON values for Home Assistant."""
    features = payload.get("features")
    if not isinstance(features, list):
        raise ForchheimInvalidResponseError("Traffic data has no feature list")
    weighted_speed = 0.0
    observations = 0.0
    cells = 0
    for feature in features:
        properties = feature.get("properties", {})
        try:
            speed = float(properties["speed"])
            count = float(properties["count"])
        except (KeyError, TypeError, ValueError):
            continue
        weighted_speed += speed * count
        observations += count
        cells += 1
    if not cells or observations <= 0:
        raise ForchheimInvalidResponseError("Traffic data contains no values")
    return TrafficSnapshot(
        period=period,
        average_speed=round(weighted_speed / observations, 1),
        observations=round(observations),
        cells=cells,
    )
