# -*- coding: utf-8 -*-

from typing import Any


class DdIotClient:
    """DdIot client instance."""

    async def set_prop_async(self, did: str, siid: int, piid: int, value: Any) -> bool:
        return True
