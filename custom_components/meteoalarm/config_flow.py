import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_API_KEY, DOMAIN


class MeteoAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Geo Weather Alarms."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="Geo Weather Alarms",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MeteoAlarmOptionsFlow(config_entry)


class MeteoAlarmOptionsFlow(config_entries.OptionsFlow):
    """Ermöglicht nachträgliches Ändern des API-Keys."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        # Wir speichern den config_entry in einer privaten Variable,
        # um den AttributeError (no setter) zu vermeiden.
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_API_KEY,
                        default=self._config_entry.data.get(CONF_API_KEY, ""),
                    ): str,
                }
            ),
        )
