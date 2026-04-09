# -*- coding: utf-8 -*-

from typing import Any
from homeassistant.helpers.entity import Entity

from .iot_client import DdIotClient


class DdIotDevice:
    """DdIot Device Instance."""

    # pylint: disable=unused-argument

    _online: bool

    _did: str # 设备id

    def __init__(
        self,
        miot_client: DdIotClient,
        device_info: dict[str, Any],
    ) -> None:
        self.miot_client = miot_client
        self.device_info = device_info
        self._online = False
        self._did = device_info.get("did", "")

    @property
    def online(self) -> bool:
        return self._online

    @property
    def did(self) -> str:
        return self._did


class DdIotPropertyEntity(Entity):
    """DdIot Property Entity."""

    def __init__(self, ddiot_device: DdIotDevice) -> None:
        self.ddiot_device = ddiot_device

    @property
    def name(self):
        """Return the name of the entity."""
        return self._attr_name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._attr_unique_id

    @property
    def entity_id(self):
        """Return the entity ID."""
        return self._attr_entity_id

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(self.ddiot_device.__class__.__name__, self.ddiot_device.did)},
            "name": self.ddiot_device.device_info.get("name", "DdIot Device"),
            "manufacturer": "Dd",
            "model": self.ddiot_device.device_info.get("model", "Unknown"),
        }

    async def set_property_async(self, value: Any) -> bool:
        if not self.spec.writable:
            raise RuntimeError(
                f"set property failed, not writable, {self.entity_id}, {self.name}"
            )
        value = self.spec.value_format(value)
        value = self.spec.value_precision(value)
        try:
            await self.ddiot_device.miot_client.set_prop_async(
                did=self.ddiot_device.did,
                siid=self.spec.service.iid,
                piid=self.spec.iid,
                value=value,
            )
        except Exception as e:
            raise RuntimeError(f"{e}, {self.entity_id}, {self.name}") from e
        self._value = value
        self.async_write_ha_state()
        return True
