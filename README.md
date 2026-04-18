# 🚐 MeteoAlarm for Campers (Home Assistant)

Stay safe on your European road trips! This integration brings official **MeteoAlarm.org** weather warnings directly into your Home Assistant dashboard. It is specially designed for campers and travelers who cross borders and need automatic weather updates based on their current location.

## ✨ Features

- **RSS-Powered:** No API keys or developer accounts required. Works out of the box!
- **HACS Ready:** Install easily as a custom repository.
- **Smart Country Detection:** Supports both **ISO Codes** (e.g., `DE`, `HR`) and **Full Country Names** (e.g., `Deutschland`, `Croatia`).
- **Camper-Centric Sensors:**
  - `Level Sensor`: Quick glance at the current alert level (Yellow, Orange, Red).
  - `Detail Sensor`: Full list of active warnings, including descriptions and expiry times.
  - `Combined Sensor`: One "Master Sensor" showing all warnings for all monitored regions.

### ℹ️ Flexible Input Formats
The integration handles various sensor formats automatically:
- **ISO Codes:** `de`, `DE`, `hr`, `HR` are all accepted.
- **Full Names:** `Deutschland`, `Österreich`, `Croatia`, etc., are mapped to their respective codes.


## 🚀 Installation via HACS

1. Open **HACS** in Home Assistant.
2. Click the three dots (top right) -> **Custom repositories**.
3. Add: `https://github.com/hflocki/meteoalarm` (Category: **Integration**).
4. Download and **Restart Home Assistant**.

## ⚙️ Setup & GeoLocator

When adding the integration (**Settings > Devices & Services**), you can choose between two modes:

### 1. Manual Mode
Select one or more fixed countries from a list. Best for stationary use or planning ahead.

### 2. GeoLocator Mode (The Camper's Choice 🌍)
The integration follows your camper! Select any sensor that provides your current location as a country.
- **Flexible Input:** The sensor can provide the country as an **ISO Code** (e.g., `DE`, `AT`, `HR`) or as a **Full Name** (e.g., `Deutschland`, `Österreich`, `Kroatien`).
- **Automatic Sync:** As soon as your sensor (e.g., from a GPS tracker or Phone) changes its state, the integration automatically reloads the correct weather feed for that country.

> **Tip:** If you use the Google Maps integration or a similar device tracker, simply point the GeoLocator to the sensor that holds the country information.

## 📊 Dashboard Examples

Use a **Markdown Card** to display your warnings beautifully:

### Warning Summary
```yaml
type: markdown
content: >
  ### ⚠️ Weather Warnings: {{ state_attr('sensor.meteoalarm_combined', 'gesamt_warnungen') }}
  {% for code, data in state_attr('sensor.meteoalarm_combined', 'laender').items() -%}
    {% set icon = '🔴' if data.warnstufe == 'Extreme' else '🟠' if data.warnstufe == 'Severe' else '🟡' %}
    {{ icon }} **{{ data.land }}**: {{ data.anzahl }} Warnings ({{ data.warnstufe }})<br>
  {% endfor %}
