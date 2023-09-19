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

from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    SelectOptionDict
)

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
            vol.Required(CONFIG_DEVICE_NAME): str,
            vol.Required(CONFIG_MODULE_HOUSECODE): 
                SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value="A", label="A"),
                            SelectOptionDict(value="B", label="B"),
                            SelectOptionDict(value="C", label="C"),
                            SelectOptionDict(value="D", label="D"),
                            SelectOptionDict(value="E", label="E"),
                            SelectOptionDict(value="F", label="F"),
                            SelectOptionDict(value="G", label="G"),
                            SelectOptionDict(value="H", label="H"),
                            SelectOptionDict(value="I", label="I"),
                            SelectOptionDict(value="J", label="J"),
                            SelectOptionDict(value="K", label="K"),
                            SelectOptionDict(value="L", label="L"),
                            SelectOptionDict(value="M", label="M"),
                            SelectOptionDict(value="N", label="N"),
                            SelectOptionDict(value="O", label="O"),
                            SelectOptionDict(value="P", label="P"),
                        ]
                    )
                ),
            vol.Required(CONFIG_MODULE_NUMBER) : 
                SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value="1", label="1"),
                            SelectOptionDict(value="2", label="2"),
                            SelectOptionDict(value="3", label="3"),
                            SelectOptionDict(value="4", label="4"),
                            SelectOptionDict(value="5", label="5"),
                            SelectOptionDict(value="6", label="6"),
                            SelectOptionDict(value="7", label="7"),
                            SelectOptionDict(value="8", label="8"),
                            SelectOptionDict(value="9", label="9"),
                            SelectOptionDict(value="10", label="10"),
                            SelectOptionDict(value="11", label="11"),
                            SelectOptionDict(value="12", label="12"),
                            SelectOptionDict(value="13", label="13"),
                            SelectOptionDict(value="14", label="14"),
                            SelectOptionDict(value="15", label="15"),
                            SelectOptionDict(value="16", label="16"),
                        ]
                    ),
                ),
            vol.Required(CONFIG_MODULE_TYPE): 
                SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(value=TYPE_LIGHT, label="Light"),
                            SelectOptionDict(value=TYPE_SWITCH, label="Switch"),
                            SelectOptionDict(value=TYPE_APPLIANCE, label="Appliance"),
                            SelectOptionDict(value=TYPE_SENSOR, label="Sensor")
                        ],
                        mode=SelectSelectorMode.DROPDOWN
                    )
                ) 
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
                self.x10_config[CONFIG_DEVICES][TYPE_LIGHT] = []
                self.x10_config[CONFIG_DEVICES][TYPE_SWITCH] = []
                self.x10_config[CONFIG_DEVICES][TYPE_SENSOR] = []
                _LOGGER.debug("Save Config : " + str(self.x10_config))
                return self.async_create_entry(title=DOMAIN, data=self.x10_config)
            
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


    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = {}
        """Manage the options."""
        if user_input is not None:
            _LOGGER.debug("asi" + str(user_input))
            return self.async_create_entry(title=DOMAIN, data=self.x10_config)

        config_schema = generate_config_schema(self.x10_config)

        return await self.async_step_configMenu({})

        return self.async_show_form(step_id="init", data_schema=generate_config_schema(self.x10_config), errors=errors)

    async def async_step_configMenu(self, user_input=None):
        return self.async_show_menu(
            step_id="configMenu",
            menu_options=["addDevice", "editDevice"]
        )

    async def async_step_addDevice(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = {}
        """Manage the options."""
        if user_input is not None:
            _LOGGER.debug("asaD" + str(user_input))

            devices = self.x10_config[CONFIG_DEVICES][user_input[CONFIG_MODULE_TYPE]]

            for device in devices:
                _LOGGER.debug("asaD device" + str(device))

                if (device[CONFIG_MODULE_HOUSECODE] == user_input[CONFIG_MODULE_HOUSECODE] 
                    and device[CONFIG_MODULE_NUMBER] == user_input[CONFIG_MODULE_NUMBER]):
                    _LOGGER.debug("Module already exists " + str(device))
                    errors["update"] = "Module already exists"
                    return
    
            add_device(self.x10_config,user_input)
            return self.async_create_entry(title=DOMAIN, data=self.x10_config)

        return self.async_show_form(step_id="addDevice", data_schema=_device_schema(), errors=errors)

    async def async_step_editDevice(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors = {}
        """Manage the options."""
        if user_input is not None:
            _LOGGER.debug("aseD" + str(user_input))
            return self.async_create_entry(title=DOMAIN, data=self.x10_config)

        config_schema = _device_schema()

        return self.async_show_form(step_id="editDevice", data_schema=generate_device_list(self.x10_config), errors=errors)
    
class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""