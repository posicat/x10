"""Support for X10 lights."""
from __future__ import annotations

import logging
from subprocess import STDOUT, CalledProcessError, check_output
from typing import Any
from homeassistant.core import HomeAssistant

from homeassistant.const import CONF_ID, CONF_NAME, CONF_TYPE, CONF_DEVICES
from .const import *
from .common import *

# import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities,
):
    """Setup lights from a config entry created in the integrations UI."""
    x10_config=hass.data[DOMAIN]

    _LOGGER.info("Config: " + str(x10_config))

    # session = async_get_clientsession(hass)


    add_entities(X10Light(light, x10_config) for light in x10_config[CONF_DEVICES][TYPE_LIGHT])


class X10Light(LightEntity):
    """Representation of an X10 Light."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, light, x10_config):
        """Initialize an X10 Light."""
        common_init(self,light,x10_config)
        self._brightness = 0

    @property
    def name(self):
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        if self._config['is_cm11a']:
            x10_command(self._config,f"on {self._id}")
        else:
            x10_command(self._config,f"fon {self._id}")
        self._brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        self._state = True

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
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
