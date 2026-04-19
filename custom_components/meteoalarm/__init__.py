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
    NAME_TO_CODE,
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


def _parse_expires(expires_str: str):
    if not expires_str:
        return None
    try:
        return datetime.fromisoformat(expires_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_atom(root) -> dict:
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


def _resolve_country(state_value: str) -> str | None:
    """Wandelt einen Sensor-State (ISO-Code oder Ländername) in einen ISO-Code um."""
    val = state_value.lower().strip()
    if val in COUNTRIES:
        return val
    if val in NAME_TO_CODE:
        return NAME_TO_CODE[val]
    return None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    cfg = entry.options or entry.data
    mode = cfg.get(CONF_MODE, "manual")

    selected_countries = []

    if mode == MODE_GEOLOCATOR:
        entity_id = cfg.get(CONF_GEOLOCATOR_ENTITY, DEFAULT_GEOLOCATOR_ENTITY)
        state = hass.states.get(entity_id)

        if state and state.state not in ("unknown", "unavailable", ""):
            country_code = _resolve_country(state.state)
            if country_code:
                selected_countries = [country_code]
            else:
                _LOGGER.warning(
                    "GeoLocator liefert unbekannten Wert '%s' – keine Sensoren angelegt",
                    state.state,
                )
        else:
            # BUG FIX: Sensor beim Start unavailable ist normal (HA startet durch).
            # Kein Fehler werfen – der State-Change-Listener übernimmt sobald
            # der Sensor verfügbar wird.
            _LOGGER.info(
                "GeoLocator-Sensor '%s' noch nicht verfügbar – warte auf ersten Update",
                entity_id,
            )
    else:
        selected_countries = cfg.get(CONF_COUNTRIES, [])

    coordinators = {}
    for country in selected_countries:
        coord = MeteoAlarmCoordinator(hass, country)
        try:
            await coord.async_config_entry_first_refresh()
        except Exception as err:
            # BUG FIX: first_refresh-Fehler nicht als Einrichtungsfehler melden –
            # der Coordinator versucht es beim nächsten Intervall erneut.
            _LOGGER.warning(
                "Erster Abruf für %s fehlgeschlagen: %s", country.upper(), err
            )
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

            new_country = _resolve_country(new_state.state)
            if not new_country:
                return

            current = list(hass.data[DOMAIN][entry.entry_id]["coordinators"].keys())
            if new_country not in current:
                _LOGGER.info(
                    "GeoLocator: Länderwechsel nach %s – lade neu", new_country.upper()
                )
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
