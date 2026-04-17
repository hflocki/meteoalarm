import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import CONF_API_KEY, CONF_COUNTRY, COUNTRIES, DOMAIN


class MeteoAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            country_code = user_input[CONF_COUNTRY]
            # Unique ID = Domain + Ländercode → verhindert Duplikate
            await self.async_set_unique_id(f"{DOMAIN}_{country_code}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"MeteoAlarm {COUNTRIES.get(country_code, country_code)}",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_COUNTRY, default="DE"): vol.In(COUNTRIES),
                vol.Optional(CONF_API_KEY, default=""): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MeteoAlarmOptionsFlow(config_entry)


class MeteoAlarmOptionsFlow(config_entries.OptionsFlow):
    """Ermöglicht nachträgliches Ändern des API-Keys."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_API_KEY,
                    default=self.config_entry.options.get(CONF_API_KEY, ""),
                ): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
