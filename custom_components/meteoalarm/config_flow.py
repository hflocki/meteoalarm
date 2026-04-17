import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

# Wichtig: Alle Konstanten müssen hier importiert werden
from .const import CONF_API_KEY, CONF_COUNTRY, COUNTRIES, DOMAIN

class MeteoAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MeteoAlarm."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            country_code = user_input[CONF_COUNTRY]
            # Unique ID verhindert, dass das gleiche Land doppelt hinzugefügt wird
            await self.async_set_unique_id(f"{DOMAIN}_{country_code}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"MeteoAlarm {COUNTRIES.get(country_code, country_code)}",
                data=user_input,
            )

        # Das Formular für den User
        schema = vol.Schema(
            {
                vol.Required(CONF_COUNTRY, default="DE"): vol.In(COUNTRIES),
                vol.Required(CONF_API_KEY): str, # Required, da 401 Fehler ohne Key
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
        """Ermöglicht das Ändern des Keys über 'Konfigurieren'."""
        return MeteoAlarmOptionsFlow(config_entry)


class MeteoAlarmOptionsFlow(config_entries.OptionsFlow):
    """Optionen-Dialog für nachträgliche Änderungen."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        # Nur EINE Init-Methode mit Unterstrich, um den Property-Fehler zu vermeiden
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_API_KEY,
                    default=self._config_entry.data.get(CONF_API_KEY, ""),
                ): str,
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
