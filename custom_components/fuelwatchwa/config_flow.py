"""Config flow for the FuelWatch WA integration."""
from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

from .const import (
    CONF_DAY,
    CONF_FUEL_TYPES,
    CONF_LOCATION,
    DAY_OPTIONS,
    DEFAULT_DAY,
    DOMAIN,
    FUEL_TYPE_OPTIONS,
)


class FuelWatchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            location = user_input[CONF_LOCATION].strip()
            raw_fuel_types = user_input[CONF_FUEL_TYPES]

            fuel_types = [item.strip() for item in raw_fuel_types.split(",") if item.strip()]

            if not location:
                errors[CONF_LOCATION] = "required"
            elif not fuel_types:
                errors[CONF_FUEL_TYPES] = "required"
            elif any(item not in FUEL_TYPE_OPTIONS for item in fuel_types):
                errors[CONF_FUEL_TYPES] = "invalid_selection"
            else:
                await self.async_set_unique_id(f"{location.lower()}_{user_input[CONF_DAY]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"FuelWatch WA ({location})",
                    data={
                        CONF_LOCATION: location,
                        CONF_FUEL_TYPES: fuel_types,
                        CONF_DAY: user_input[CONF_DAY],
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_LOCATION): str,
                vol.Required(CONF_FUEL_TYPES, default="diesel"): str,
                vol.Required(CONF_DAY, default=DEFAULT_DAY): vol.In(DAY_OPTIONS),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
