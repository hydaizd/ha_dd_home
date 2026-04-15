# -*- coding: utf-8 -*-

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

# 用于在 HA 前端显示的名称
DEFAULT_NAME = "Aam Home Controlled Switch"


async def async_setup_entry(
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    switch_instance = hass.data[DOMAIN][config_entry.entry_id]
    # 添加实体
    async_add_entities([AamSwitchEntity(switch_instance)])


class AamSwitchEntity(CoordinatorEntity, SwitchEntity):
    """Representation of an AAM Switch."""

    _is_on: bool  # 开关开启状态(True/False, 初始状态为 False, True为开启, False为关闭)
    _cmd: str  # 开关控制艾美指令(固定 set_state)
    _midBindId: str  # 开关设备指纹
    _endpointId: int  # 开关设备端点ID

    # pylint: disable=unused-argument

    _attr_name = DEFAULT_NAME
    _attr_unique_id = f"{DOMAIN}_switch_{DOMAIN}"  # 确保 unique_id 唯一

    def __init__(self, switch_instance):
        """Initialize the switch."""
        super().__init__(switch_instance.coordinator)  # 如果有协调器的话
        self._switch = switch_instance
        self._is_on = False
        self._cmd = "set_state"

    @property
    def is_on(self) -> bool:
        """On/Off state."""
        return self._is_on is True

    @property
    def cmd(self) -> str:
        """Return the command."""
        return self._cmd

    @property
    def midBindId(self) -> str:
        """Return the midBindId."""
        return self._midBindId

    @property
    def endpointId(self) -> int:
        """Return the endpointId."""
        return self._endpointId

    async def _send_request(self, value: bool) -> bool:
        """Send a request to the switch."""
        try:
            await self.iot_client.fetch_post_async(
                midBindId=self.midBindId,
                cmd=self.cmd,
                ep=self.endpointId,
                value=value,
            )
        except Exception as e:
            raise RuntimeError(f"{e}, {self._switch.entity_id}, {self._switch.name}") from e
        self._is_on = value
        self.async_write_ha_state()
        return True

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._send_request(value=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._send_request(value=False)

    async def async_toggle(self, **kwargs: Any) -> None:
        """Toggle the switch."""
        await self._send_request(value=not self.is_on)
