# 🚐 MeteoAlarm for Campers (Home Assistant)

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

## 🚀 Installation via HACS

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

---

## 📋 Dashboard Examples

### Warning Detail Card

```yaml
type: markdown
title: Weather Alerts
content: >
  {% set now_ts = now().timestamp() %}
  {% set all_warnings = state_attr('sensor.meteoalarm_combined', 'alle_warnungen') %}
  {% set active = all_warnings | selectattr('expires', 'defined') | list %}
  {% set countries = active | map(attribute='country') | unique | sort %}
  {%- for country in countries %}
    <br><strong>🚩 {{ country }}</strong><hr>
    {%- for w in active | selectattr('country', 'eq', country) | sort(attribute='expires') %}
      {%- if as_timestamp(w.expires) > now_ts %}
        {%- set s = w.severity.lower() -%}
        {%- set icon = '🔴' if 'red' in s or 'extreme' in s else '🟠' if 'orange' in s or 'severe' in s else '🟡' -%}
        <div style="margin-bottom: 10px;">
          {{ icon }} <b>{{ w.headline }}</b><br>
          🕒 <i>Until: {{ as_timestamp(w.expires) | timestamp_custom('%d.%m. %H:%M') }}</i>
        </div>
      {%- endif %}
    {%- endfor %}
  {%- endfor %}
```

### Country Overview Card

```yaml
type: markdown
content: >
  ### ⚠️ Active Warnings: {{ state_attr('sensor.meteoalarm_combined', 'gesamt_warnungen') }}
  {% for code, data in state_attr('sensor.meteoalarm_combined', 'laender').items() %}
    {% set icon = '🔴' if data.warnstufe == 'Extreme' else '🟠' if data.warnstufe == 'Severe' else '🟡' %}
    {{ icon }} **{{ data.land }}** ({{ code }}): {{ data.anzahl }} warning(s) – {{ data.warnstufe }}
  {% endfor %}
```

### Conditional Alert (only visible when warnings are active)

```yaml
type: conditional
conditions:
  - entity: sensor.meteoalarm_combined
    state_not: Keine
card:
  type: markdown
  content: "⚠️ Active weather warnings! Check sensor.meteoalarm_combined for details."
```

---

## 🌍 Supported Countries

| Code | Country | Code | Country | Code | Country |
|---|---|---|---|---|---|
| AD | Andorra | HU | Hungary | PT | Portugal |
| AT | Austria | IE | Ireland | RO | Romania |
| BA | Bosnia-Herzegovina | IL | Israel | RS | Serbia |
| BE | Belgium | IS | Iceland | SE | Sweden |
| BG | Bulgaria | IT | Italy | SI | Slovenia |
| CH | Switzerland | LT | Lithuania | SK | Slovakia |
| CY | Cyprus | LU | Luxembourg | UA | Ukraine |
| CZ | Czechia | LV | Latvia | UK | United Kingdom |
| DE | Germany | MD | Moldova | | |
| DK | Denmark | ME | Montenegro | | |
| EE | Estonia | MK | North Macedonia | | |
| ES | Spain | MT | Malta | | |
| FI | Finland | NL | Netherlands | | |
| FR | France | NO | Norway | | |
| GR | Greece | PL | Poland | | |
| HR | Croatia | | | | |

---

## 🔧 Technical Details

| Property | Value |
|---|---|
| Data source | [feeds.meteoalarm.org](https://feeds.meteoalarm.org/) – official Atom/CAP 1.2 feeds |
| Update interval | Every 15 minutes |
| Feed format | Atom 1.0 with CAP 1.2 namespace |
| Severity mapping | `Minor` → Yellow · `Moderate` → Orange · `Severe`/`Extreme` → Red |
| Expired warnings | Filtered out automatically via CAP `expires` field |

---

## 📄 License

MIT
