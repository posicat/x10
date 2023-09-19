"""Support for X10 configuration."""
import logging
import voluptuous as vol

from typing import Any

from homeassistant import exceptions,config_entries
from homeassistant.const import CONF_BASE
from .const import *
from .common import *

from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult


_LOGGER = logging.getLogger(__name__)

async def validate_input(hass: HomeAssistant, x10_config: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    version = x10_command(x10_config,"version")
    _LOGGER.debug("'heyu version' returned : " + version)

    if not ("Version:" in version):
        raise CannotConnect
    
    info = x10_command(x10_config,"info")

    if ("Raw interface clock:" in info):
        _LOGGER.info("Device appears to be a CM11A: %s", info)
        x10_config['is_cm11a'] = True
    else:
        _LOGGER.info("Assuming that the device is CM17A: %s", info)
        x10_config['is_cm11a'] = False

def _heyu_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(CONFIG_USE_SSH): bool,
            vol.Optional(CONFIG_SSH_HOST): str,
            vol.Optional(CONFIG_SSH_USERNAME): str,
            vol.Optional(CONFIG_SSH_PASSWORD): str,
        },
    )

def _device_schema() -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(CONFIG_DEVICE_NAME): str,
            vol.Optional(CONFIG_MODULE_HOUSECODE): str,
            vol.Optional(CONFIG_MODULE_NUMBER): str,
            vol.Optional(CONFIG_MODULE_TYPE): str,
        },
    )

def generate_config_schema(x10_config):
        schema={}
        for platform in PLATFORMS:
            _LOGGER.debug("Platform : " + platform)

        return vol.Schema(schema)


class X10ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """X10 config flow."""
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1

    def __init__(self) -> None:
        """Initialize the x10 config flow."""
        self.x10_config: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors={}

        if user_input is not None:
            info, errors = await self._async_validate_or_error(user_input)

            if not errors:
                self.x10_config.update(user_input)
                self.x10_config[CONFIG_DEVICES] = {}
                self.x10_config[CONFIG_DEVICES][TYPE_LIGHT] = {}
                self.x10_config[CONFIG_DEVICES][TYPE_SWITCH] = {}
                self.x10_config[CONFIG_DEVICES][TYPE_SENSOR] = {}
                _LOGGER.debug("Save Config : " + str(self.x10_config))
                return self.async_create_entry(title=DOMAIN, data=self.x10_config)
            
            return self.async_show_form(step_id="user", data_schema=_heyu_schema(), errors=errors)

        return self.async_show_form(step_id="user", data_schema=_heyu_schema(), errors=errors)
    
    async def async_step_device(self, user_input: dict[str, Any] | None = None):
        errors={}
        if user_input is not None:
            _LOGGER.debug("user_input : " + str(user_input))

        return self.async_show_form(step_id="device", data_schema=_device_schema(), errors=errors)

    async def _async_validate_or_error(
        self, x10_config: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, str]]:
        
        errors = {}
        info = {}
        try:
            info['Version'] = await validate_input(self.hass, x10_config)
        except CannotConnect:
            errors[CONF_BASE] = "cannot_connect"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors[CONF_BASE] = "unknown"

        return info, errors
    
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for Met."""
        return X10OptionsFlowHandler(config_entry)

class X10OptionsFlowHandler(config_entries.OptionsFlow):
    VERSION = 1

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.x10_config = config_entry.data
        self._errors: dict[str, Any] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Do stuff here
            return self.async_create_entry(title=DOMAIN, data=self.x10_config)

        config_schema = generate_config_schema(self.x10_config)


        return self.async_show_form(step_id="device", data_schema=_device_schema(), errors=errors)
    
class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""