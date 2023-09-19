"""The x10 component."""
from __future__ import annotations
import voluptuous as vol

from .const import *
from .common import *

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

from homeassistant.const import Platform,CONF_ID, CONF_NAME, CONF_TYPE, CONF_DEVICES, EVENT_HOMEASSISTANT_STOP
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
    """Set up x10 from a config entry."""

    x10_config = entry.data
    _LOGGER.debug("async_setup_entry x10_config : " + str(x10_config))

    # x10_process = X10_Process(hass, x10_config)

    # async def async_shutdown(event):
    #         # Handle shutdown
    #         await x10_config[X10_PROCESS].stop()

    # hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, async_shutdown)

    # x10_config[X10_PROCESS] = x10_process

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

class X10_Process:
      
    def __init__(self, hass : HomeAssistant, properties):
        self._hass = hass
        self._properties = properties
        self._callbacks = set()

        _LOGGER.debug("__init__ _properties : " + str(properties))

        # self._x10 = X10_Start_Monitor(properties.get(ATTR_DEVICE_PATH, ""), properties.get(CONF_HOST, ""), properties.get(CONF_PORT, 0))        
        # self._x10.register_process_callback(self._process_update)

        # self._heyu_monitor = self._hass.loop.create_task(self._x10.heyu_monitor_read())

    async def stop(self):
        # self._heyu_monitor.cancel()

        await self._x10.close()

    def _process_update(self, type, response) -> None:
        LOGGER.debug("_process_update self : " + str(self.x10_config))