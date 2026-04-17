import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

# Stelle sicher, dass CONF_COUNTRY und COUNTRIES hier importiert werden
from .const import CONF_API_KEY, CONF_COUNTRY, COUNTRIES, DOMAIN


class MeteoAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # Land-Code extrahieren für die Unique ID
            c_code = user_input[CONF_COUNTRY]
            await self.async_set_unique_id(f"{DOMAIN}_{c_code}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"MeteoAlarm {c_code}", data=user_input
            )

        # Das Schema zeigt die Länderliste und das API-Key Feld
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_COUNTRY, default="DE"): vol.In(COUNTRIES),
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MeteoAlarmOptionsFlow(config_entry)


class MeteoAlarmOptionsFlow(config_entries.OptionsFlow):
    """Ermöglicht nachträgliches Ändern des API-Keys."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        # Nur eine Zuweisung mit Unterstrich, um Property-Fehler zu vermeiden
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Optionen verwalten."""
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
