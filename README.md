# 🚐 MeteoAlarm RSS for Campers (Home Assistant)

Stay safe on the road! This Home Assistant integration brings official **MeteoAlarm.org** weather warnings directly into your dashboard. Designed specifically for campers and travelers moving across Europe, it helps you monitor weather hazards for multiple countries without the need for complex API keys.

## ✨ Features

- **RSS-Powered:** Uses public feeds from MeteoAlarm.org—no registration or API tokens required.
- **HACS Compatible:** Easy to install and update as a Custom Repository.
- **Multi-Country Setup:** Monitor several countries at once (e.g., Germany and Croatia) with dedicated sensors for each.
- **Camper-Centric Sensors:**
  - `Level Sensor`: Shows the highest alert level (Yellow, Orange, Red).
  - `Detail Sensor`: Full list of active warning headlines and descriptions.
  - `Combined Sensor`: A master view aggregating all your monitored regions into one card.

## 🚀 Installation via HACS

Since this is a custom integration, you can add it to HACS in a few simple steps:

1. Open **HACS** in your Home Assistant sidebar.
2. Click on the three dots in the top right corner and select **Custom repositories**.
3. Paste the URL of this repository: `https://github.com/hflocki/meteoalarm`
4. Select **Integration** as the Category and click **Add**.
5. Find the "MeteoAlarm Wetterwarnungen" integration in HACS and click **Download**.
6. **Restart Home Assistant.**

## ⚙️ Configuration

1. Go to **Settings > Devices & Services**.
2. Click **Add Integration** and search for **MeteoAlarm**.
3. Select your desired countries from the checklist (e.g., DE, HR, AT).
4. The sensors will be created automatically using the format `sensor.meteoalarm_xx_level`.

## 📊 Dashboard Examples

### Summary Overview
```yaml
type: markdown
content: >
  ### ⚠️ Weather Warnings: {{ state_attr('sensor.meteoalarm_combined', 'gesamt_warnungen') }}
  {% for code, data in state_attr('sensor.meteoalarm_combined', 'laender').items() -%}
    {% set icon = '🔴' if data.warnstufe == 'Extreme' else '🟠' if data.warnstufe == 'Severe' else '🟡' %}
    {{ icon }} **{{ data.land }}**: {{ data.anzahl }} Warnings ({{ data.warnstufe }})<br>
  {% endfor %}
