import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
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
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class MeteoAlarmCoordinator(DataUpdateCoordinator):
    """Holt Warnungen basierend auf den HA-System-Koordinaten."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        # Wir holen nur den API-Key. Das Land brauchen wir nicht mehr im Init.
        self.api_key = entry.data.get(CONF_API_KEY)
        self.entry = entry

        super().__init__(
            hass,
            _LOGGER,
            name="Geo Weather Alarms",
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
        )

    async def _async_update_data(self):
        # HA-interne GPS-Koordinaten abgreifen
        lat = self.hass.config.latitude
        lon = self.hass.config.longitude

        # URL aus der const.py nutzen und Koordinaten einsetzen
        url = BASE_URL.format(lon=lon, lat=lat)
        headers = {
            "Accept": "application/geo+json",
            "apikey": self.api_key,
        }

        try:
            # Nutze die von HA empfohlene aiohttp_client Helper-Methode (optional, aber sauberer)
            from homeassistant.helpers.aiohttp_client import async_get_clientsession

            session = async_get_clientsession(self.hass)

            async with session.get(
                url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
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
                    "titel": props.get("headline"),
                    "typ": props.get("event"),
                    "stufe": props.get("severity"),
                    "von": props.get("onset"),
                    "bis": props.get("expires"),
                    "beschreibung": props.get("description"),
                    "instruction": props.get("instruction"),
                }
            )

        return {
            "warnungen": matched,
            # Wir geben die Koordinaten zurück, damit man sie im Sensor sieht
            "location": f"{lat}, {lon}",
        }
