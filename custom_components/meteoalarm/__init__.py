import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import BASE_URL, CONF_API_KEY, CONF_COUNTRY, DOMAIN, SCAN_INTERVAL_MINUTES

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    coordinator = MeteoAlarmCoordinator(hass, entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class MeteoAlarmCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        # Hier holen wir das Land und den Key aus den Config-Einträgen
        self.country = entry.data[CONF_COUNTRY]
        self.api_key = entry.data[CONF_API_KEY]
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name=f"MeteoAlarm {self.country}",
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
        )

    async def _async_update_data(self):
        """Daten von der API abrufen."""
        lat = self.hass.config.latitude
        lon = self.hass.config.longitude

        # 1. URL zusammenbauen und den Token direkt anhängen (tokenQuery Methode)
        # Wir nutzen &token=, da in der BASE_URL bereits ein ?f=json steht
        url = f"{BASE_URL.format(country=self.country)}?f=GeoJSON&token={self.api_key}"
        
        # DEBUG: Hilft dir im Log zu sehen, was genau aufgerufen wird
        _LOGGER.debug("MeteoAlarm Abruf: %s (Key beginnt mit %s)", url.split("&token=")[0], self.api_key[:5])

        # 2. Header ohne Authorization (da der Key nun in der URL steckt)
        headers = {
            "Accept": "application/geo+json",
        }

        try:
            from homeassistant.helpers.aiohttp_client import async_get_clientsession
            session = async_get_clientsession(self.hass)
            
            async with session.get(url, headers=headers, timeout=30) as resp:
                if resp.status == 401:
                    # Logge die Antwort des Servers bei Fehlern
                    error_text = await resp.text()
                    _LOGGER.error("Auth Fehler (401): %s", error_text)
                    raise UpdateFailed("Invalid API Key")
                if resp.status != 200:
                    raise UpdateFailed(f"API Error: {resp.status}")
                
                data = await resp.json(content_type=None)
        except Exception as err:
            raise UpdateFailed(f"Connection Error: {err}")

        features = data.get("features", [])
        matched = []

        for feature in features:
            props = feature.get("properties", {})
            
            # HIER kannst du später noch deine GPS-Filter Logik einbauen
            # (Prüfung ob lat/lon innerhalb der Geometrie des Features liegen)
            
            matched.append({
                "headline": props.get("headline"),
                "event": props.get("event"),
                "severity": props.get("severity"),
                "onset": props.get("onset"),
                "expires": props.get("expires"),
                "description": props.get("description"),
                "instruction": props.get("instruction"),
            })

        return {
            "warnungen": matched, 
            "location": f"{lat}, {lon}"
        }
