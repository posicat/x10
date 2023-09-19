"""Support for X10 switches."""
from __future__ import annotations

import logging
from subprocess import STDOUT, CalledProcessError, check_output
from typing import Any
from homeassistant.core import HomeAssistant

from homeassistant.const import CONF_ID, CONF_NAME, CONF_TYPE, CONF_DEVICES
from .const import *
from .common import *

# import voluptuous as vol

from homeassistant.components.switch import (
    PLATFORM_SCHEMA,
    SwitchEntity,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    x10_config = entry.data

    switches = get_devices(x10_config,Platform.SWITCH)
    _LOGGER.debug("async_setup_entry " + str(switches))

    async_add_entities(X10Switch(switch, x10_config) for switch in switches)

class X10Switch(SwitchEntity):
    """Representation of an X10 Switch."""

    def __init__(self, switch, x10_config):
        """Initialize an X10 Switch."""
        common_init(self,switch,x10_config)

    @property
    def name(self):
        """Return the display name of this switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the switch to turn on."""
        if self._config['is_cm11a']:
            x10_command(self._config,f"on {self._id}")
        else:
            x10_command(self._config,f"fon {self._id}")
        self._state = True

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the switch to turn off."""
        if self._config['is_cm11a']:
            x10_command(self._config,f"off {self._id}")
        else:
            x10_command(self._config,f"foff {self._id}")
        self._state = False

    def update(self) -> None:
        """Fetch update state."""
        if self._config['is_cm11a']:
            self._state = bool(get_unit_status(self._config,self._id))
        else:
            # Not supported on CM17A
            pass
