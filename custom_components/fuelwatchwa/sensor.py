"""Sensor platform for FuelWatch WA."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    coordinators = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for fuel_type, coordinator in coordinators.items():
        entities.extend(
            [
                FuelNumericSensor(coordinator, fuel_type, "min_price"),
                FuelNumericSensor(coordinator, fuel_type, "avg_price"),
                FuelNumericSensor(coordinator, fuel_type, "max_price"),
                FuelNumericSensor(coordinator, fuel_type, "price_spread"),
                FuelNumericSensor(coordinator, fuel_type, "station_count"),
                FuelCheapestSensor(coordinator, fuel_type, "price"),
                FuelCheapestSensor(coordinator, fuel_type, "brand"),
                FuelCheapestSensor(coordinator, fuel_type, "address"),
            ]
        )

    async_add_entities(entities)


class BaseFuelSensor(SensorEntity):
    def __init__(self, coordinator, fuel_type: str):
        self.coordinator = coordinator
        self.fuel_type = fuel_type

    async def async_update(self):
        await self.coordinator.async_request_refresh()

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return None

        return {
            "location": self.coordinator.data.get("location"),
            "fuel_type": self.coordinator.data.get("fuel_type"),
            "day": self.coordinator.data.get("day"),
            "top_3": self.coordinator.data.get("top_3"),
            "fetched_at": self.coordinator.data.get("fetched_at"),
        }


class FuelNumericSensor(BaseFuelSensor):
    def __init__(self, coordinator, fuel_type: str, key: str):
        super().__init__(coordinator, fuel_type)
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


class FuelCheapestSensor(BaseFuelSensor):
    def __init__(self, coordinator, fuel_type: str, field: str):
        super().__init__(coordinator, fuel_type)
        self.field = field

    @property
    def name(self):
        return f"FuelWatch {self.fuel_type} cheapest {self.field}"

    @property
    def unique_id(self):
        return f"fuelwatchwa_{self.fuel_type}_cheapest_{self.field}"

    @property
    def native_value(self):
        if self.coordinator.data:
            cheapest = self.coordinator.data.get("cheapest", {})
            return cheapest.get(self.field)
        return None
