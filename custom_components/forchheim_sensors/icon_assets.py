"""Locally served pictures for map points and waste date sensors."""

from __future__ import annotations

from .const import DOMAIN

ICON_URL = f"/{DOMAIN}/icons"

PLACE_PICTURES = {
    "weather": f"{ICON_URL}/weather_station.png",
    "playground": f"{ICON_URL}/playground.png",
    "construction": f"{ICON_URL}/construction.png",
}

WASTE_PICTURES = {
    "restmuell": f"{ICON_URL}/bin_black.png",
    "single": f"{ICON_URL}/bin_black.png",
    "bio": f"{ICON_URL}/bin_green.svg",
    "papier": f"{ICON_URL}/bin_blue.svg",
    "gelb": f"{ICON_URL}/bin_yellow.svg",
}
