# 🚐 MeteoAlarm for Campers (Home Assistant)

<img src="/logo/icon.png" alt="GeoWeather Logo" width="150">

Stay safe on your European road trips! This integration brings official **MeteoAlarm.org** weather warnings directly into your Home Assistant dashboard — no API keys, no accounts, works out of the box.

Designed for campers, van lifers, and travelers who cross borders and need automatic weather updates based on their current location.

## ✨ Features

- **No API keys required** – uses the official [MeteoAlarm Atom feeds](https://feeds.meteoalarm.org/)
- **HACS Ready** – install as a custom repository in minutes
- **39 countries** – all MeteoAlarm member states across Europe
- **Two setup modes** – fixed country list or fully automatic via GPS/location sensor
- **Smart country detection** – accepts ISO codes (`DE`, `hr`) and full names (`Deutschland`, `Croatia`)
- **Expired warnings filtered** – only currently active warnings are shown
- **Three sensor types per country** plus one combined master sensor

## 🌍 Supported Countries

| Code | Flag | Country | Code | Flag | Country | Code | Flag | Country |
|---|:---:|---|---|:---:|---|---|:---:|---|
| AD | <img src="https://flagcdn.com/w20/ad.png" srcset="https://flagcdn.com/w40/ad.png 2x" width="20" alt="Andorra"> | Andorra | HU | <img src="https://flagcdn.com/w20/hu.png" srcset="https://flagcdn.com/w40/hu.png 2x" width="20" alt="Hungary"> | Hungary | PT | <img src="https://flagcdn.com/w20/pt.png" srcset="https://flagcdn.com/w40/pt.png 2x" width="20" alt="Portugal"> | Portugal |
| AT | <img src="https://flagcdn.com/w20/at.png" srcset="https://flagcdn.com/w40/at.png 2x" width="20" alt="Austria"> | Austria | IE | <img src="https://flagcdn.com/w20/ie.png" srcset="https://flagcdn.com/w40/ie.png 2x" width="20" alt="Ireland"> | Ireland | RO | <img src="https://flagcdn.com/w20/ro.png" srcset="https://flagcdn.com/w40/ro.png 2x" width="20" alt="Romania"> | Romania |
| BA | <img src="https://flagcdn.com/w20/ba.png" srcset="https://flagcdn.com/w40/ba.png 2x" width="20" alt="Bosnia-Herzegovina"> | Bosnia-Herzegovina | IL | <img src="https://flagcdn.com/w20/il.png" srcset="https://flagcdn.com/w40/il.png 2x" width="20" alt="Israel"> | Israel | RS | <img src="https://flagcdn.com/w20/rs.png" srcset="https://flagcdn.com/w40/rs.png 2x" width="20" alt="Serbia"> | Serbia |
| BE | <img src="https://flagcdn.com/w20/be.png" srcset="https://flagcdn.com/w40/be.png 2x" width="20" alt="Belgium"> | Belgium | IS | <img src="https://flagcdn.com/w20/is.png" srcset="https://flagcdn.com/w40/is.png 2x" width="20" alt="Iceland"> | Iceland | SE | <img src="https://flagcdn.com/w20/se.png" srcset="https://flagcdn.com/w40/se.png 2x" width="20" alt="Sweden"> | Sweden |
| BG | <img src="https://flagcdn.com/w20/bg.png" srcset="https://flagcdn.com/w40/bg.png 2x" width="20" alt="Bulgaria"> | Bulgaria | IT | <img src="https://flagcdn.com/w20/it.png" srcset="https://flagcdn.com/w40/it.png 2x" width="20" alt="Italy"> | Italy | SI | <img src="https://flagcdn.com/w20/si.png" srcset="https://flagcdn.com/w40/si.png 2x" width="20" alt="Slovenia"> | Slovenia |
| CH | <img src="https://flagcdn.com/w20/ch.png" srcset="https://flagcdn.com/w40/ch.png 2x" width="20" alt="Switzerland"> | Switzerland | LT | <img src="https://flagcdn.com/w20/lt.png" srcset="https://flagcdn.com/w40/lt.png 2x" width="20" alt="Lithuania"> | Lithuania | SK | <img src="https://flagcdn.com/w20/sk.png" srcset="https://flagcdn.com/w40/sk.png 2x" width="20" alt="Slovakia"> | Slovakia |
| CY | <img src="https://flagcdn.com/w20/cy.png" srcset="https://flagcdn.com/w40/cy.png 2x" width="20" alt="Cyprus"> | Cyprus | LU | <img src="https://flagcdn.com/w20/lu.png" srcset="https://flagcdn.com/w40/lu.png 2x" width="20" alt="Luxembourg"> | Luxembourg | UA | <img src="https://flagcdn.com/w20/ua.png" srcset="https://flagcdn.com/w40/ua.png 2x" width="20" alt="Ukraine"> | Ukraine |
| CZ | <img src="https://flagcdn.com/w20/cz.png" srcset="https://flagcdn.com/w40/cz.png 2x" width="20" alt="Czechia"> | Czechia | LV | <img src="https://flagcdn.com/w20/lv.png" srcset="https://flagcdn.com/w40/lv.png 2x" width="20" alt="Latvia"> | Latvia | UK | <img src="https://flagcdn.com/w20/gb.png" srcset="https://flagcdn.com/w40/gb.png 2x" width="20" alt="United Kingdom"> | United Kingdom |
| DE | <img src="https://flagcdn.com/w20/de.png" srcset="https://flagcdn.com/w40/de.png 2x" width="20" alt="Germany"> | Germany | MD | <img src="https://flagcdn.com/w20/md.png" srcset="https://flagcdn.com/w40/md.png 2x" width="20" alt="Moldova"> | Moldova | | | |
| DK | <img src="https://flagcdn.com/w20/dk.png" srcset="https://flagcdn.com/w40/dk.png 2x" width="20" alt="Denmark"> | Denmark | ME | <img src="https://flagcdn.com/w20/me.png" srcset="https://flagcdn.com/w40/me.png 2x" width="20" alt="Montenegro"> | Montenegro | | | |
| EE | <img src="https://flagcdn.com/w20/ee.png" srcset="https://flagcdn.com/w40/ee.png 2x" width="20" alt="Estonia"> | Estonia | MK | <img src="https://flagcdn.com/w20/mk.png" srcset="https://flagcdn.com/w40/mk.png 2x" width="20" alt="North Macedonia"> | North Macedonia | | | |
| ES | <img src="https://flagcdn.com/w20/es.png" srcset="https://flagcdn.com/w40/es.png 2x" width="20" alt="Spain"> | Spain | MT | <img src="https://flagcdn.com/w20/mt.png" srcset="https://flagcdn.com/w40/mt.png 2x" width="20" alt="Malta"> | Malta | | | |
| FI | <img src="https://flagcdn.com/w20/fi.png" srcset="https://flagcdn.com/w40/fi.png 2x" width="20" alt="Finland"> | Finland | NL | <img src="https://flagcdn.com/w20/nl.png" srcset="https://flagcdn.com/w40/nl.png 2x" width="20" alt="Netherlands"> | Netherlands | | | |
| FR | <img src="https://flagcdn.com/w20/fr.png" srcset="https://flagcdn.com/w40/fr.png 2x" width="20" alt="France"> | France | NO | <img src="https://flagcdn.com/w20/no.png" srcset="https://flagcdn.com/w40/no.png 2x" width="20" alt="Norway"> | Norway | | | |
| GR | <img src="https://flagcdn.com/w20/gr.png" srcset="https://flagcdn.com/w40/gr.png 2x" width="20" alt="Greece"> | Greece | PL | <img src="https://flagcdn.com/w20/pl.png" srcset="https://flagcdn.com/w40/pl.png 2x" width="20" alt="Poland"> | Poland | | | |
| HR | <img src="https://flagcdn.com/w20/hr.png" srcset="https://flagcdn.com/w40/hr.png 2x" width="20" alt="Croatia"> | Croatia | | | | | | |

## 🚀 Installation via HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=hflocki&repository=https%3A%2F%2Fgithub.com%2Fhflocki%2Fmeteoalarm&category=Weather)

or

1. Open **HACS** in Home Assistant
2. Click the three dots (top right) → **Custom repositories**
3. Add `https://github.com/hflocki/meteoalarm` as category **Integration**
4. Download and **restart Home Assistant**

## ⚙️ Setup

Go to **Settings → Devices & Services → + Add Integration → MeteoAlarm**.

---

### Mode 1 – Manual 🗺️
Select one or more fixed countries from a list. Sensors are created immediately and update every 15 minutes. Best for stationary use or if you want specific countries regardless of location.

---

### Mode 2 – GeoLocator (The Camper's Choice 🌍)

Point the integration to any sensor that reports the current country. As soon as the sensor changes (e.g. after a border crossing), MeteoAlarm automatically reloads and creates sensors for the new country — no restart, no manual intervention.

**Accepted sensor values:**
- ISO codes: `de`, `DE`, `hr`, `AT`, `fr` … (case-insensitive)
- Full country names: `Deutschland`, `Österreich`, `Croatia`, `France` … (German or English)

**Compatible sources:**
- [GeoLocator by SmartyVan](https://github.com/SmartyVan/hass-geolocator) → `sensor.geolocator_country_code` *(recommended)*
- Home Assistant Companion App → geocoded location sensor
- Any GPS tracker or device tracker that exposes a country as sensor state

> **Note:** If the sensor is `unavailable` at startup (no GPS fix yet), MeteoAlarm waits and automatically activates as soon as the first valid country value arrives.

---

## 📊 Sensors

For each configured country, two sensors are created:

### `sensor.meteoalarm_XX_level`
Highest active warning level for that country.

| State | Color | Meaning |
|---|---|---|
| `Keine` | – | No active warnings |
| `Moderate` | 🟡 Yellow | Low-level warning |
| `Severe` | 🟠 Orange | Significant warning |
| `Extreme` | 🔴 Red | Extreme/dangerous warning |

**Attributes:** `country_code`, `country_name`, `severity_raw`, `warning_count`

### `sensor.meteoalarm_XX_details`
Full list of active warnings for that country.

**State:** e.g. `5 Warnungen` or `Keine Warnungen`

**Attributes:** `country_code`, `country_name`, `warnungen` (list with `headline`, `event`, `area`, `severity`, `expires`, `urgency`)

### `sensor.meteoalarm_combined`
Always created, regardless of mode. Aggregates all active warnings across **all** monitored countries. Use this one in your dashboard — it always reflects the current state even when countries change.

**State:** highest warning level across all countries

**Attributes:**
- `gesamt_warnungen` – total number of active warnings
- `laender` – summary per country (name, level, count)
- `alle_warnungen` – flat list of all warnings with country tag

> **Note on Warning Lists:**  
> To keep Home Assistant running smoothly and prevent attribute limits from overflowing when a country experiences widespread severe weather, the attribute lists (`warnungen` and `alle_warnungen`) store a maximum of 10 warnings sorted by priority. The total count entity state always reflects the real total number of warnings.

---

### Optional: Recorder Exclusion (`configuration.yaml`)

To keep your Home Assistant database small, you can exclude the large combined sensor attributes:

```yaml
recorder:
  exclude:
    entities:
      - sensor.meteoalarm_combined
