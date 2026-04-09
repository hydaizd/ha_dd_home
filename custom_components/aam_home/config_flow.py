# -*- coding: utf-8 -*-

import voluptuous as vol
import logging
import websocket
import json
from pprint import pformat
from urllib.parse import urlparse
from typing import Any, List, Dict

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)

from .const import (
    CONF_DEVICE_ID,
    CONF_HARDWARE,
    DOMAIN,
    DEFAULT_PORT,
)

LOGGER = logging.getLogger(__name__)

CONF_MANUAL_INPUT = "Manually configure Dd device"


def wsdiscovery() -> List[Dict[str, Any]]:
    """Get devices from custom websocket interface."""
    devices = []
    try:
        # 连接到自定义websocket接口
        ws_url = "ws://localhost:8888/devices"
        ws = websocket.create_connection(ws_url)

        # 发送请求获取设备列表
        request = {"action": "get_devices"}
        ws.send(json.dumps(request))

        # 接收响应
        response = ws.recv()
        data = json.loads(response)

        # 解析设备列表
        if data.get("success"):
            for device_data in data.get("devices", []):
                device = {
                    CONF_DEVICE_ID: device_data.get("device_id"),
                    CONF_NAME: device_data.get("name"),
                    CONF_HOST: device_data.get("host"),
                    CONF_PORT: device_data.get("port", 80),
                    CONF_HARDWARE: device_data.get("hardware"),
                }
                devices.append(device)

        ws.close()
    except Exception as e:
        LOGGER.error("Failed to get devices from websocket: %s", e)

    return devices


async def async_discovery(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Return if there are devices that can be discovered."""
    LOGGER.debug("Starting Dd discovery")
    devices = await hass.async_add_executor_job(wsdiscovery)

    LOGGER.debug("Discovered devices from websocket: %s", pformat(devices))

    return devices


class DdOptionsFlowHandler(OptionsFlow):
    """Handle Dd options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize Dd options flow."""
        self.options = dict(config_entry.options)


class DdFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a Dd config flow."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> DdOptionsFlowHandler:
        """Get the options flow for this handler."""
        return DdOptionsFlowHandler(config_entry)

    def __init__(self) -> None:
        """Initialize the ONVIF config flow."""
        self.device_id = None
        self.devices: list[dict[str, Any]] = []
        self.onvif_config: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle user flow."""
        if user_input:
            if user_input["host"]:
                return await self.async_step_device()
            return await self.async_step_configure()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("host", default=""): str}),
        )

    async def async_step_device(
        self, user_input: dict[str, str] | None = None
    ) -> ConfigFlowResult:
        """Handle WS-Discovery.

        Let user choose between discovered devices and manual configuration.
        If no device is found allow user to manually input configuration.
        """
        if user_input:
            if user_input[CONF_HOST] == CONF_MANUAL_INPUT:
                return await self.async_step_configure()

            for device in self.devices:
                if device[CONF_HOST] == user_input[CONF_HOST]:
                    self.device_id = device[CONF_DEVICE_ID]
                    self.onvif_config = {
                        CONF_NAME: device[CONF_NAME],
                        CONF_HOST: device[CONF_HOST],
                        CONF_PORT: device[CONF_PORT],
                    }
                    return await self.async_step_configure()

        discovery = await async_discovery(self.hass)
        for device in discovery:
            configured = any(
                entry.unique_id == device[CONF_DEVICE_ID]
                for entry in self._async_current_entries()
            )

            if not configured:
                self.devices.append(device)

        if LOGGER.isEnabledFor(logging.DEBUG):
            LOGGER.debug("Discovered ONVIF devices %s", pformat(self.devices))

        if self.devices:
            devices = {CONF_MANUAL_INPUT: CONF_MANUAL_INPUT}
            for device in self.devices:
                description = f"{device[CONF_NAME]} ({device[CONF_HOST]})"
                if hardware := device[CONF_HARDWARE]:
                    description += f" [{hardware}]"
                devices[device[CONF_HOST]] = description

            return self.async_show_form(
                step_id="device",
                data_schema=vol.Schema({vol.Optional(CONF_HOST): vol.In(devices)}),
            )

        return await self.async_step_configure()

    async def async_step_configure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Device configuration."""
        errors: dict[str, str] = {}
        description_placeholders: dict[str, str] = {}
        if user_input:
            self.onvif_config = user_input
            errors, description_placeholders = await self.async_setup_profiles()
            if not errors:
                title = f"{self.onvif_config[CONF_NAME]} - {self.device_id}"
                return self.async_create_entry(title=title, data=self.onvif_config)

        def conf(name, default=None):
            return self.onvif_config.get(name, default)

        # Username and Password are optional and default empty
        # due to some cameras not allowing you to change ONVIF user settings.
        # See https://github.com/home-assistant/core/issues/39182
        # and https://github.com/home-assistant/core/issues/35904
        return self.async_show_form(
            step_id="configure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=conf(CONF_NAME)): str,
                    vol.Required(CONF_HOST, default=conf(CONF_HOST)): str,
                    vol.Required(CONF_PORT, default=conf(CONF_PORT, DEFAULT_PORT)): int,
                    vol.Optional(CONF_USERNAME, default=conf(CONF_USERNAME, "")): str,
                    vol.Optional(CONF_PASSWORD, default=conf(CONF_PASSWORD, "")): str,
                }
            ),
            errors=errors,
            description_placeholders=description_placeholders,
        )
