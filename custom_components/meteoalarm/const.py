DOMAIN = "meteoalarm"
SCAN_INTERVAL_MINUTES = 15

COUNTRIES = {
    "at": "Österreich",
    "be": "Belgien",
    "bg": "Bulgarien",
    "ch": "Schweiz",
    "cy": "Zypern",
    "cz": "Tschechien",
    "de": "Deutschland",
    "dk": "Dänemark",
    "ee": "Estland",
    "es": "Spanien",
    "fi": "Finnland",
    "fr": "Frankreich",
    "gr": "Griechenland",
    "hr": "Kroatien",
    "hu": "Ungarn",
    "ie": "Irland",
    "is": "Island",
    "it": "Italien",
    "lt": "Litauen",
    "lu": "Luxemburg",
    "lv": "Lettland",
    "me": "Montenegro",
    "mk": "Nordmazedonien",
    "mt": "Malta",
    "nl": "Niederlande",
    "no": "Norwegen",
    "pl": "Polen",
    "pt": "Portugal",
    "ro": "Rumänien",
    "rs": "Serbien",
    "se": "Schweden",
    "si": "Slowenien",
    "sk": "Slowakei",
    "uk": "Großbritannien",
}

SEVERITY_ORDER = {
    "Keine": 0,
    "Yellow": 1,
    "Orange": 2,
    "Red": 3,
}

SEVERITY_LABELS = {
    "Yellow": "Moderate",
    "Orange": "Severe",
    "Red": "Extreme",
    "Keine": "Keine",
}

# Konfigurations-Keys
CONF_MODE = "mode"
MODE_MANUAL = "manual"
MODE_GEOLOCATOR = "geolocator"
CONF_COUNTRIES = "countries"
CONF_GEOLOCATOR_ENTITY = "geolocator_entity"

# Standard-Entity des GeoLocator-Sensors
DEFAULT_GEOLOCATOR_ENTITY = "sensor.geolocator_country_code"
