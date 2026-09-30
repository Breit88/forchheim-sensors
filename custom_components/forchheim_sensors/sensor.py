"""Sensor platform for Forchheim Sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    DEGREE,
    PERCENTAGE,
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfVolumetricFlux,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import ForchheimConfigEntry
from .const import DOMAIN, GRAFANA_DASHBOARDS, TENANT_UID
from .coordinator import ForchheimDataUpdateCoordinator
from .models import CityData, Place, Station

PARALLEL_UPDATES = 0
ATTRIBUTION = "Daten: Stadt Forchheim / Smart Data Services"


@dataclass(frozen=True, kw_only=True)
class ForchheimSensorEntityDescription(SensorEntityDescription):
    """Describe a Forchheim measurement."""

    source_key: str
    categories: tuple[str, ...]


SENSORS: tuple[ForchheimSensorEntityDescription, ...] = (
    ForchheimSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        source_key="Temperatur",
        categories=("weather", "temperature", "road"),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        source_key="Luftfeuchtigkeit (rel.)",
        categories=("weather", "temperature", "road"),
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="pressure",
        translation_key="pressure",
        source_key="Luftdruck",
        categories=("weather",),
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        native_unit_of_measurement=UnitOfPressure.HPA,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="wind_speed",
        translation_key="wind_speed",
        source_key="Windgeschwindigkeit",
        categories=("weather",),
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="wind_direction",
        translation_key="wind_direction",
        source_key="Windrichtung",
        categories=("weather",),
        icon="mdi:compass-outline",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="dew_point",
        translation_key="dew_point",
        source_key="Taupunkt",
        categories=("weather", "road"),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="precipitation_hour",
        translation_key="precipitation_hour",
        source_key="Niederschlag pro h",
        categories=("weather",),
        device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
        native_unit_of_measurement=UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="battery",
        translation_key="battery",
        source_key="Batterielevel",
        categories=("temperature",),
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    ForchheimSensorEntityDescription(
        key="surface_temperature",
        translation_key="surface_temperature",
        source_key="Oberflächentemperatur",
        categories=("road",),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="battery_voltage",
        translation_key="battery_voltage",
        source_key="Batteriespannung",
        categories=("road",),
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
)


def _distance_km(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    """Calculate great-circle distance between two positions."""
    radius = 6371.0
    lat_a = radians(latitude_a)
    lat_b = radians(latitude_b)
    delta_lat = radians(latitude_b - latitude_a)
    delta_lon = radians(longitude_b - longitude_a)
    value = sin(delta_lat / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(delta_lon / 2) ** 2
    return 2 * radius * asin(sqrt(value))


def _nearest(
    data: tuple[Place, ...], latitude: float, longitude: float
) -> Place | None:
    """Return the nearest place to Home Assistant's home location."""
    return min(
        data,
        key=lambda place: _distance_km(
            latitude, longitude, place.latitude, place.longitude
        ),
        default=None,
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ForchheimConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up all public Forchheim sensor entities."""
    coordinator = entry.runtime_data
    data = coordinator.data
    entities: list[SensorEntity] = []
    for station in data.stations:
        entities.extend(
            ForchheimMeasurementSensor(coordinator, station, description)
            for description in SENSORS
            if station.category in description.categories
        )
    entities.extend(
        ForchheimChargingSensor(
            coordinator, place, hass.config.latitude, hass.config.longitude
        )
        for place in data.charging_sites
    )
    entities.extend(
        _summary_entities(coordinator, hass.config.latitude, hass.config.longitude)
    )
    async_add_entities(entities)


class ForchheimMeasurementSensor(
    CoordinatorEntity[ForchheimDataUpdateCoordinator], SensorEntity
):
    """A measurement from a public Forchheim station."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    entity_description: ForchheimSensorEntityDescription

    def __init__(
        self,
        coordinator: ForchheimDataUpdateCoordinator,
        station: Station,
        description: ForchheimSensorEntityDescription,
    ) -> None:
        """Initialize a measurement sensor."""
        super().__init__(coordinator)
        self.station = station
        self.entity_description = description
        self._attr_unique_id = f"{station.uid}_{description.key}"
        dashboard = GRAFANA_DASHBOARDS[station.category]
        dashboard_url = (
            f"https://dashboard-public.sds.community/grafana/d/{dashboard}"
            f"?var-varTenant={TENANT_UID}&var-varSensor={station.uid}&orgId=2&kiosk=1"
        )
        category_names = {
            "weather": "Wetterstation",
            "temperature": "Klimasensor",
            "road": "Fahrbahnsensor",
        }
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, station.uid)},
            name=f"{category_names[station.category]} {station.name}",
            manufacturer="Stadt Forchheim / Smart Data Services",
            model=station.model or category_names[station.category],
            configuration_url=dashboard_url,
        )

    @property
    def available(self) -> bool:
        """Return whether this measurement is available."""
        return super().available and self.entity_description.source_key in (
            self.coordinator.data.measurements.get(self.station.uid, {})
        )

    @property
    def native_value(self) -> float | None:
        """Return the current measurement."""
        measurement = self.coordinator.data.measurements.get(self.station.uid, {}).get(
            self.entity_description.source_key
        )
        return measurement.value if measurement else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return station and source metadata."""
        measurement = self.coordinator.data.measurements.get(self.station.uid, {}).get(
            self.entity_description.source_key
        )
        return {
            "measurement_time": (
                measurement.measured_at.isoformat()
                if measurement and measurement.measured_at
                else None
            ),
            "station": self.station.name,
            "station_type": self.station.category,
            "latitude": self.station.latitude,
            "longitude": self.station.longitude,
        }


class ForchheimChargingSensor(
    CoordinatorEntity[ForchheimDataUpdateCoordinator], SensorEntity
):
    """Distance and metadata for one public charging site."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION
    _attr_device_class = SensorDeviceClass.DISTANCE
    _attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator: ForchheimDataUpdateCoordinator,
        place: Place,
        home_latitude: float,
        home_longitude: float,
    ) -> None:
        """Initialize a charging-site sensor."""
        super().__init__(coordinator)
        self.place_uid = place.uid
        self.home_latitude = home_latitude
        self.home_longitude = home_longitude
        self._attr_unique_id = f"charging_{place.uid}"
        self._attr_name = "Entfernung"
        self._attr_icon = (
            "mdi:bicycle-electric" if "E-Bike" in place.category else "mdi:ev-station"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"charging_{place.uid}")},
            name=f"{place.category} {place.address or place.name}",
            manufacturer="Stadt Forchheim",
            model="Öffentliche Ladestation",
            configuration_url="https://dz.forchheim.de/",
        )

    @property
    def place(self) -> Place | None:
        """Return the current place record."""
        return next(
            (
                place
                for place in self.coordinator.data.charging_sites
                if place.uid == self.place_uid
            ),
            None,
        )

    @property
    def available(self) -> bool:
        """Return whether the charging site still exists in the source."""
        return super().available and self.place is not None

    @property
    def native_value(self) -> float | None:
        """Return distance from home in kilometres."""
        if (place := self.place) is None:
            return None
        return round(
            _distance_km(
                self.home_latitude,
                self.home_longitude,
                place.latitude,
                place.longitude,
            ),
            2,
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return charging-site metadata."""
        if (place := self.place) is None:
            return {}
        return {
            "type": place.category,
            "address": place.address,
            "description": place.note,
            "latitude": place.latitude,
            "longitude": place.longitude,
        }


class ForchheimSummarySensor(
    CoordinatorEntity[ForchheimDataUpdateCoordinator], SensorEntity
):
    """A citywide count or traffic summary."""

    _attr_has_entity_name = True
    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: ForchheimDataUpdateCoordinator,
        key: str,
        name: str,
        icon: str,
        value_fn: Callable[[CityData], int | float],
        attributes_fn: Callable[[CityData], dict[str, Any]] | None = None,
        unit: str | None = None,
        device_class: SensorDeviceClass | None = None,
    ) -> None:
        """Initialize a summary sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"city_{key}"
        self._attr_name = name
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self.value_fn = value_fn
        self.attributes_fn = attributes_fn
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "digitales_forchheim")},
            name="Digitales Forchheim",
            manufacturer="Stadt Forchheim",
            model="Öffentliche Stadtdaten",
            configuration_url="https://dz.forchheim.de/",
        )

    @property
    def native_value(self) -> int | float:
        """Return the current summary value."""
        return self.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return optional summary details."""
        return self.attributes_fn(self.coordinator.data) if self.attributes_fn else {}


def _place_attributes(place: Place | None) -> dict[str, Any]:
    """Return attributes for a nearest-place sensor."""
    if place is None:
        return {}
    return {
        "name": place.name,
        "type": place.category,
        "address": place.address,
        "description": place.note,
        "latitude": place.latitude,
        "longitude": place.longitude,
        **place.extra,
    }


def _summary_entities(
    coordinator: ForchheimDataUpdateCoordinator,
    home_latitude: float,
    home_longitude: float,
) -> list[SensorEntity]:
    """Create citywide summary and nearest-place sensors."""

    def count_stations(category: str) -> Callable[[CityData], int]:
        return lambda data: sum(s.category == category for s in data.stations)

    def count_places(*categories: str) -> Callable[[CityData], int]:
        return lambda data: sum(p.category in categories for p in data.places)

    def nearest_value(selector: Callable[[CityData], tuple[Place, ...]]):
        def value(data: CityData) -> float:
            place = _nearest(selector(data), home_latitude, home_longitude)
            if place is None:
                return 0.0
            return round(
                _distance_km(
                    home_latitude, home_longitude, place.latitude, place.longitude
                ),
                2,
            )

        return value

    def nearest_attributes(selector: Callable[[CityData], tuple[Place, ...]]):
        return lambda data: _place_attributes(
            _nearest(selector(data), home_latitude, home_longitude)
        )

    distance_args = {
        "unit": UnitOfLength.KILOMETERS,
        "device_class": SensorDeviceClass.DISTANCE,
    }
    return [
        ForchheimSummarySensor(
            coordinator,
            "weather_station_count",
            "Wetterstationen",
            "mdi:weather-partly-cloudy",
            count_stations("weather"),
        ),
        ForchheimSummarySensor(
            coordinator,
            "temperature_station_count",
            "Temperatur- und Feuchtesensoren",
            "mdi:thermometer-lines",
            count_stations("temperature"),
        ),
        ForchheimSummarySensor(
            coordinator,
            "car_charging_count",
            "PKW-Ladestationen",
            "mdi:ev-station",
            count_places("E-Ladesäule (PKW)"),
        ),
        ForchheimSummarySensor(
            coordinator,
            "bike_charging_count",
            "E-Bike-Ladestationen",
            "mdi:bicycle-electric",
            count_places("E-Ladesäule (E-Bike)"),
        ),
        ForchheimSummarySensor(
            coordinator,
            "parking_count",
            "Parkmöglichkeiten",
            "mdi:parking",
            count_places("Parkplatz", "Parkhaus", "Tiefgarage", "Behindertenparkplatz"),
        ),
        ForchheimSummarySensor(
            coordinator,
            "bicycle_rack_count",
            "Fahrradständer",
            "mdi:bicycle-basket",
            count_places("Fahrradständer"),
        ),
        ForchheimSummarySensor(
            coordinator,
            "playground_count",
            "Spielplätze",
            "mdi:slide",
            lambda data: len(data.playgrounds),
        ),
        ForchheimSummarySensor(
            coordinator,
            "construction_count",
            "Aktive Baustellen",
            "mdi:sign-caution",
            lambda data: len(data.construction_sites),
            lambda data: {
                "sites": [
                    {
                        "name": place.name,
                        "address": place.address,
                        **place.extra,
                    }
                    for place in data.construction_sites[:20]
                ]
            },
        ),
        ForchheimSummarySensor(
            coordinator,
            "traffic_average_speed",
            "Verkehr Durchschnittsgeschwindigkeit",
            "mdi:speedometer",
            lambda data: data.traffic.average_speed,
            lambda data: {
                "period": data.traffic.period,
                "cells": data.traffic.cells,
                "data_type": "Historisches Floating-Car-Verkehrsprofil",
            },
            UnitOfSpeed.KILOMETERS_PER_HOUR,
            SensorDeviceClass.SPEED,
        ),
        ForchheimSummarySensor(
            coordinator,
            "traffic_observations",
            "Verkehr Messungen",
            "mdi:car-multiple",
            lambda data: data.traffic.observations,
            lambda data: {"period": data.traffic.period},
        ),
        ForchheimSummarySensor(
            coordinator,
            "nearest_bus_stop",
            "Nächste Bushaltestelle",
            "mdi:bus-stop",
            nearest_value(
                lambda data: tuple(p for p in data.transit_stops if p.category == "BUS")
            ),
            nearest_attributes(
                lambda data: tuple(p for p in data.transit_stops if p.category == "BUS")
            ),
            **distance_args,
        ),
        ForchheimSummarySensor(
            coordinator,
            "nearest_rail_stop",
            "Nächster Bahnhof",
            "mdi:train",
            nearest_value(
                lambda data: tuple(
                    p for p in data.transit_stops if p.category in ("R", "S")
                )
            ),
            nearest_attributes(
                lambda data: tuple(
                    p for p in data.transit_stops if p.category in ("R", "S")
                )
            ),
            **distance_args,
        ),
        ForchheimSummarySensor(
            coordinator,
            "nearest_playground",
            "Nächster Spielplatz",
            "mdi:slide",
            nearest_value(lambda data: data.playgrounds),
            nearest_attributes(lambda data: data.playgrounds),
            **distance_args,
        ),
        ForchheimSummarySensor(
            coordinator,
            "nearest_construction",
            "Nächste Baustelle",
            "mdi:sign-caution",
            nearest_value(lambda data: data.construction_sites),
            nearest_attributes(lambda data: data.construction_sites),
            **distance_args,
        ),
    ]
