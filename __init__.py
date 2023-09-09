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

_LOGGER = logging.getLogger(__name__)

from .const import DOMAIN, CONFIG_USE_SSH, CONFIG_SSH_HOST, CONFIG_SSH_USERNAME, CONFIG_SSH_PASSWORD
from homeassistant.const import CONF_ID, CONF_NAME, CONF_TYPE, CONF_DEVICES

DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ID): cv.string,
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_TYPE): cv.string,
    },
)
X10_SCHEMA = vol.Schema(
    {
        vol.Required(CONFIG_USE_SSH): cv.boolean,
        vol.Optional(CONFIG_SSH_HOST): cv.string,
        vol.Optional(CONFIG_SSH_USERNAME): cv.string,
        vol.Optional(CONFIG_SSH_PASSWORD): cv.string,
        vol.Optional(CONF_DEVICES): vol.All(
            cv.ensure_list, [DEVICE_SCHEMA]
        ),
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(DOMAIN): vol.All(
            cv.ensure_list, [X10_SCHEMA]
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Your controller/hub specific code."""
    
    success = True

    # Data that you want to share with your platforms
    hass.data[DOMAIN] = {}
    x10_config = {}
    
    for conf in config[DOMAIN]:
        x10_config[CONFIG_USE_SSH] = conf.get(CONFIG_USE_SSH)
        x10_config[CONFIG_SSH_HOST] = conf.get(CONFIG_SSH_HOST)
        x10_config[CONFIG_SSH_USERNAME] = conf.get(CONFIG_SSH_USERNAME)
        x10_config[CONFIG_SSH_PASSWORD] = conf.get(CONFIG_SSH_PASSWORD)
        x10_config[CONF_DEVICES] = conf.get(CONF_DEVICES)

    hass.data[DOMAIN] = x10_config;
    _LOGGER.debug("Domain: " + str(hass.data[DOMAIN]))
       
    hass.helpers.discovery.load_platform('light', DOMAIN, {}, config)

    return success