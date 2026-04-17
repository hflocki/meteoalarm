from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COUNTRIES, DOMAIN, SEVERITY_ORDER


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Wir brauchen kein 'country' mehr aus den entry.data
    async_add_entities(
        [
            MeteoAlarmLevelSensor(coordinator, entry),
            MeteoAlarmDetailSensor(coordinator, entry),
        ]
    )


class MeteoAlarmBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._entry.entry_id)},
            "name": "Geo Weather Alarms",
            "manufacturer": "EUMETNET",
            "model": "MeteoAlarm EDR API",
        }


class MeteoAlarmCountSensor(MeteoAlarmBaseSensor):
    _attr_icon = "mdi:weather-lightning"
    _attr_native_unit_of_measurement = "Warnungen"

    @property
    def unique_id(self):
        return f"meteoalarm_{self._country}_count"

    @property
    def name(self):
        return f"MeteoAlarm {self._country_name} Aktive Warnungen"

    @property
    def native_value(self):
        if self.coordinator.data:
            return len(self.coordinator.data.get("warnungen", []))
        return 0

    @property
    def icon(self):
        val = self.native_value
        if val and val > 0:
            return "mdi:weather-lightning"
        return "mdi:shield-check"


class MeteoAlarmLevelSensor(MeteoAlarmBaseSensor):
    @property
    def unique_id(self):
        return f"meteoalarm_{self._country}_level"

    @property
    def name(self):
        return f"MeteoAlarm {self._country_name} Höchste Stufe"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return "Keine"
        warnungen = self.coordinator.data.get("warnungen", [])
        if not warnungen:
            return "Keine"
        return max(
            (w.get("stufe", "Minor") for w in warnungen),
            key=lambda s: SEVERITY_ORDER.get(s, 0),
            default="Keine",
        )

    @property
    def icon(self):
        lvl = self.native_value
        icons = {
            "Extreme": "mdi:alert-octagon",
            "Severe": "mdi:alert",
            "Moderate": "mdi:alert-circle-outline",
            "Minor": "mdi:information-outline",
        }
        return icons.get(lvl, "mdi:shield-check")

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        return {"land": self.coordinator.data.get("land", self._country)}


class MeteoAlarmDetailSensor(MeteoAlarmBaseSensor):
    _attr_icon = "mdi:format-list-bulleted"

    @property
    def unique_id(self):
        return f"meteoalarm_{self._country}_details"

    @property
    def name(self):
        return f"MeteoAlarm {self._country_name} Details"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return "Keine Daten"
        warnungen = self.coordinator.data.get("warnungen", [])
        if not warnungen:
            return "Keine Warnungen"
        return warnungen[0].get("titel", "Warnung aktiv")

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        data = self.coordinator.data
        return {
            "warnungen": data.get("warnungen", []),
            "anzahl_gesamt_api": data.get("gesamt_api", 0),
            "land": data.get("land", self._country),
        }
