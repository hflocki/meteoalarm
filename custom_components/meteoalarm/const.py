DOMAIN = "meteoalarm"
CONF_API_KEY = "api_key"
CONF_COUNTRY = "country"

# Pfad laut OpenAPI-Dokumentation
BASE_URL = (
    "https://api.meteoalarm.org/edr/v1/collections/warnings/locations/{country}?f=json"
)

SEVERITY_ORDER = {
    "Minor": 1,
    "Moderate": 2,
    "Severe": 3,
    "Extreme": 4,
}
