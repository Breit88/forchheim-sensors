"""Shared test fixtures for Forchheim Sensors."""

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Allow loading the custom integration in Home Assistant tests."""
    yield
