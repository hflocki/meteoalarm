from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, SEVERITY_ORDER

async def async_setup_entry(hass, entry, async_add_entities):
    """Setzt die Sensoren basierend auf dem Config Entry auf."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Wir fügen beide Sensoren hinzu
    async_add_entities([
        MeteoAlarmLevelSensor(coordinator, entry),
        MeteoAlarmDetailSensor(coordinator, entry)
    ])

class MeteoAlarmLevelSensor(CoordinatorEntity, SensorEntity):
    """Sensor für die höchste Warnstufe im gewählten Land."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_highest_level"
        self._attr_name = f"MeteoAlarm {entry.title} Höchste Stufe"

    @property
    def native_value(self):
        """Gibt die höchste aktuelle Warnstufe zurück."""
        warnungen = self.coordinator.data.get("warnungen", [])
        if not warnungen:
            return "Keine"
        
        # Findet die Warnung mit der höchsten Stufe basierend auf SEVERITY_ORDER
        return max(
            (w.get("severity", "Minor") for w in warnungen),
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

class MeteoAlarmDetailSensor(CoordinatorEntity, SensorEntity):
    """Sensor für die detaillierten Warnungstexte."""

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_details"
        self._attr_name = f"MeteoAlarm {entry.title} Details"
        self._attr_icon = "mdi:format-list-bulleted"

    @property
    def native_value(self):
        """Zeigt den Titel der ersten Warnung oder 'Keine Warnungen'."""
        warnungen = self.coordinator.data.get("warnungen", [])
        if not warnungen:
            return "Keine Warnungen"
        return warnungen[0].get("headline", "Warnung aktiv")

    @property
    def extra_state_attributes(self):
        """Schreibt alle Warnungen in die Attribute für Dashboards."""
        data = self.coordinator.data
        return {
            "anzahl": data.get("count", 0),
            "standort": data.get("location"),
            "alle_warnungen": data.get("warnungen", []),
        }
