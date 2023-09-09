"""The x10 component."""
from __future__ import annotations
from x10.zm import X10

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from homeassistant.const import (
    ATTR_ID,
    ATTR_NAME,
    Platform,
)

import logging

CONFIG_USE_SSH = "use_ssh"
CONFIG_SSH_HOST = "ssh_host"
CONFIG_SSH_USERNAME = "ssh_username"
CONFIG_SSH_PASSWORD = "ssh_password"

DOMAIN = 'x10'

HOST_CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONFIG_USE_SSH) : cv.boolean,
        vol.Optional(CONFIG_SSH_HOST): cv.string,
        vol.Optional(CONFIG_SSH_USERNAME): cv.string,
        vol.Optional(CONFIG_SSH_PASSWORD): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.All(cv.ensure_list, [HOST_CONFIG_SCHEMA])}, extra=vol.ALLOW_EXTRA
)


def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Your controller/hub specific code."""
    
    success = True

    # Data that you want to share with your platforms
    hass.data[DOMAIN] = {}

    for conf in config[DOMAIN]:
        z10_client = X10(
            conf.get(CONFIG_USE_SSH),
            conf.get(CONFIG_SSH_HOST),
            conf.get(CONFIG_SSH_USERNAME),
            conf.get(CONFIG_SSH_PASSWORD),
        )
        hass.data[DOMAIN][x10_config] = zm_client
        
    hass.helpers.discovery.load_platform('light', DOMAIN, {}, config)

    return success