import logging
import paramiko

from homeassistant.const import Platform, CONF_ID, CONF_NAME, CONF_TYPE, CONF_DEVICES
from .const import *
from .common import *

_LOGGER = logging.getLogger(__name__)

#PLATFORMS: list[str] = [Platform.SENSOR, Platform.LIGHT, Platform.SWITCH]
PLATFORMS: list[str] = [Platform.SENSOR]

def x10_command(x10_config, command):
    """Execute X10 command and check output."""

    if (x10_config[CONFIG_USE_SSH]):
        _LOGGER.debug("Sending ssh heyu command : " + command)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # _LOGGER.debug("ssh_host:" + x10_config[CONFIG_SSH_HOST])
        # _LOGGER.debug("ssh_username:" + x10_config[CONFIG_SSH_USERNAME])
        # _LOGGER.debug("ssh_password:" + x10_config[CONFIG_SSH_PASSWORD])
    
        ssh.connect(x10_config[CONFIG_SSH_HOST], username=x10_config[CONFIG_SSH_USERNAME], password=x10_config[CONFIG_SSH_PASSWORD])

        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("heyu " + command)

        output = "".join(ssh_stdout.readlines())
        output += "".join(ssh_stderr.readlines())

        ssh.close()
    else:
        _LOGGER.debug("Sending local heyu command : " + command)
        output = check_output(["heyu", command])
        
    _LOGGER.debug("heyu reply : " + output)

    return output

def get_unit_status(x10_config,code):
    """Get on/off status for given unit."""
    
    command = "onstate "+code
    output = x10_command(x10_config,command)

    return int(output)

def common_init(self,device,x10_config):
    self._name = device["name"]
    self._attr_unique_id = "X10." + device["type"] + "." + device["id"].upper()
    self._id = device["id"].upper()
    self._state = False
    self._config = x10_config

def get_devices(x10_config,type):
    return x10_config[CONFIG_DEVICES][type] | {};
