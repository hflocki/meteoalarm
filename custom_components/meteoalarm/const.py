DOMAIN = "meteoalarm"
SCAN_INTERVAL_MINUTES = 15

# Ländername + Feed-Slug kombiniert: code -> (name, slug)
COUNTRIES_DATA = {
    "ad": ("Andorra", "andorra"),
    "at": ("Österreich", "austria"),
    "ba": ("Bosnien-Herzegowina", "bosnia-herzegovina"),
    "be": ("Belgien", "belgium"),
    "bg": ("Bulgarien", "bulgaria"),
    "ch": ("Schweiz", "switzerland"),
    "cy": ("Zypern", "cyprus"),
    "cz": ("Tschechien", "czechia"),
    "de": ("Deutschland", "germany"),
    "dk": ("Dänemark", "denmark"),
    "ee": ("Estland", "estonia"),
    "es": ("Spanien", "spain"),
    "fi": ("Finnland", "finland"),
    "fr": ("Frankreich", "france"),
    "gr": ("Griechenland", "greece"),
    "hr": ("Kroatien", "croatia"),
    "hu": ("Ungarn", "hungary"),
    "ie": ("Irland", "ireland"),
    "il": ("Israel", "israel"),
    "is": ("Island", "iceland"),
    "it": ("Italien", "italy"),
    "lt": ("Litauen", "lithuania"),
    "lu": ("Luxemburg", "luxembourg"),
    "lv": ("Lettland", "latvia"),
    "md": ("Moldau", "moldova"),
    "me": ("Montenegro", "montenegro"),
    "mk": ("Nordmazedonien", "republic-of-north-macedonia"),
    "mt": ("Malta", "malta"),
    "nl": ("Niederlande", "netherlands"),
    "no": ("Norwegen", "norway"),
    "pl": ("Polen", "poland"),
    "pt": ("Portugal", "portugal"),
    "ro": ("Rumänien", "romania"),
    "rs": ("Serbien", "serbia"),
    "se": ("Schweden", "sweden"),
    "si": ("Slowenien", "slovenia"),
    "sk": ("Slowakei", "slovakia"),
    "ua": ("Ukraine", "ukraine"),
    "uk": ("Großbritannien", "united-kingdom"),
}

# Abgeleitete Dicts für Rückwärtskompatibilität
COUNTRIES = {k: v[0] for k, v in COUNTRIES_DATA.items()}
COUNTRY_FEED_SLUG = {k: v[1] for k, v in COUNTRIES_DATA.items()}

# CAP severity → interne Warnstufe
CAP_SEVERITY_MAP = {
    "Minor": "Yellow",
    "Moderate": "Orange",
    "Severe": "Red",
    "Extreme": "Red",
    "Unknown": "Keine",
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
DEFAULT_GEOLOCATOR_ENTITY = "sensor.geolocator_country_code"

# Abgelaufene Warnungen (expires in der Vergangenheit) herausfiltern
# True = nur aktive Warnungen anzeigen (empfohlen)
# False = alle Warnungen wie vom Feed geliefert
FILTER_EXPIRED = True
