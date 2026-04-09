# -*- coding: utf-8 -*-

from typing import Optional

from homeassistant import config_entries
from homeassistant.core import callback


from .ddiot.const import DOMAIN


class DdHomeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Dd Home config flow."""

    # pylint: disable=unused-argument, inconsistent-quotes
    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """Initialize."""

    async def async_step_user(self, user_input: Optional[dict] = None):
        """Handle the user step."""

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Dd Home options flow."""

    # pylint: disable=unused-argument
    # pylint: disable=inconsistent-quotes
    _config_entry: config_entries.ConfigEntry

    def __init__(self, config_entry):
        self.config_entry = config_entry
