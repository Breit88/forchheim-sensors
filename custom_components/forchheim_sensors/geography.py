"""Check whether a public location belongs to the city of Forchheim."""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

from .forchheim_boundary import BOUNDARY

_MIN_LONGITUDE = 10.9995754
_MAX_LONGITUDE = 11.1266269
_MIN_LATITUDE = 49.6738465
_MAX_LATITUDE = 49.7508951


def is_in_forchheim(latitude: float, longitude: float) -> bool:
    """Return whether a point lies inside the official city boundary."""
    if not (
        _MIN_LATITUDE <= latitude <= _MAX_LATITUDE
        and _MIN_LONGITUDE <= longitude <= _MAX_LONGITUDE
    ):
        return False

    inside = False
    for (first_lon, first_lat), (next_lon, next_lat) in zip(
        BOUNDARY, BOUNDARY[1:], strict=False
    ):
        if (first_lat > latitude) != (next_lat > latitude) and longitude < (
            (next_lon - first_lon) * (latitude - first_lat) / (next_lat - first_lat)
            + first_lon
        ):
            inside = not inside
    return inside


def distance_km(
    latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float
) -> float:
    """Calculate the great-circle distance between two locations."""
    radius = 6371.0
    lat_a = radians(latitude_a)
    lat_b = radians(latitude_b)
    delta_lat = radians(latitude_b - latitude_a)
    delta_lon = radians(longitude_b - longitude_a)
    value = sin(delta_lat / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(delta_lon / 2) ** 2
    return 2 * radius * asin(sqrt(value))
