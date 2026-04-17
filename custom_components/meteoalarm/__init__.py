import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import BASE_URL, CONF_API_KEY, DOMAIN, SCAN_INTERVAL_MINUTES

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
        # Die URL nutzt jetzt den Platzhalter {country} aus der const.py
        url = BASE_URL.format(country=self.country)
        
        # Laut OpenAPI yaml ist Bearer Auth der Standard
        headers = {
            "Accept": "application/geo+json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            session = async_get_clientsession(self.hass)
            async with session.get(url, headers=headers, timeout=30) as resp:
                if resp.status == 401:
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
            matched.append(
                {
                    "headline": props.get("headline"),
                    "event": props.get("event"),
                    "severity": props.get("severity"),
                    "onset": props.get("onset"),
                    "expires": props.get("expires"),
                    "description": props.get("description"),
                    "instruction": props.get("instruction"),
                }
            )

        return {"warnungen": matched, "location": f"{lat}, {lon}"}
