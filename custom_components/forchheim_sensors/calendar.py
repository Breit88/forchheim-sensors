"""Calendar platform for official Landkreis Forchheim waste collections."""

from __future__ import annotations

from datetime import datetime, timedelta
from urllib.parse import quote

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import ForchheimConfigEntry
from .const import CONF_WASTE_LOCATION, DOMAIN, WASTE_BASE_URL
from .coordinator import ForchheimDataUpdateCoordinator
from .models import WasteEvent


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ForchheimConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add a calendar only when the user chose a collection area."""
    if entry.options.get(CONF_WASTE_LOCATION):
        async_add_entities([ForchheimWasteCalendar(entry.runtime_data)])


class ForchheimWasteCalendar(
    CoordinatorEntity[ForchheimDataUpdateCoordinator], CalendarEntity
):
    """All collection events for the selected street or locality."""

    _attr_name = "Forchheim Abfalltermine"
    _attr_unique_id = "waste_calendar"

    def __init__(self, coordinator: ForchheimDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        path = coordinator.config_entry.options[CONF_WASTE_LOCATION]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "waste_collection")},
            name="Abfalltermine Forchheim",
            manufacturer="Landkreis Forchheim",
            model="Abfallkalender",
            configuration_url=f"{WASTE_BASE_URL}{quote(path, safe='/()-')}",
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next pickup event."""
        today = dt_util.now().date()
        return next(
            (
                _as_calendar_event(item)
                for item in self.coordinator.data.waste_events
                if item.day >= today
            ),
            None,
        )

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return all pickups in the requested date range."""
        return [
            _as_calendar_event(item)
            for item in self.coordinator.data.waste_events
            if start_date.date() <= item.day < end_date.date()
        ]


def _as_calendar_event(item: WasteEvent) -> CalendarEvent:
    return CalendarEvent(
        start=item.day,
        end=item.day + timedelta(days=1),
        summary=item.kind,
    )
