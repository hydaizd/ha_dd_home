# -*- coding: utf-8 -*-

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.switch import SwitchEntity

from .ddiot.iot_device import DdIotDevice
from .ddiot.iot_device import DdIotPropertyEntity
from .ddiot.const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up a config entry."""
    device_list: list[DdIotDevice] = hass.data[DOMAIN]['devices'][
        config_entry.entry_id]

    new_entities = []
    for miot_device in device_list:
        for prop in miot_device.prop_list.get('switch', []):
            new_entities.append(Switch(miot_device=miot_device, spec=prop))

    if new_entities:
        async_add_entities(new_entities)


class Switch(DdIotPropertyEntity, SwitchEntity):
    """Switch entities for Dd Home."""

    # pylint: disable=unused-argument

    def __init__(self, ddiot_device: DdIotDevice) -> None:
        """Initialize the Switch."""
        super().__init__(ddiot_device=ddiot_device)

    @property
    def is_on(self) -> bool:
        """On/Off state."""
        return self._value is True

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.set_property_async(value=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.set_property_async(value=False)

    async def async_toggle(self, **kwargs: Any) -> None:
        """Toggle the switch."""
        await self.set_property_async(value=not self.is_on)
