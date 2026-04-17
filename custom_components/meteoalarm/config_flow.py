import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import COUNTRIES, DOMAIN


class MeteoAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Konfigurationsfluss für MeteoAlarm RSS."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="MeteoAlarm Überwachung", data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("countries"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                {"value": k, "label": v} for k, v in COUNTRIES.items()
                            ],
                            multiple=True,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                }
            ),
        )
