DOMAIN = "meteoalarm"
CONF_COUNTRY = "country"
CONF_API_KEY = "api_key"
SCAN_INTERVAL_MINUTES = 10

BASE_URL = "https://api.meteogate.eu/edr/v1/collections/warnings/position?coords=POINT({lon} {lat})&f=GeoJSON"

SEVERITY_ORDER = {
    "Minor": 1,
    "Moderate": 2,
    "Severe": 3,
    "Extreme": 4,
}
