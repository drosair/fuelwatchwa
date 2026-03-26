from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import FuelWatchAPI
from .const import DOMAIN

_LOGGER = logging.getLogger(DOMAIN)

class FuelWatchCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, suburb: str, fuel_type: str, day: str):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=30),
        )
        self.api = FuelWatchAPI()
        self.suburb = suburb
        self.fuel_type = fuel_type
        self.day = day

    async def _async_update_data(self):
        return await self.api.fetch(self.suburb, self.fuel_type, self.day)
