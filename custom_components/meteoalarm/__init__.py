import logging
import xml.etree.ElementTree as ET
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_COUNTRIES,
    CONF_GEOLOCATOR_ENTITY,
    CONF_MODE,
    COUNTRIES,
    DEFAULT_GEOLOCATOR_ENTITY,
    DOMAIN,
    MODE_GEOLOCATOR,
    SCAN_INTERVAL_MINUTES,
    SEVERITY_ORDER,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    cfg = entry.options or entry.data
    mode = cfg.get(CONF_MODE, "manual")

    if mode == MODE_GEOLOCATOR:
        entity_id = cfg.get(CONF_GEOLOCATOR_ENTITY, DEFAULT_GEOLOCATOR_ENTITY)
        # Aktuelles Land aus dem Sensor lesen
        state = hass.states.get(entity_id)
        country_code = (state.state.lower() if state and state.state not in ("unknown", "unavailable", "") else None)
        selected_countries = [country_code] if country_code and country_code in COUNTRIES else []
    else:
        selected_countries = cfg.get(CONF_COUNTRIES, [])

    coordinators = {}
    for country in selected_countries:
        coord = MeteoAlarmRSSCoordinator(hass, country)
        await coord.async_config_entry_first_refresh()
        coordinators[country] = coord

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinators": coordinators,
        "mode": mode,
        "geolocator_entity": cfg.get(CONF_GEOLOCATOR_ENTITY, DEFAULT_GEOLOCATOR_ENTITY) if mode == MODE_GEOLOCATOR else None,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    # Im GeoLocator-Modus: Sensor-Änderungen überwachen
    if mode == MODE_GEOLOCATOR:
        entity_id = cfg.get(CONF_GEOLOCATOR_ENTITY, DEFAULT_GEOLOCATOR_ENTITY)

        @callback
        def _on_geolocator_change(event):
            """Wenn GeoLocator-Sensor ein neues Land meldet → Integration neu laden."""
            new_state = event.data.get("new_state")
            if not new_state or new_state.state in ("unknown", "unavailable", ""):
                return
            new_country = new_state.state.lower()
            current_countries = list(hass.data[DOMAIN][entry.entry_id]["coordinators"].keys())
            if new_country not in current_countries:
                _LOGGER.info("GeoLocator: Länderwechsel nach %s – lade MeteoAlarm neu", new_country.upper())
                hass.async_create_task(hass.config_entries.async_reload(entry.entry_id))

        entry.async_on_unload(
            async_track_state_change_event(hass, [entity_id], _on_geolocator_change)
        )

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class MeteoAlarmRSSCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, country):
        self.country_code = country.lower()
        super().__init__(
            hass,
            _LOGGER,
            name=f"MeteoAlarm RSS {country.upper()}",
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
        )

    async def _async_update_data(self):
        url = f"https://www.meteoalarm.org/en/rss/{self.country_code}"
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(url, timeout=15) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"RSS Feed nicht erreichbar: {resp.status}")
                text = await resp.text()

            root = ET.fromstring(text)
            items = []
            highest_severity = "Keine"

            for item in root.findall(".//item"):
                title = item.find("title").text if item.find("title") is not None else ""
                description = item.find("description").text if item.find("description") is not None else ""
                pubdate = item.find("pubDate").text if item.find("pubDate") is not None else ""

                severity = "Keine"
                if "Red" in title:
                    severity = "Red"
                elif "Orange" in title:
                    severity = "Orange"
                elif "Yellow" in title:
                    severity = "Yellow"

                if SEVERITY_ORDER.get(severity, 0) > SEVERITY_ORDER.get(highest_severity, 0):
                    highest_severity = severity

                items.append({
                    "headline": title,
                    "description": description,
                    "severity": severity,
                    "pubDate": pubdate,
                    "country": self.country_code.upper(),
                })

            return {
                "warnungen": items,
                "count": len(items),
                "highest_severity": highest_severity,
            }

        except Exception as err:
            _LOGGER.error("Parsing Fehler für %s: %s", self.country_code, err)
            raise UpdateFailed(f"RSS Parsing Fehler: {err}")
