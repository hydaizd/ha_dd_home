# -*- coding: utf-8 -*-

DOMAIN: str = "dd_home"

#　定义集成支持的平台
SUPPORTED_PLATFORMS: list = [
    "switch",
]

# Keys for values used in the config_entry data dictionary
CONF_DEVICE_NAME = "name"
CONF_DEVICE_ID = "mid_bind_id"
CONF_DEVICE_TYPE = "product_type"
CONF_DEVICE_SKU = "sku_id"


CONF_HARDWARE = "hardware"
DEFAULT_PORT = 80

# Http api
HTTP_API_TIMEOUT: int = 30
