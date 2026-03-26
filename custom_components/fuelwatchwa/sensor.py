from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.core import HomeAssistant

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinators = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for fuel_type, coordinator in coordinators.items():
        entities.extend([
            FuelSummarySensor(coordinator, fuel_type, "min_price"),
            FuelSummarySensor(coordinator, fuel_type, "avg_price"),
            FuelSummarySensor(coordinator, fuel_type, "max_price"),
            FuelSummarySensor(coordinator, fuel_type, "price_spread"),
            FuelSummarySensor(coordinator, fuel_type, "station_count"),
        ])

    async_add_entities(entities)

class FuelSummarySensor(SensorEntity):
    def __init__(self, coordinator, fuel_type: str, key: str):
        self.coordinator = coordinator
        self.fuel_type = fuel_type
        self.key = key

    @property
    def name(self):
        return f"FuelWatch {self.fuel_type} {self.key}"

    @property
    def unique_id(self):
        return f"fuelwatchwa_{self.fuel_type}_{self.key}"

    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data.get(self.key)
        return None

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return None

        return {
            "location": self.coordinator.data.get("location"),
            "fuel_type": self.coordinator.data.get("fuel_type"),
            "day": self.coordinator.data.get("day"),
            "top_3": self.coordinator.data.get("top_3"),
        }

    async def async_update(self):
        await self.coordinator.async_request_refresh()
