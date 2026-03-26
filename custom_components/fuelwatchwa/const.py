"""Constants for the FuelWatch WA integration."""
from __future__ import annotations

from datetime import timedelta

DOMAIN = "fuelwatchwa"
PLATFORMS = ["sensor"]

CONF_LOCATION = "location"
CONF_DAY = "day"
CONF_FUEL_TYPES = "fuel_types"

DEFAULT_DAY = "today"
DEFAULT_FUEL_TYPES = ["ulp_91"]
DEFAULT_SCAN_INTERVAL = timedelta(minutes=30)

DAY_OPTIONS = ["today", "tomorrow"]
FUEL_TYPE_OPTIONS = {
    "ulp_91": 1,
    "premium_95": 2,
    "diesel": 4,
    "lpg": 5,
    "premium_98": 6,
    "e85": 10,
    "brand_diesel": 11,
}

ATTR_TOP_3 = "top_3"
ATTR_FETCHED_AT = "fetched_at"
ATTR_LOCATION = "location"
ATTR_FUEL_TYPE = "fuel_type"
ATTR_DAY = "day"
ATTR_STATION_COUNT = "station_count"
