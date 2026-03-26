"""Config flow for the FuelWatch WA integration."""
from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector
import voluptuous as vol

from .const import (
    COMMON_SUBURBS,
    CONF_DAY,
    CONF_FUEL_TYPES,
    CONF_LOCATION,
    DAY_OPTIONS,
    DEFAULT_DAY,
    DOMAIN,
    FUEL_TYPE_NAMES,
    FUEL_TYPE_OPTIONS,
)


class FuelWatchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            location = user_input[CONF_LOCATION]
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
                vol.Required(CONF_LOCATION): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=COMMON_SUBURBS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                        custom_value=True,
                    ),
                ),
                vol.Required(CONF_FUEL_TYPES, default=["diesel"]): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=k, label=v)
                            for k, v in FUEL_TYPE_NAMES.items()
                        ],
                        multiple=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    ),
                ),
                vol.Required(CONF_DAY, default=DEFAULT_DAY): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=DAY_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    ),
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
