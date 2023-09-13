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

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the x10 switch platform."""

    x10_config = hass.data[DOMAIN]

    _LOGGER.info("Config: " + str(x10_config))

    x10_config['is_cm11a'] = True
    try:
        x10_command(x10_config,"info")
    except CalledProcessError as err:
        _LOGGER.info("Assuming that the device is CM17A: %s", err.output)
        x10_config['is_cm11a'] = False

    add_entities(X10Switch(switch, x10_config) for switch in x10_config[CONF_DEVICES][TYPE_SWITCH])


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
