import logging
import xml.etree.ElementTree as ET
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL_MINUTES, SEVERITY_ORDER

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    selected_countries = entry.data.get("countries", [])

    coordinators = {}
    for country in selected_countries:
        coordinator = MeteoAlarmRSSCoordinator(hass, country)
        await coordinator.async_config_entry_first_refresh()
        coordinators[country] = coordinator

    hass.data[DOMAIN][entry.entry_id] = coordinators
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


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
            name=f"MeteoAlarm RSS {country}",
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
                title = (
                    item.find("title").text if item.find("title") is not None else ""
                )
                description = (
                    item.find("description").text
                    if item.find("description") is not None
                    else ""
                )

                severity = "Keine"
                if "Red" in title:
                    severity = "Red"
                elif "Orange" in title:
                    severity = "Orange"
                elif "Yellow" in title:
                    severity = "Yellow"

                if SEVERITY_ORDER.get(severity, 0) > SEVERITY_ORDER.get(
                    highest_severity, 0
                ):
                    highest_severity = severity

                items.append(
                    {
                        "headline": title,
                        "description": description,
                        "severity": severity,
                        "pubDate": item.find("pubDate").text
                        if item.find("pubDate") is not None
                        else "",
                    }
                )

            return {
                "warnungen": items,
                "count": len(items),
                "highest_severity": highest_severity,
            }

        except Exception as err:
            _LOGGER.error("Parsing Fehler für %s: %s", self.country_code, err)
            raise UpdateFailed(f"RSS Parsing Fehler: {err}")
