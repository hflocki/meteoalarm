import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_COUNTRIES,
    CONF_GEOLOCATOR_ENTITY,
    CONF_MODE,
    COUNTRIES,
    DEFAULT_GEOLOCATOR_ENTITY,
    DOMAIN,
    MODE_GEOLOCATOR,
    MODE_MANUAL,
)

COUNTRY_OPTIONS = [
    {"value": k, "label": f"{k.upper()} – {v}"}
    for k, v in sorted(COUNTRIES.items(), key=lambda x: x[1])
]

MODE_OPTIONS = [
    {"value": MODE_MANUAL, "label": "Manuell – Länder selbst auswählen"},
    {"value": MODE_GEOLOCATOR, "label": "GeoLocator – Land automatisch vom Sensor"},
]


def _manual_schema(default=None):
    return vol.Schema(
        {
            vol.Required(
                CONF_COUNTRIES, default=default or []
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=COUNTRY_OPTIONS,
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            ),
        }
    )


def _geolocator_schema(default_entity=None):
    return vol.Schema(
        {
            vol.Required(
                CONF_GEOLOCATOR_ENTITY,
                default=default_entity or DEFAULT_GEOLOCATOR_ENTITY,
            ): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        }
    )


class MeteoAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._mode = None

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._mode = user_input[CONF_MODE]
            if self._mode == MODE_GEOLOCATOR:
                return await self.async_step_geolocator()
            return await self.async_step_manual()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MODE, default=MODE_MANUAL
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=MODE_OPTIONS,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                }
            ),
        )

    async def async_step_manual(self, user_input=None):
        errors = {}
        if user_input is not None:
            if not user_input.get(CONF_COUNTRIES):
                errors[CONF_COUNTRIES] = "no_countries"
            else:
                return self.async_create_entry(
                    title="MeteoAlarm (Manuell)",
                    data={CONF_MODE: MODE_MANUAL, **user_input},
                )
        return self.async_show_form(
            step_id="manual", data_schema=_manual_schema(), errors=errors
        )

    async def async_step_geolocator(self, user_input=None):
        errors = {}
        if user_input is not None:
            entity_id = user_input.get(CONF_GEOLOCATOR_ENTITY, "").strip()
            # BUG FIX: Nur prüfen ob entity_id nicht leer - EntitySelector
            # stellt sicher dass die Entity in HA existiert. Kein State-Check
            # nötig (Sensor kann beim Setup "unavailable" sein).
            if not entity_id:
                errors[CONF_GEOLOCATOR_ENTITY] = "entity_not_found"
            else:
                return self.async_create_entry(
                    title="MeteoAlarm (GeoLocator)",
                    data={CONF_MODE: MODE_GEOLOCATOR, **user_input},
                )
        return self.async_show_form(
            step_id="geolocator",
            data_schema=_geolocator_schema(),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MeteoAlarmOptionsFlow()


class MeteoAlarmOptionsFlow(config_entries.OptionsFlow):
    # BUG FIX: Kein __init__ der self.config_entry manuell setzt –
    # HA setzt self.config_entry automatisch (seit HA 2024.x).
    # Manuelles Setzen ist deprecated und kann zu Fehlern führen.

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            mode = user_input[CONF_MODE]
            if mode == MODE_GEOLOCATOR:
                return await self.async_step_geolocator()
            return await self.async_step_manual()

        cfg = self.config_entry.options or self.config_entry.data
        current_mode = cfg.get(CONF_MODE, MODE_MANUAL)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MODE, default=current_mode
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=MODE_OPTIONS,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                }
            ),
        )

    async def async_step_manual(self, user_input=None):
        errors = {}
        cfg = self.config_entry.options or self.config_entry.data
        if user_input is not None:
            if not user_input.get(CONF_COUNTRIES):
                errors[CONF_COUNTRIES] = "no_countries"
            else:
                return self.async_create_entry(
                    title="", data={CONF_MODE: MODE_MANUAL, **user_input}
                )
        return self.async_show_form(
            step_id="manual",
            data_schema=_manual_schema(default=list(cfg.get(CONF_COUNTRIES, []))),
            errors=errors,
        )

    async def async_step_geolocator(self, user_input=None):
        errors = {}
        cfg = self.config_entry.options or self.config_entry.data
        if user_input is not None:
            entity_id = user_input.get(CONF_GEOLOCATOR_ENTITY, "").strip()
            if not entity_id:
                errors[CONF_GEOLOCATOR_ENTITY] = "entity_not_found"
            else:
                return self.async_create_entry(
                    title="", data={CONF_MODE: MODE_GEOLOCATOR, **user_input}
                )
        return self.async_show_form(
            step_id="geolocator",
            data_schema=_geolocator_schema(
                default_entity=cfg.get(
                    CONF_GEOLOCATOR_ENTITY, DEFAULT_GEOLOCATOR_ENTITY
                )
            ),
            errors=errors,
        )
