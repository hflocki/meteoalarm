DOMAIN = "meteoalarm"
SCAN_INTERVAL_MINUTES = 15

COUNTRIES = {
    "ad": "Andorra",
    "at": "Österreich",
    "ba": "Bosnien-Herzegowina",
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
    "il": "Israel",
    "is": "Island",
    "it": "Italien",
    "lt": "Litauen",
    "lu": "Luxemburg",
    "lv": "Lettland",
    "md": "Moldau",
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
    "ua": "Ukraine",
    "uk": "Großbritannien",
}

# Exakte Feed-Slugs von feeds.meteoalarm.org
COUNTRY_FEED_SLUG = {
    "ad": "andorra",
    "at": "austria",
    "ba": "bosnia-herzegovina",
    "be": "belgium",
    "bg": "bulgaria",
    "ch": "switzerland",
    "cy": "cyprus",
    "cz": "czechia",
    "de": "germany",
    "dk": "denmark",
    "ee": "estonia",
    "es": "spain",
    "fi": "finland",
    "fr": "france",
    "gr": "greece",
    "hr": "croatia",
    "hu": "hungary",
    "ie": "ireland",
    "il": "israel",
    "is": "iceland",
    "it": "italy",
    "lt": "lithuania",
    "lu": "luxembourg",
    "lv": "latvia",
    "md": "moldova",
    "me": "montenegro",
    "mk": "republic-of-north-macedonia",
    "mt": "malta",
    "nl": "netherlands",
    "no": "norway",
    "pl": "poland",
    "pt": "portugal",
    "ro": "romania",
    "rs": "serbia",
    "se": "sweden",
    "si": "slovenia",
    "sk": "slovakia",
    "ua": "ukraine",
    "uk": "united-kingdom",
}

# CAP severity → interne Warnstufe
CAP_SEVERITY_MAP = {
    "Minor":    "Yellow",
    "Moderate": "Orange",
    "Severe":   "Orange",
    "Extreme":  "Red",
    "Unknown":  "Keine",
}

SEVERITY_ORDER = {
    "Keine":  0,
    "Yellow": 1,
    "Orange": 2,
    "Red":    3,
}

SEVERITY_LABELS = {
    "Yellow": "Moderate",
    "Orange": "Severe",
    "Red":    "Extreme",
    "Keine":  "Keine",
}

# Konfigurations-Keys
CONF_MODE = "mode"
MODE_MANUAL = "manual"
MODE_GEOLOCATOR = "geolocator"
CONF_COUNTRIES = "countries"
CONF_GEOLOCATOR_ENTITY = "geolocator_entity"
DEFAULT_GEOLOCATOR_ENTITY = "sensor.geolocator_country_code"
