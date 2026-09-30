"""Data models for Forchheim Sensors."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class Station:
    """A public Forchheim measurement station."""

    uid: str
    name: str
    latitude: float
    longitude: float
    model: str | None = None
    category: str = "weather"


@dataclass(frozen=True, slots=True)
class Measurement:
    """A current sensor measurement."""

    value: float
    measured_at: datetime | None


@dataclass(frozen=True, slots=True)
class Place:
    """A public place from a Forchheim GeoJSON data set."""

    uid: str
    category: str
    name: str
    latitude: float
    longitude: float
    address: str | None = None
    note: str | None = None
    url: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TrafficSnapshot:
    """Aggregated floating-car data for one time period."""

    period: str
    average_speed: float
    observations: int
    cells: int


@dataclass(frozen=True, slots=True)
class CityData:
    """All public Forchheim data used by the integration."""

    stations: tuple[Station, ...]
    measurements: dict[str, dict[str, Measurement]]
    charging_sites: tuple[Place, ...]
    places: tuple[Place, ...]
    playgrounds: tuple[Place, ...]
    transit_stops: tuple[Place, ...]
    construction_sites: tuple[Place, ...]
    traffic: TrafficSnapshot
