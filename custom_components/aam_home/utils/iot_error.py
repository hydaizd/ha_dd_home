# -*- coding: utf-8 -*-

from enum import Enum
from typing import Any


class IotErrorCode(Enum):
    """Iot error code."""
    # Base error code
    CODE_UNKNOWN = -10000

    # Http error code
    CODE_HTTP_INVALID_ACCESS_TOKEN = -10030

    CODE_MIPS_INVALID_RESULT = -10040


class IotError(Exception):
    """Iot error."""
    code: IotErrorCode
    message: Any

    def __init__(
            self, message: Any, code: IotErrorCode = IotErrorCode.CODE_UNKNOWN
    ) -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)

    def to_str(self) -> str:
        return f'{{"code":{self.code.value},"message":"{self.message}"}}'

    def to_dict(self) -> dict:
        return {"code": self.code.value, "message": self.message}


class HttpError(IotError):
    ...


class IoTClientError(IotError):
    ...
