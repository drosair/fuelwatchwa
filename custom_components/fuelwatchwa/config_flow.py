"""Config flow for the FuelWatch WA integration."""
from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol

from .const import CONF_DAY, CONF_FUEL_TYPES, CONF_LOCATION, DAY_OPTIONS, DEFAULT_DAY, DEFAULT_FUEL_TYPES, DOMAIN, FUEL_TYPE_OPTIONS


class FuelWatchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FuelWatch WA."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            location = user_input[CONF_LOCATION].strip()
            fuel_types = user_input[CONF_FUEL_TYPES]

            if not location:
                errors[CONF_LOCATION] = "required"
            elif not fuel_types:
                errors[CONF_FUEL_TYPES] = "required"
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
                vol.Required(CONF_FUEL_TYPES, default=DEFAULT_FUEL_TYPES): cv_multi_select(FUEL_TYPE_OPTIONS),
                vol.Required(CONF_DAY, default=DEFAULT_DAY): vol.In(DAY_OPTIONS),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)


def cv_multi_select(options: dict[str, int]):
    """Return a simple multi-select validator compatible with config flows."""
    valid = set(options.keys())

    def validate(value):
        if isinstance(value, str):
            selected = [value]
        else:
            selected = list(value)
        if not selected or any(item not in valid for item in selected):
            raise vol.Invalid("invalid_selection")
        return selected

    return validate
