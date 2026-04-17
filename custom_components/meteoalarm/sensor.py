from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    """Setzt den Sensor basierend auf dem Config Entry auf."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MeteoAlarmSensor(coordinator, entry)])

class MeteoAlarmSensor(CoordinatorEntity, SensorEntity):
    """Haupt-Sensor für MeteoAlarm Warnungen."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_name = f"MeteoAlarm {entry.title}"
        self._attr_unique_id = f"{entry.entry_id}_warnings"
        self._attr_icon = "mdi:alert-decagram"

    @property
    def state(self):
        """Gibt die Anzahl der aktuellen Warnungen zurück."""
        return self.coordinator.data.get("count", 0)

    @property
    def extra_state_attributes(self):
        """Schreibt die Details der Warnungen in die Attribute."""
        return {
            "warnungen": self.coordinator.data.get("warnungen", []),
            "standort": self.coordinator.data.get("location"),
            "letztes_update": self.coordinator.last_update_success_time
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
