from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import FuelWatchCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    location = entry.data.get("location")
    fuel_types = entry.data.get("fuel_types", ["ulp_91"])

    coordinators = {}
    for fuel_type in fuel_types:
        coordinator = FuelWatchCoordinator(hass, location, fuel_type)
        await coordinator.async_config_entry_first_refresh()
        coordinators[fuel_type] = coordinator

    hass.data[DOMAIN][entry.entry_id] = coordinators
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True
