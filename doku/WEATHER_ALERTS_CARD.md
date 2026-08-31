# 🗂️ Integration with `weather-alerts-card`

If you want to display weather warnings using the popular [weather-alerts-card](https://github.com/seevee/weather_alerts_card) frontend custom card, you can easily bridge the data using a Home Assistant **Template Sensor**.

This method keeps your system lightweight and efficient without creating dozens of single entities for every active warning.

---

## 🛠️ Setup Instructions

### 1. Add the Template Sensor
Add the following configuration to your `configuration.yaml` (or your dedicated `templates.yaml` file). 

This sensor automatically maps the combined MeteoAlarm warnings into the exact Common Alerting Protocol (CAP) format expected by the card:

```yaml
template:
  - sensor:
      - name: "MeteoAlarm CAP Adapter"
        unique_id: meteoalarm_cap_adapter
        state: >
          {{ state_attr('sensor.meteoalarm_combined', 'gesamt_warnungen') | int(0) }}
        icon: mdi:alert-decagram
        attributes:
          alerts: >
            {% set map_severity = {'Yellow': 'minor', 'Orange': 'moderate', 'Red': 'severe'} %}
            {% set raw_warnings = state_attr('sensor.meteoalarm_combined', 'alle_warnungen') or [] %}
            {% set ns = namespace(formatted=[]) %}
            {% for w in raw_warnings %}
              {% set item = {
                'id': w.id | default(loop.index | string),
                'event': w.event | default(w.headline),
                'headline': w.headline,
                'description': w.description | default(''),
                'severity': w.severity | default('Yellow'),
                'severity_normalized': map_severity.get(w.severity, 'minor'),
                'urgency': w.urgency | default('unknown'),
                'onset': w.pubDate,
                'effective': w.pubDate,
                'expires': w.expires,
                'ends': w.expires,
                'area_desc': w.area | default(w.country),
                'area': w.area | default(w.country)
              } %}
              {% set ns.formatted = ns.formatted + [item] %}
            {% endfor %}
            {{ ns.formatted }}
