from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COUNTRIES, DOMAIN, SEVERITY_LABELS


async def async_setup_entry(hass, entry, async_add_entities):
    coordinators = hass.data[DOMAIN][entry.entry_id]
    entities = []

    for country_code, coordinator in coordinators.items():
        entities.append(MeteoAlarmLevelSensor(coordinator, country_code))
        entities.append(MeteoAlarmDetailSensor(coordinator, country_code))

    async_add_entities(entities)


class MeteoAlarmLevelSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, country_code):
        super().__init__(coordinator)
        self._country = country_code.lower()
        country_name = COUNTRIES.get(self._country, self._country.upper())
        self._attr_name = f"MeteoAlarm {country_name} Level"
        self._attr_unique_id = f"meteoalarm_{self._country}_level"
        self.entity_id = f"sensor.meteoalarm_{self._country}_level"

    @property
    def native_value(self):
        sev = self.coordinator.data.get("highest_severity", "Keine")
        return SEVERITY_LABELS.get(sev, sev)

    @property
    def icon(self):
        lvl = self.coordinator.data.get("highest_severity", "Keine")
        if lvl == "Red":
            return "mdi:alert-octagon"
        if lvl == "Orange":
            return "mdi:alert"
        if lvl == "Yellow":
            return "mdi:alert-circle-outline"
        return "mdi:shield-check"


class MeteoAlarmDetailSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, country_code):
        super().__init__(coordinator)
        self._country = country_code.lower()
        country_name = COUNTRIES.get(self._country, self._country.upper())
        self._attr_name = f"MeteoAlarm {country_name} Details"
        self._attr_unique_id = f"meteoalarm_{self._country}_details"
        self.entity_id = f"sensor.meteoalarm_{self._country}_details"
        self._attr_icon = "mdi:format-list-bulleted"

    @property
    def native_value(self):
        count = self.coordinator.data.get("count", 0)
        return f"{count} Warnungen" if count > 0 else "Keine Warnungen"

    @property
    def extra_state_attributes(self):
        return {
            "warnungen": self.coordinator.data.get("warnungen", []),
            "land": self._country.upper(),
        }
