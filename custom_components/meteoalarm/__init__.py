import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CAP_SEVERITY_MAP,
    CONF_COUNTRIES,
    CONF_GEOLOCATOR_ENTITY,
    CONF_MODE,
    COUNTRIES,
    COUNTRY_FEED_SLUG,
    DEFAULT_GEOLOCATOR_ENTITY,
    DOMAIN,
    FILTER_EXPIRED,
    MODE_GEOLOCATOR,
    SCAN_INTERVAL_MINUTES,
    SEVERITY_ORDER,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

_NS_ATOM = "http://www.w3.org/2005/Atom"
_NS_CAP = "urn:oasis:names:tc:emergency:cap:1.2"


def _a(tag):
    return f"{{{_NS_ATOM}}}{tag}"


def _c(tag):
    return f"{{{_NS_CAP}}}{tag}"


def _parse_expires(expires_str: str) -> datetime | None:
    """Parst einen ISO-8601-Zeitstempel aus dem CAP-Feed, gibt None bei Fehler."""
    if not expires_str:
        return None
    try:
        # Python 3.11+: fromisoformat kann +00:00 direkt
        # Für ältere HA-Versionen: Z durch +00:00 ersetzen
        return datetime.fromisoformat(expires_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_atom(root) -> dict:
    """Parst einen Atom/CAP-Feed (feeds.meteoalarm.org).

    Abgelaufene Warnungen werden gefiltert wenn FILTER_EXPIRED=True (aus const.py).
    """
    items = []
    highest_severity = "Keine"
    now = datetime.now(tz=timezone.utc)

    for entry in root.findall(_a("entry")):
        title = entry.findtext(_a("title"), "")
        summary = entry.findtext(_a("summary"), "")
        updated = entry.findtext(_a("updated"), "")
        cap_severity = entry.findtext(_c("severity"), "")
        cap_event = entry.findtext(_c("event"), "")
        cap_expires = entry.findtext(_c("expires"), "")
        cap_area = entry.findtext(_c("areaDesc"), "")
        cap_urgency = entry.findtext(_c("urgency"), "")

        # Abgelaufene Warnungen überspringen
        if FILTER_EXPIRED:
            expires_dt = _parse_expires(cap_expires)
            if expires_dt is not None and expires_dt < now:
                continue

        severity = CAP_SEVERITY_MAP.get(cap_severity, "Keine")
        if SEVERITY_ORDER.get(severity, 0) > SEVERITY_ORDER.get(highest_severity, 0):
            highest_severity = severity

        items.append(
            {
                "headline": title,
                "description": summary,
                "severity": severity,
                "pubDate": updated,
                "event": cap_event,
                "area": cap_area,
                "expires": cap_expires,
                "urgency": cap_urgency,
            }
        )

    return {
        "warnungen": items,
        "count": len(items),
        "highest_severity": highest_severity,
    }


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    cfg = entry.options or entry.data
    mode = cfg.get(CONF_MODE, "manual")

    if mode == MODE_GEOLOCATOR:
        entity_id = cfg.get(CONF_GEOLOCATOR_ENTITY, DEFAULT_GEOLOCATOR_ENTITY)
        state = hass.states.get(entity_id)
        country_code = (
            state.state.lower()
            if state and state.state not in ("unknown", "unavailable", "")
            else None
        )
        selected_countries = (
            [country_code] if country_code and country_code in COUNTRIES else []
        )
    else:
        selected_countries = cfg.get(CONF_COUNTRIES, [])

    coordinators = {}
    for country in selected_countries:
        coord = MeteoAlarmCoordinator(hass, country)
        await coord.async_config_entry_first_refresh()
        coordinators[country] = coord

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinators": coordinators,
        "mode": mode,
        "geolocator_entity": cfg.get(CONF_GEOLOCATOR_ENTITY, DEFAULT_GEOLOCATOR_ENTITY)
        if mode == MODE_GEOLOCATOR
        else None,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    if mode == MODE_GEOLOCATOR:
        entity_id = cfg.get(CONF_GEOLOCATOR_ENTITY, DEFAULT_GEOLOCATOR_ENTITY)

        @callback
        def _on_geolocator_change(event):
            new_state = event.data.get("new_state")
            if not new_state or new_state.state in ("unknown", "unavailable", ""):
                return
            new_country = new_state.state.lower()
            current = list(hass.data[DOMAIN][entry.entry_id]["coordinators"].keys())
            if new_country not in current:
                _LOGGER.info("GeoLocator: Länderwechsel nach %s", new_country.upper())
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


class MeteoAlarmCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, country):
        self.country_code = country.lower()
        slug = COUNTRY_FEED_SLUG.get(self.country_code, self.country_code)
        self.feed_url = (
            f"https://feeds.meteoalarm.org/feeds/meteoalarm-legacy-atom-{slug}"
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"MeteoAlarm {country.upper()}",
            update_interval=timedelta(minutes=SCAN_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict:
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(self.feed_url, timeout=15) as resp:
                if resp.status != 200:
                    raise UpdateFailed(
                        f"Feed nicht erreichbar ({resp.status}): {self.feed_url}"
                    )
                text = await resp.text()

            root = ET.fromstring(text)

            # Sicherheitscheck: ist es wirklich ein Atom-Feed?
            if _NS_ATOM not in root.tag:
                raise UpdateFailed(
                    f"Unerwartetes Feed-Format für {self.country_code.upper()} "
                    f"(Root-Tag: {root.tag})"
                )

            return _parse_atom(root)

        except ET.ParseError as err:
            raise UpdateFailed(f"XML-Fehler: {err}") from err
        except UpdateFailed:
            raise
        except Exception as err:
            _LOGGER.error("Fehler für %s: %s", self.country_code.upper(), err)
            raise UpdateFailed(f"Unerwarteter Fehler: {err}") from err
