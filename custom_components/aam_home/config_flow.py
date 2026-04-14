# -*- coding: utf-8 -*-

import json
import logging
from pprint import pformat
from typing import Any, List, Dict

import voluptuous as vol
import websocket
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant, callback

from .const import (
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_DEVICE_TYPE,
    CONF_DEVICE_SKU,
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
        ws_url = "ws://10.0.3.74:8888/devices"
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
                    CONF_DEVICE_NAME: device_data.get("device_name"),
                    CONF_DEVICE_TYPE: device_data.get("device_type"),
                    CONF_DEVICE_SKU: device_data.get("device_sku"),
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
    def async_get_options_flow(config_entry: ConfigEntry) -> DdOptionsFlowHandler:
        """Get the options flow for this handler."""
        return DdOptionsFlowHandler(config_entry)

    def __init__(self) -> None:
        """Initialize the ONVIF config flow."""
        self.device_id = None
        self.devices: list[dict[str, Any]] = []
        self.onvif_config: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle user flow."""
        if user_input:
            if user_input["host"]:
                return await self.async_step_device()
            return await self.async_step_configure()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("host", default=""): str}),
        )

    async def async_step_device(self, user_input: dict[str, str] | None = None) -> ConfigFlowResult:
        """Handle WS-Discovery.

        Let user choose between discovered devices and manual configuration.
        If no device is found allow user to manually input configuration.
        """
        if user_input:
            for device in self.devices:
                if device[CONF_DEVICE_ID] == user_input[CONF_DEVICE_ID]:
                    self.device_id = device[CONF_DEVICE_ID]
                    self.onvif_config = {
                        CONF_DEVICE_NAME: device[CONF_DEVICE_NAME],
                        CONF_DEVICE_ID: device[CONF_DEVICE_ID],
                        CONF_DEVICE_TYPE: device[CONF_DEVICE_TYPE],
                        CONF_DEVICE_SKU: device[CONF_DEVICE_SKU],
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
            devices = {}
            for device in self.devices:
                description = f"{device[CONF_DEVICE_NAME]} ({device[CONF_DEVICE_SKU]})"
                if dtype := device[CONF_DEVICE_TYPE]:
                    description += f" [{dtype}]"
                devices[device[CONF_DEVICE_ID]] = description

            return self.async_show_form(
                step_id="device",
                data_schema=vol.Schema({vol.Optional(CONF_DEVICE_ID): vol.In(devices)}),
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
            title = f"{self.onvif_config[CONF_DEVICE_NAME]} - {self.device_id}"
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
                    vol.Required(CONF_DEVICE_NAME, default=conf(CONF_DEVICE_NAME)): str,
                    vol.Required(CONF_DEVICE_ID, default=conf(CONF_DEVICE_ID)): str,
                    vol.Required(CONF_DEVICE_TYPE, default=conf(CONF_DEVICE_TYPE)): str,
                    vol.Required(CONF_DEVICE_SKU, default=conf(CONF_DEVICE_SKU)): str,
                }
            ),
            errors=errors,
            description_placeholders=description_placeholders,
        )
