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

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    _LOGGER.debug("Config : " + str(x10_config))
    version = x10_command(x10_config,"version")
    _LOGGER.debug("'heyu version' returned : " + version)

    if ("Version:" in version):
        return version
    else:
        raise CannotConnect



class X10ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """X10 config flow."""
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1

    def __init__(self) -> None:
        """Initialize the nut config flow."""
        self.x10_config: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            info, errors = await self._async_validate_or_error(user_input)

            if not errors:
                self.x10_config.update(user_input)
                _LOGGER.debug("Config : " + str(self.x10_config))
                return self.async_create_entry(title="x10", data=self.x10_config)
            
            return self.async_show_form(
                step_id="ups",
                data_schema=_ups_schema(self.ups_list or {}),
                errors=errors,
        )

        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(
                {
                    vol.Optional(CONFIG_USE_SSH): bool,
                    vol.Optional(CONFIG_SSH_HOST): str,
                    vol.Optional(CONFIG_SSH_USERNAME): str,
                    vol.Optional(CONFIG_SSH_PASSWORD): str,
                }
            )
        )
    
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
    
class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""