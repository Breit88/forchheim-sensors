"""Sensor platform for Forchheim Sensors."""

from __future__ import annotations

from dataclasses import dataclass
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
from .const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_STATION,
    CONF_STATION_NAME,
    DOMAIN,
    GRAFANA_DASHBOARD_URL,
    TENANT_UID,
)
from .coordinator import ForchheimDataUpdateCoordinator

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class ForchheimSensorEntityDescription(SensorEntityDescription):
    """Describe a Forchheim measurement."""

    source_key: str


SENSORS: tuple[ForchheimSensorEntityDescription, ...] = (
    ForchheimSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        source_key="Temperatur",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        source_key="Luftfeuchtigkeit (rel.)",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="pressure",
        translation_key="pressure",
        source_key="Luftdruck",
        device_class=SensorDeviceClass.ATMOSPHERIC_PRESSURE,
        native_unit_of_measurement=UnitOfPressure.HPA,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="wind_speed",
        translation_key="wind_speed",
        source_key="Windgeschwindigkeit",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="wind_direction",
        translation_key="wind_direction",
        source_key="Windrichtung",
        icon="mdi:compass-outline",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="dew_point",
        translation_key="dew_point",
        source_key="Taupunkt",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    ForchheimSensorEntityDescription(
        key="precipitation_hour",
        translation_key="precipitation_hour",
        source_key="Niederschlag pro h",
        device_class=SensorDeviceClass.PRECIPITATION_INTENSITY,
        native_unit_of_measurement=UnitOfVolumetricFlux.MILLIMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ForchheimConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up all measurement entities for a station."""
    coordinator = entry.runtime_data
    async_add_entities(
        ForchheimSensor(coordinator, entry, description) for description in SENSORS
    )


class ForchheimSensor(CoordinatorEntity[ForchheimDataUpdateCoordinator], SensorEntity):
    """A measurement from a Forchheim weather station."""

    _attr_has_entity_name = True
    _attr_attribution = "Daten: Stadt Forchheim / Smart Data Services"
    entity_description: ForchheimSensorEntityDescription

    def __init__(
        self,
        coordinator: ForchheimDataUpdateCoordinator,
        entry: ForchheimConfigEntry,
        description: ForchheimSensorEntityDescription,
    ) -> None:
        """Initialize a sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        station_uid = entry.data[CONF_STATION]
        self._attr_unique_id = f"{station_uid}_{description.key}"
        dashboard_url = (
            f"{GRAFANA_DASHBOARD_URL}?var-varTenant={TENANT_UID}"
            f"&var-varSensor={station_uid}&orgId=2&kiosk=1"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, station_uid)},
            name=f"Wetterstation {entry.data[CONF_STATION_NAME]}",
            manufacturer="Stadt Forchheim / Smart Data Services",
            model="Öffentliche Wetterstation",
            configuration_url=dashboard_url,
        )

    @property
    def available(self) -> bool:
        """Return whether this measurement is currently available."""
        return (
            super().available
            and self.entity_description.source_key in self.coordinator.data
        )

    @property
    def native_value(self) -> float | None:
        """Return the current measurement."""
        measurement = self.coordinator.data.get(self.entity_description.source_key)
        return measurement.value if measurement else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return source metadata."""
        measurement = self.coordinator.data.get(self.entity_description.source_key)
        return {
            "measurement_time": (
                measurement.measured_at.isoformat()
                if measurement and measurement.measured_at
                else None
            ),
            "station": self.coordinator.config_entry.data[CONF_STATION_NAME],
            "latitude": self.coordinator.config_entry.data[CONF_LATITUDE],
            "longitude": self.coordinator.config_entry.data[CONF_LONGITUDE],
        }
