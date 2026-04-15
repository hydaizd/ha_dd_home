# -*- coding: utf-8 -*-

import json
import logging
from typing import Optional

import aiohttp

from .iot_error import IotErrorCode, HttpError
from ..const import (
    HTTP_API_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class HttpClient:
    """HTTP Client."""

    _session: aiohttp.ClientSession
    _host: str
    _base_url: str
    _access_token: str

    def __init__(self, access_token: str) -> None:
        self._base_url = 'http://127.0.0.1:10088'
        self._access_token = ''

        if (
                not isinstance(access_token, str)
        ):
            raise HttpError('invalid params')

        self.update_http_header(access_token=access_token)

        self._session = aiohttp.ClientSession()

    async def de_init_async(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    def update_http_header(self, access_token: Optional[str] = None) -> None:
        if isinstance(access_token, str):
            self._access_token = access_token

    @property
    def __api_request_headers(self) -> dict:
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer{self._access_token}',
        }

    async def __api_post_async(self, url_path: str, data: dict, timeout: int = HTTP_API_TIMEOUT) -> dict:
        http_res = await self._session.post(
            url=f'{self._base_url}{url_path}',
            json=data,
            headers=self.__api_request_headers,
            timeout=timeout)
        if http_res.status == 401:
            raise HttpError('aam home api get failed, unauthorized(401)', IotErrorCode.CODE_HTTP_INVALID_ACCESS_TOKEN)
        if http_res.status != 200:
            raise HttpError(f'aam home api post failed, {http_res.status}, 'f'{url_path}, {data}')
        res_str = await http_res.text()
        res_obj: dict = json.loads(res_str)
        if not res_obj.get('success', None):
            raise HttpError(f'invalid response, {res_obj.get("success", None)}, 'f'{res_obj.get("msg", "")}')
        _LOGGER.debug('aam home api post, %s%s, %s -> %s', self._base_url, url_path, data, res_obj)
        return res_obj

    async def fetch_post_async(self, params: list) -> list:
        """
        params = {"midBindId": "xxxx", "cmd": cmd, "endpointId": ep, "value": value}
        """
        res_obj = await self.__api_post_async(
            url_path='/api/basic/device/ctrl',
            data={
                'params': params
            },
            timeout=15
        )
        if 'result' not in res_obj:
            raise HttpError('invalid response result')

        return res_obj['result']
