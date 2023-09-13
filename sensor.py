"""Support for X10 Sensors."""
from __future__ import annotations

import logging
from subprocess import STDOUT, CalledProcessError, check_output
from typing import Any
from homeassistant.core import HomeAssistant

from homeassistant.const import CONF_ID, CONF_NAME, CONF_TYPE, CONF_DEVICES
from .const import *
from .common import *

# import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorEntity,
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
    """Set up the x10 Sensor platform."""

    x10_config = hass.data[DOMAIN]

    _LOGGER.info("Config: " + str(x10_config))

    x10_config['is_cm11a'] = True
    try:
        x10_command(x10_config,"info")
    except CalledProcessError as err:
        _LOGGER.info("Assuming that the device is CM17A: %s", err.output)
        x10_config['is_cm11a'] = False

    add_entities(X10Sensor(sensor, x10_config) for sensor in x10_config[CONF_DEVICES][TYPE_SENSOR])


class X10Sensor(SensorEntity):
    """Representation of an X10 Sensor."""

    def __init__(self, sensor, x10_config):
        """Initialize an X10 Sensor."""
        common_init(self,sensor,x10_config)

    @property
    def name(self):
        """Return the display name of this sensor."""
        return self._name

    @property
    def is_on(self):
        """Return true if sensor is on."""
        return self._state

    def update(self) -> None:
        """Fetch update state."""
        if self._config['is_cm11a']:
            self._state = bool(get_unit_status(self._config,self._id))
        else:
            # Not supported on CM17A
            pass
