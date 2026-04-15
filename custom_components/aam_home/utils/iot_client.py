# -*- coding: utf-8 -*-

import logging
from typing import Any, Callable, Optional

from homeassistant.core import HomeAssistant

from .http_client import HttpClient
from .iot_error import IoTClientError, IotErrorCode
from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class IotClient:
    """Iot client instance."""
    _entry_id: str
    _entry_data: dict
    _http: HttpClient

    def __init__(self, entry_id: str, entry_data: dict, ) -> None:
        self._http = None

    async def init_async(self) -> None:
        # Iot http client instance
        self._http = HttpClient(access_token='')

    async def send_request_async(self, mid_bind_id: str, cmd: str, ep: int, value: Any) -> bool:
        # Local http control
        result = await self._http.fetch_post_async(
            params=[
                {'midBindId': mid_bind_id, 'cmd': cmd, 'endpointId': ep, 'value': value}
            ])
        _LOGGER.debug('cloud set prop, %s.%d.%d, %s -> %s', mid_bind_id, cmd, ep, value, result)
        if result and len(result) == 1:
            rc = result[0].get('code', IotErrorCode.CODE_MIPS_INVALID_RESULT.value)
            if rc in [0, 1]:
                return True
            if rc in [-704010000, -704042011]:
                # Device remove or offline
                _LOGGER.error('device may be removed or offline, %s', mid_bind_id)
            raise IoTClientError("device may be removed or offline11111")
        return True


@staticmethod
async def get_iot_instance_async(
        hass: HomeAssistant, entry_id: str, entry_data: Optional[dict] = None,
        persistent_notify: Optional[Callable[[str, str, str], None]] = None
) -> IotClient:
    if entry_id is None:
        raise IoTClientError('invalid entry_id')

    miot_client = hass.data[DOMAIN].get('iot_clients', {}).get(entry_id, None)
    if miot_client:
        _LOGGER.info('instance exist, %s', entry_id)
        return miot_client

    # Iot client
    iot_client = IotClient(entry_id=entry_id, entry_data=entry_data)
    iot_client.persistent_notify = persistent_notify
    hass.data[DOMAIN]['iot_clients'].setdefault(entry_id, iot_client)
    _LOGGER.info('new miot_client instance, %s, %s', entry_id, entry_data)
    await iot_client.init_async()
    return iot_client
