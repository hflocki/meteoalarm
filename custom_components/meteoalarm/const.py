# const.py
DOMAIN = "meteoalarm"
CONF_API_KEY = "api_key"
CONF_COUNTRY = "country"
SCAN_INTERVAL_MINUTES = 10

# Pfad laut OpenAPI-Dokumentation
BASE_URL = (
    "https://api.meteoalarm.org/edr/v1/collections/warnings/locations/{country}?f=json"
)

COUNTRIES = {
    "AT": "Österreich",
    "BE": "Belgien",
    "BG": "Bulgarien",
    "CH": "Schweiz",
    "CY": "Zypern",
    "CZ": "Tschechien",
    "DE": "Deutschland",
    "DK": "Dänemark",
    "EE": "Estland",
    "ES": "Spanien",
    "FI": "Finnland",
    "FR": "Frankreich",
    "GR": "Griechenland",
    "HR": "Kroatien",
    "HU": "Ungarn",
    "IE": "Irland",
    "IS": "Island",
    "IT": "Italien",
    "LT": "Litauen",
    "LU": "Luxemburg",
    "LV": "Lettland",
    "ME": "Montenegro",
    "MK": "Nordmazedonien",
    "MT": "Malta",
    "NL": "Niederlande",
    "NO": "Norwegen",
    "PL": "Polen",
    "PT": "Portugal",
    "RO": "Rumänien",
    "RS": "Serbien",
    "SE": "Schweden",
    "SI": "Slowenien",
    "SK": "Slowakei",
    "UK": "Großbritannien",
}

SEVERITY_ORDER = {
    "Minor": 1,
    "Moderate": 2,
    "Severe": 3,
    "Extreme": 4,
}
