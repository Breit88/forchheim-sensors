"""Validate the importable waste reminder with Home Assistant's schemas."""

from pathlib import Path

from homeassistant.components.automation.config import (
    AUTOMATION_BLUEPRINT_SCHEMA,
    PLATFORM_SCHEMA,
)
from homeassistant.components.blueprint.models import Blueprint, BlueprintInputs
from homeassistant.util import yaml


async def test_waste_reminder_blueprint_is_valid() -> None:
    """The sample notification can be configured in the automation editor."""
    path = (
        Path(__file__).parents[1]
        / "blueprints/automation/forchheim_sensors/waste_reminder.yaml"
    )
    blueprint = Blueprint(
        yaml.load_yaml_dict(path),
        path=str(path),
        expected_domain="automation",
        schema=AUTOMATION_BLUEPRINT_SCHEMA,
    )
    inputs = BlueprintInputs(
        blueprint,
        {
            "use_blueprint": {
                "path": str(path),
                "input": {
                    "waste_calendar": "calendar.forchheim_abfalltermine",
                    "notification_actions": [
                        {
                            "action": "persistent_notification.create",
                            "data": {"message": "{{ trigger.calendar_event.summary }}"},
                        }
                    ],
                },
            }
        },
    )
    inputs.validate()
    automation = PLATFORM_SCHEMA(inputs.async_substitute())
    assert automation["triggers"][0]["entity_id"] == "calendar.forchheim_abfalltermine"
