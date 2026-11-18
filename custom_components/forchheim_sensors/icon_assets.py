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
    "restmuell": f"{ICON_URL}/bin_black_custom.png",
    "single": f"{ICON_URL}/bin_black_custom.png",
    "bio": f"{ICON_URL}/bin_green_custom.png",
    "papier": f"{ICON_URL}/bin_blue_custom.png",
    "gelb": f"{ICON_URL}/bin_yellow_custom.png",
}
