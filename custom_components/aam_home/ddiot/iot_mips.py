# -*- coding: utf-8 -*-

import asyncio
from typing import Any, Callable, Optional, final, Coroutine


class MipsLocalClient():
    """MIoT Pub/Sub Local Client."""

    def __init__(
        self,
        did: str,
        host: str,
        group_id: str,
        ca_file: str,
        cert_file: str,
        key_file: str,
        port: int = 8883,
        home_name: str = "",
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._did = did

        super().__init__(
            client_id=did,
            host=host,
            port=port,
            ca_file=ca_file,
            cert_file=cert_file,
            key_file=key_file,
            loop=loop,
        )

    @final
    async def set_prop_async(
        self, did: str, siid: int, piid: int, value: Any, timeout_ms: int = 10000
    ) -> dict:
        return {
            "code": 0,
            "message": "Invalid result",
        }

    @final
    async def get_dev_list_async(
        self, payload: Optional[str] = None, timeout_ms: int = 10000
    ) -> dict[str, dict]:
        """获取设备列表."""

        device_list = {}

        return device_list
