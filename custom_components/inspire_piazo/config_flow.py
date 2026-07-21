"""Config flow for Inspire Piazo."""

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_REMOTE_CODE,
    DEFAULT_NAME,
    DEFAULT_REMOTE_CODE,
    DOMAIN,
    RFXTRX_DOMAIN,
)
from .protocol import normalize_remote_code


class InspirePiazoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an Inspire Piazo config flow."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle configuration started by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = user_input[CONF_NAME].strip()

            if not name:
                errors[CONF_NAME] = "name_required"

            try:
                remote_code = normalize_remote_code(user_input[CONF_REMOTE_CODE])
            except ValueError:
                errors[CONF_REMOTE_CODE] = "invalid_remote_code"

            if not self.hass.config_entries.async_entries(RFXTRX_DOMAIN):
                errors["base"] = "rfxtrx_not_configured"

            if not errors:
                await self.async_set_unique_id(remote_code)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={CONF_REMOTE_CODE: remote_code},
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_NAME,
                    default=(
                        user_input.get(CONF_NAME, DEFAULT_NAME)
                        if user_input
                        else DEFAULT_NAME
                    ),
                ): cv.string,
                vol.Required(
                    CONF_REMOTE_CODE,
                    default=(
                        user_input.get(CONF_REMOTE_CODE, DEFAULT_REMOTE_CODE)
                        if user_input
                        else DEFAULT_REMOTE_CODE
                    ),
                ): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
