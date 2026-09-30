"""Constants for the Forchheim Sensors integration."""

from typing import Final

DOMAIN: Final = "forchheim_sensors"

CONF_STATION: Final = "station"
CONF_STATION_NAME: Final = "station_name"
CONF_LATITUDE: Final = "latitude"
CONF_LONGITUDE: Final = "longitude"
CONF_SCAN_INTERVAL: Final = "scan_interval"

DEFAULT_SCAN_INTERVAL: Final = 300
MIN_SCAN_INTERVAL: Final = 60
MAX_SCAN_INTERVAL: Final = 3600

TENANT_UID: Final = "76819234-B9B7-4F10-AD77-1FB61257E150"
LOCATIONS_URL: Final = "https://dz.forchheim.de/datasource-data/sensorthings/Locations/"
GRAFANA_QUERY_URL: Final = "https://dashboard-public.sds.community/api/ds/query"
GRAFANA_DASHBOARD_URL: Final = (
    "https://dashboard-public.sds.community/grafana/d/"
    "wetterstation_forchheim/wetterstation-forchheim"
)

PLATFORMS: Final = ["sensor"]
