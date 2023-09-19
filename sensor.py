"""Support for X10 Sensors."""
from __future__ import annotations

import logging
import json 

from subprocess import STDOUT, CalledProcessError, check_output
from typing import Any
from homeassistant.core import HomeAssistant

from homeassistant.const import Platform, CONF_ID, CONF_NAME, CONF_TYPE, CONF_DEVICES
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

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
):
    """Setup sensors from a config entry created in the integrations UI."""
    x10_config = entry.data

    sensors = get_devices(x10_config,Platform.SENSOR)
    _LOGGER.debug("async_setup_entry " + str(sensors))

    async_add_entities(X10Sensor(sensor, x10_config) for sensor in sensors)


class X10Sensor(SensorEntity):
    """Representation of an X10 Sensor."""

    def __init__(self, sensor, x10_config):
        """Initialize an X10 Sensor."""
        _LOGGER.debug("__init__ " + str(sensor))
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
