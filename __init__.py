"""The x10 component."""
from __future__ import annotations
import voluptuous as vol

from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
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
CONFIG_DEVICES = "devices"
CONFIG_ID = "id"
CONFIG_TYPE = "type"
CONFIG_NAME = "name"

DOMAIN = 'x10'

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONFIG_ID): cv.string,
        vol.Required(CONFIG_TYPE): cv.string,
        vol.Required(CONFIG_NAME): cv.string,
    },
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONFIG_USE_SSH): cv.boolean,
                vol.Optional(CONFIG_SSH_HOST): cv.string,
                vol.Optional(CONFIG_SSH_USERNAME): cv.string,
                vol.Optional(CONFIG_SSH_PASSWORD): cv.string,
                vol.Optional(CONFIG_DEVICES): vol.Schema(DEVICE_SCHEMA),
            }
        )
    },
)

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Your controller/hub specific code."""
    
    success = True

    # Data that you want to share with your platforms
    hass.data[DOMAIN] = {}

    for conf in config[DOMAIN]:
        hass.data[DOMAIN][CONFIG_USE_SSH] = conf.get(CONFIG_USE_SSH),
        hass.data[DOMAIN][CONFIG_SSH_HOST] = conf.get(CONFIG_SSH_HOST),
        hass.data[DOMAIN][CONFIG_SSH_USERNAME] = conf.get(CONFIG_SSH_USERNAME),
        hass.data[DOMAIN][CONFIG_SSH_PASSWORD] = conf.get(CONFIG_SSH_PASSWORD),

    logger.debug(hass.data[DOMAIN])
       
    hass.helpers.discovery.load_platform('light', DOMAIN, {}, config)

    return success