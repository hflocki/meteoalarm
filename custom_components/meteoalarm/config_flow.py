import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from .const import (
    CONF_COUNTRIES, CONF_GEOLOCATOR_ENTITY, CONF_MODE,
    COUNTRIES, DEFAULT_GEOLOCATOR_ENTITY, DOMAIN,
    MODE_GEOLOCATOR, MODE_MANUAL,
)

COUNTRY_OPTIONS = [
    {"value": k, "label": f"{k.upper()} – {v}"}
    for k, v in sorted(COUNTRIES.items(), key=lambda x: x[1])
]

MODE_OPTIONS = [
    {"value": MODE_MANUAL,     "label": "Manuell – Länder selbst auswählen"},
    {"value": MODE_GEOLOCATOR, "label": "GeoLocator – Land automatisch vom Sensor"},
]


def _manual_schema(default=None):
    return vol.Schema({
        vol.Required(CONF_COUNTRIES, default=default or []): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=COUNTRY_OPTIONS, multiple=True,
                mode=selector.SelectSelectorMode.LIST,
            )
        ),
    })


def _geolocator_schema(default_entity=None):
    return vol.Schema({
        vol.Required(CONF_GEOLOCATOR_ENTITY, default=default_entity or DEFAULT_GEOLOCATOR_ENTITY):
            selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
    })


class MeteoAlarmConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        self._mode = None

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._mode = user_input[CONF_MODE]
            return await (self.async_step_geolocator() if self._mode == MODE_GEOLOCATOR
                          else self.async_step_manual())
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_MODE, default=MODE_MANUAL): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=MODE_OPTIONS,
                                                  mode=selector.SelectSelectorMode.LIST)
                ),
            }),
        )

    async def async_step_manual(self, user_input=None):
        errors = {}
        if user_input is not None:
            if not user_input.get(CONF_COUNTRIES):
                errors[CONF_COUNTRIES] = "no_countries"
            else:
                return self.async_create_entry(
                    title="MeteoAlarm Wetterwarnungen",
                    data={CONF_MODE: MODE_MANUAL, **user_input},
                )
        return self.async_show_form(step_id="manual", data_schema=_manual_schema(), errors=errors)

    async def async_step_geolocator(self, user_input=None):
        errors = {}
        if user_input is not None:
            if not self.hass.states.get(user_input.get(CONF_GEOLOCATOR_ENTITY, "")):
                errors[CONF_GEOLOCATOR_ENTITY] = "entity_not_found"
            else:
                return self.async_create_entry(
                    title="MeteoAlarm (GeoLocator)",
                    data={CONF_MODE: MODE_GEOLOCATOR, **user_input},
                )
        return self.async_show_form(step_id="geolocator", data_schema=_geolocator_schema(), errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        return MeteoAlarmOptionsFlow(config_entry)


class MeteoAlarmOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        cfg = self.config_entry.options or self.config_entry.data
        current_mode = cfg.get(CONF_MODE, MODE_MANUAL)
        if user_input is not None:
            mode = user_input[CONF_MODE]
            return await (self.async_step_geolocator() if mode == MODE_GEOLOCATOR
                          else self.async_step_manual())
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_MODE, default=current_mode): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=MODE_OPTIONS,
                                                  mode=selector.SelectSelectorMode.LIST)
                ),
            }),
        )

    async def async_step_manual(self, user_input=None):
        cfg = self.config_entry.options or self.config_entry.data
        errors = {}
        if user_input is not None:
            if not user_input.get(CONF_COUNTRIES):
                errors[CONF_COUNTRIES] = "no_countries"
            else:
                return self.async_create_entry(title="", data={CONF_MODE: MODE_MANUAL, **user_input})
        return self.async_show_form(
            step_id="manual",
            data_schema=_manual_schema(default=list(cfg.get(CONF_COUNTRIES, []))),
            errors=errors,
        )

    async def async_step_geolocator(self, user_input=None):
        cfg = self.config_entry.options or self.config_entry.data
        errors = {}
        if user_input is not None:
            if not self.hass.states.get(user_input.get(CONF_GEOLOCATOR_ENTITY, "")):
                errors[CONF_GEOLOCATOR_ENTITY] = "entity_not_found"
            else:
                return self.async_create_entry(title="", data={CONF_MODE: MODE_GEOLOCATOR, **user_input})
        return self.async_show_form(
            step_id="geolocator",
            data_schema=_geolocator_schema(default_entity=cfg.get(CONF_GEOLOCATOR_ENTITY, DEFAULT_GEOLOCATOR_ENTITY)),
            errors=errors,
        )
