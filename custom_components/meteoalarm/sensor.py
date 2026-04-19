import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import COUNTRIES, DOMAIN, SEVERITY_LABELS, SEVERITY_ORDER

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinators = entry_data["coordinators"]

    # ── Alte Entities bereinigen ──────────────────────────────────────────────
    # Wenn man von manuell auf GeoLocator wechselt (oder Länder ändert),
    # bleiben Entities alter Länder in der Entity Registry. Diese müssen
    # entfernt werden damit sie nicht als "unavailable" im Dashboard hängen.
    er = async_get_entity_registry(hass)
    active_unique_ids = set()
    for cc in coordinators:
        active_unique_ids.add(f"meteoalarm_{cc}_level")
        active_unique_ids.add(f"meteoalarm_{cc}_details")
    active_unique_ids.add("meteoalarm_combined")

    for entity_entry in list(er.entities.values()):
        if entity_entry.config_entry_id != entry.entry_id:
            continue
        if entity_entry.unique_id not in active_unique_ids:
            _LOGGER.info("Entferne veraltete Entity: %s", entity_entry.entity_id)
            er.async_remove(entity_entry.entity_id)
    # ─────────────────────────────────────────────────────────────────────────

    entities = []
    for country_code, coordinator in coordinators.items():
        entities.append(MeteoAlarmLevelSensor(coordinator, country_code))
        entities.append(MeteoAlarmDetailSensor(coordinator, country_code))

    # Combined immer anlegen – auch wenn coordinators gerade leer ist
    # (GeoLocator-Modus: Sensor beim Start noch unavailable)
    entities.append(MeteoAlarmCombinedSensor(list(coordinators.values()), entry))

    async_add_entities(entities)


class MeteoAlarmLevelSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, country_code):
        super().__init__(coordinator)
        self._country = country_code.lower()
        cc = self._country.upper()
        name = COUNTRIES.get(self._country, cc)
        self._attr_name = f"MeteoAlarm [{cc}] {name} Level"
        self._attr_unique_id = f"meteoalarm_{self._country}_level"
        self.entity_id = f"sensor.meteoalarm_{self._country}_level"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        sev = self.coordinator.data.get("highest_severity", "Keine")
        return SEVERITY_LABELS.get(sev, sev)

    @property
    def extra_state_attributes(self):
        return {
            "country_code": self._country.upper(),
            "country_name": COUNTRIES.get(self._country, self._country.upper()),
            "severity_raw": self.coordinator.data.get("highest_severity", "Keine")
            if self.coordinator.data
            else "Keine",
            "warning_count": self.coordinator.data.get("count", 0)
            if self.coordinator.data
            else 0,
        }

    @property
    def icon(self):
        if not self.coordinator.data:
            return "mdi:shield-check"
        return {
            "Red": "mdi:alert-octagon",
            "Orange": "mdi:alert",
            "Yellow": "mdi:alert-circle-outline",
        }.get(self.coordinator.data.get("highest_severity", ""), "mdi:shield-check")


class MeteoAlarmDetailSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, country_code):
        super().__init__(coordinator)
        self._country = country_code.lower()
        cc = self._country.upper()
        name = COUNTRIES.get(self._country, cc)
        self._attr_name = f"MeteoAlarm [{cc}] {name} Details"
        self._attr_unique_id = f"meteoalarm_{self._country}_details"
        self.entity_id = f"sensor.meteoalarm_{self._country}_details"
        self._attr_icon = "mdi:format-list-bulleted"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return "Keine Warnungen"
        count = self.coordinator.data.get("count", 0)
        return f"{count} Warnungen" if count > 0 else "Keine Warnungen"

    @property
    def extra_state_attributes(self):
        return {
            "country_code": self._country.upper(),
            "country_name": COUNTRIES.get(self._country, self._country.upper()),
            "warnungen": self.coordinator.data.get("warnungen", [])
            if self.coordinator.data
            else [],
        }


class MeteoAlarmCombinedSensor(SensorEntity):
    """Kombinierter Sensor über alle aktiven Länder.

    Wird immer angelegt – auch im GeoLocator-Modus wenn beim Start noch
    kein Land bekannt ist. Aktualisiert sich sobald Coordinatoren verfügbar sind.
    Abonniert dynamisch neue Coordinatoren wenn die Integration neu lädt.
    """

    def __init__(self, coordinators: list, entry):
        self._entry = entry
        self._coordinators = coordinators
        self._attr_name = "MeteoAlarm Combined"
        self._attr_unique_id = "meteoalarm_combined"
        self.entity_id = "sensor.meteoalarm_combined"
        self._attr_icon = "mdi:earth"
        self._unsub = []

    async def async_added_to_hass(self):
        for coord in self._coordinators:
            self._unsub.append(coord.async_add_listener(self._handle_update))

    async def async_will_remove_from_hass(self):
        for unsub in self._unsub:
            unsub()
        self._unsub.clear()

    def _handle_update(self):
        self.async_write_ha_state()

    def _get_active_coordinators(self):
        """Holt immer die aktuellen Coordinatoren aus hass.data."""
        try:
            return list(
                self.hass.data[DOMAIN][self._entry.entry_id]["coordinators"].values()
            )
        except (KeyError, AttributeError):
            return self._coordinators

    @property
    def native_value(self):
        highest = "Keine"
        for coord in self._get_active_coordinators():
            if coord.data:
                sev = coord.data.get("highest_severity", "Keine")
                if SEVERITY_ORDER.get(sev, 0) > SEVERITY_ORDER.get(highest, 0):
                    highest = sev
        return SEVERITY_LABELS.get(highest, highest)

    @property
    def extra_state_attributes(self):
        all_warnings, summary, total = [], {}, 0
        for coord in self._get_active_coordinators():
            if not coord.data:
                continue
            cc = coord.country_code.upper()
            count = coord.data.get("count", 0)
            total += count
            sev = coord.data.get("highest_severity", "Keine")
            summary[cc] = {
                "land": COUNTRIES.get(coord.country_code, cc),
                "warnstufe": SEVERITY_LABELS.get(sev, sev),
                "anzahl": count,
            }
            for w in coord.data.get("warnungen", []):
                all_warnings.append({**w, "country": cc})
        return {
            "gesamt_warnungen": total,
            "laender": summary,
            "alle_warnungen": all_warnings,
        }

    @property
    def icon(self):
        highest = "Keine"
        for coord in self._get_active_coordinators():
            if coord.data:
                sev = coord.data.get("highest_severity", "Keine")
                if SEVERITY_ORDER.get(sev, 0) > SEVERITY_ORDER.get(highest, 0):
                    highest = sev
        return {
            "Red": "mdi:alert-octagon",
            "Orange": "mdi:alert",
            "Yellow": "mdi:alert-circle-outline",
        }.get(highest, "mdi:earth")
