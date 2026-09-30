"""Data models for Forchheim Sensors."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Station:
    """A public Forchheim weather station."""

    uid: str
    name: str
    latitude: float
    longitude: float
    model: str | None = None


@dataclass(frozen=True, slots=True)
class Measurement:
    """A current sensor measurement."""

    value: float
    measured_at: datetime | None
