# -*- coding: utf-8 -*-

import logging
from typing import Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components import persistent_notification
from homeassistant.helpers import device_registry, entity_registry

from .const import DOMAIN, SUPPORTED_PLATFORMS

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, hass_config: dict) -> bool:
    """集成初始化"""
    # pylint: disable=unused-argument
    hass.data.setdefault(DOMAIN, {})
    # {[entry_id:str]: DdIotClient}, ddiot client instance
    hass.data[DOMAIN].setdefault("ddiot_clients", {})
    # {[entry_id:str]: list[DdIotDevice]}
    hass.data[DOMAIN].setdefault("devices", {})
    # {[entry_id:str]: entities}
    hass.data[DOMAIN].setdefault("entities", {})
    for platform in SUPPORTED_PLATFORMS:
        hass.data[DOMAIN]["entities"][platform] = []
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """集成安装"""

    def ha_persistent_notify(
        notify_id: str, title: Optional[str] = None, message: Optional[str] = None
    ) -> None:
        """Send messages in Notifications dialog box."""
        if title:
            persistent_notification.async_create(
                hass=hass, message=message or "", title=title, notification_id=notify_id
            )
        else:
            persistent_notification.async_dismiss(hass=hass, notification_id=notify_id)

    entry_id = config_entry.entry_id
    entry_data = dict(config_entry.data)

    ha_persistent_notify(notify_id=f"{entry_id}.oauth_error", title=None, message=None)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """集成卸载"""
    return True


async def async_remove_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """集成移除"""
    return True


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    device_entry: device_registry.DeviceEntry,
) -> bool:
    """集成移除设备"""

    return True
