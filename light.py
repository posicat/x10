"""Support for X10 lights."""
from __future__ import annotations

import logging
import paramiko
from subprocess import STDOUT, CalledProcessError, check_output
from typing import Any

from .const import DOMAIN, CONFIG_USE_SSH, CONFIG_SSH_HOST, CONFIG_SSH_USERNAME, CONFIG_SSH_PASSWORD
from homeassistant.const import CONF_ID, CONF_NAME, CONF_TYPE

import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
)
from homeassistant.const import CONF_DEVICES, CONF_ID, CONF_NAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_DEVICES): vol.All(
            cv.ensure_list,
            [{vol.Required(CONF_ID): cv.string, vol.Required(CONF_NAME): cv.string}],
        )
    }
)

def x10_command(x10_config, command):
    """Execute X10 command and check output."""
    cmd = "heyu "+command
    _LOGGER.info("x10_command:" + cmd)

###x10_config[use_ssh]
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # _LOGGER.info("ssh_host:" + x10_config[CONFIG_SSH_HOST])
    # _LOGGER.info("ssh_username:" + x10_config[CONFIG_SSH_USERNAME])
    # _LOGGER.info("ssh_password:" + x10_config[CONFIG_SSH_PASSWORD])
    
    ssh.connect(x10_config[CONFIG_SSH_HOST], username=x10_config[CONFIG_SSH_USERNAME], password=x10_config[CONFIG_SSH_PASSWORD])
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)

    output = "".join(ssh_stdout.readlines())
    output += "".join(ssh_stderr.readlines())
    output = output.replace("[\n]+","\n")
    ssh.close()

    _LOGGER.info("output:" + output)
    return output

def get_unit_status(x10_config,code):
    """Get on/off status for given unit."""
    cmd = "heyu onstate "+code
    _LOGGER.info("x10_command:" + cmd)

###x10_config[use_ssh]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # _LOGGER.info("ssh_host:" + x10_config[CONFIG_SSH_HOST])
    # _LOGGER.info("ssh_username:" + x10_config[CONFIG_SSH_USERNAME])
    # _LOGGER.info("ssh_password:" + x10_config[CONFIG_SSH_PASSWORD])
    
    ssh.connect(x10_config[CONFIG_SSH_HOST], username=x10_config[CONFIG_SSH_USERNAME], password=x10_config[CONFIG_SSH_PASSWORD])
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)

    output = "".join(ssh_stdout.readlines())
    output += "".join(ssh_stderr.readlines())
    output = output.replace("[\n]+","\n")
    _LOGGER.info("output:" + output)

    ssh.close()

    return int(output)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the x10 Light platform."""

    x10_config = hass.data[DOMAIN]

    _LOGGER.info("Config: " + str(x10_config))

    x10_config['is_cm11a'] = True
    try:
        x10_command(x10_config,"info")
    except CalledProcessError as err:
        _LOGGER.info("Assuming that the device is CM17A: %s", err.output)
        x10_config['is_cm11a'] = False

    add_entities(X10Light(light, x10_config) for light in x10_config[CONF_DEVICES])


class X10Light(LightEntity):
    """Representation of an X10 Light."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, light, x10_config):
        """Initialize an X10 Light."""
        self._name = light["name"]
        self._id = light["id"].upper()
        self._brightness = 0
        self._state = False
        self._config = x10_config
        self._attr_unique_id = "X10."+ light["id"].upper()

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
