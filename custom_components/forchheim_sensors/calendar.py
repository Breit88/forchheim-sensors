"""Calendar platform for official Landkreis Forchheim waste collections."""

from __future__ import annotations

from datetime import datetime, time, timedelta
from urllib.parse import quote

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import ForchheimConfigEntry
from .const import CONF_WASTE_LOCATION, DOMAIN, WASTE_BASE_URL
from .coordinator import ForchheimWasteUpdateCoordinator
from .models import WasteEvent
from .waste import configured_waste_locations, waste_entity_suffix


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ForchheimConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add a calendar only when the user chose a collection area."""
    primary = entry.options.get(CONF_WASTE_LOCATION)
    async_add_entities(
        [
            ForchheimWasteCalendar(entry.runtime_data.waste_coordinators[path], primary)
            for path in configured_waste_locations(entry.options)
        ]
    )


class ForchheimWasteCalendar(
    CoordinatorEntity[ForchheimWasteUpdateCoordinator], CalendarEntity
):
    """All collection events for the selected street or locality."""

    def __init__(
        self, coordinator: ForchheimWasteUpdateCoordinator, primary: str | None = None
    ) -> None:
        super().__init__(coordinator)
        path = coordinator.path
        suffix = waste_entity_suffix(path, primary)
        self._attr_unique_id = f"waste_calendar{suffix}"
        self._attr_name = (
            "Forchheim Abfalltermine"
            if not suffix
            else f"Abfalltermine {path.rsplit('/', 1)[-1]}"
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"waste_collection{suffix}")},
            name=f"Abfalltermine {path.rsplit('/', 1)[-1]}",
            manufacturer="Landkreis Forchheim",
            model="Abfallkalender",
            configuration_url=f"{WASTE_BASE_URL}{quote(path, safe='/()-')}",
        )

    @property
    def available(self) -> bool:
        """Keep the last known events while a later refresh fails."""
        return self.coordinator.data is not None

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next pickup event."""
        today = dt_util.now().date()
        return next(
            (
                _as_calendar_event(item)
                for item in self.coordinator.data or ()
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
            for item in self.coordinator.data or ()
            if (
                datetime.combine(
                    item.day + timedelta(days=1), time.min, start_date.tzinfo
                )
                > start_date
                and datetime.combine(item.day, time.min, end_date.tzinfo) < end_date
            )
        ]


def _as_calendar_event(item: WasteEvent) -> CalendarEvent:
    return CalendarEvent(
        start=item.day,
        end=item.day + timedelta(days=1),
        summary=item.kind,
    )
