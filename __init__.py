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

from homeassistant.const import CONF_ID, CONF_NAME, CONF_TYPE, CONF_DEVICES
from .const import *
from .common import *

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

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hello World from a config entry."""
    # Store an instance of the "connecting" class that does the work of speaking
    # with your actual devices.

    e=entry
    h=hass

    _LOGGER.debug("Entry : " + str(e))
    _LOGGER.debug("hass : " + str(h))

    return True

def setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Your controller/hub specific code."""
    
    success = True

    # Data that you want to share with your platforms
    hass.data[DOMAIN] = {}
    x10_config = {}
    x10_config[CONF_DEVICES] = {}
    
    for conf in config[DOMAIN]:
        x10_config[CONFIG_USE_SSH] = conf.get(CONFIG_USE_SSH)
        x10_config[CONFIG_SSH_HOST] = conf.get(CONFIG_SSH_HOST)
        x10_config[CONFIG_SSH_USERNAME] = conf.get(CONFIG_SSH_USERNAME)
        x10_config[CONFIG_SSH_PASSWORD] = conf.get(CONFIG_SSH_PASSWORD)
        for device in conf.get(CONF_DEVICES):
            type = device[CONF_TYPE]

            if (type == TYPE_APPLIANCE): # X10 calls them appliances, in HA they're switches
                type = TYPE_SWITCH
            if (not type in x10_config[CONF_DEVICES]):
                x10_config[CONF_DEVICES][type] = []

            x10_config[CONF_DEVICES][type].append(device)

    hass.data[DOMAIN] = x10_config;
    # _LOGGER.debug("Domain: " + str(hass.data[DOMAIN]))
    
    hass.helpers.discovery.load_platform('sensor', DOMAIN, {}, config)
    hass.helpers.discovery.load_platform('light', DOMAIN, {}, config)
    hass.helpers.discovery.load_platform('switch', DOMAIN, {}, config)
       
    return success