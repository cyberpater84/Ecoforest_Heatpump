"""Constants for the Ecoforest Heat Pump integration."""

DOMAIN = "ecoforest"
DEFAULT_NAME = "Ecoforest"
DEFAULT_PORT = 502
DEFAULT_SLAVE = 1
DEFAULT_SCAN_INTERVAL = 30

CONF_SLAVE = "slave"
CONF_SCAN_INTERVAL = "scan_interval"

# ---------------------------------------------------------------------------
# ecoAIR register map  (uit officieel Ecoforest Modbus Guide)
# Analog registers: raw waarde / 10 => °C / bar / %
# Integer registers: raw waarde direct
# Boolean: coil registers
# ---------------------------------------------------------------------------

# --- ANALOG registers (Function Code 3, Read Holding Registers) ---
# Waarde = register_raw / 10
ANALOG_SENSORS = {
    # adres: (naam, eenheid, device_class, icon)
    1:   ("Aanvoertemperatuur binnenunit",    "°C",  "temperature",  "mdi:thermometer"),
    2:   ("Retourtemperatuur binnenunit",     "°C",  "temperature",  "mdi:thermometer"),
    3:   ("Zuigdruk tussendruk compressor",   "bar", "pressure",     "mdi:gauge"),
    4:   ("Aanvoertemperatuur buitenunit",    "°C",  "temperature",  "mdi:thermometer"),
    5:   ("Retourtemperatuur buitenunit",     "°C",  "temperature",  "mdi:thermometer"),
    6:   ("Druk verwarmingscircuit",          "bar", "pressure",     "mdi:gauge"),
    7:   ("Zuigdruk compressor",             "bar", "pressure",     "mdi:gauge"),
    8:   ("Zuigtemperatuur compressor",      "°C",  "temperature",  "mdi:thermometer"),
    9:   ("Persdruk compressor",             "bar", "pressure",     "mdi:gauge"),
    10:  ("Perstemperatuur compressor",      "°C",  "temperature",  "mdi:thermometer"),
    11:  ("Boilertemperatuur",               "°C",  "temperature",  "mdi:thermometer-water"),
    12:  ("Retourtemperatuur boiler",        "°C",  "temperature",  "mdi:thermometer-water"),
    13:  ("Aanvoertemperatuur groep SG2",    "°C",  "temperature",  "mdi:thermometer"),
    14:  ("Aanvoertemperatuur groep SG3",    "°C",  "temperature",  "mdi:thermometer"),
    17:  ("Buffervattemperatuur verwarming", "°C",  "temperature",  "mdi:thermometer"),
    18:  ("Buffervattemperatuur koeling",    "°C",  "temperature",  "mdi:thermometer"),
    19:  ("Zwembadtemperatuur",              "°C",  "temperature",  "mdi:pool"),
    20:  ("Buitentemperatuur",               "°C",  "temperature",  "mdi:thermometer"),
    21:  ("Aanvoertemperatuur groep SG1",    "°C",  "temperature",  "mdi:thermometer"),
    23:  ("Setpoint bufvat verwarming",      "°C",  "temperature",  "mdi:target"),
    24:  ("Setpoint bufvat koeling",         "°C",  "temperature",  "mdi:target"),
    25:  ("Condensatietemperatuur",          "°C",  "temperature",  "mdi:thermometer"),
    26:  ("Oververhitting",                  "°C",  "temperature",  "mdi:thermometer-chevron-up"),
    27:  ("Verdampingstemperatuur",          "°C",  "temperature",  "mdi:thermometer-chevron-down"),
    28:  ("Expansieventiel opening",         "%",   None,           "mdi:valve"),
    29:  ("Regelaar distributiepompe",       "%",   None,           "mdi:pump"),
    30:  ("Ventilatorregelaar",              "%",   None,           "mdi:fan"),
    31:  ("Regelaar groep SG2",              "%",   None,           "mdi:pump"),
    32:  ("Regelaar groep SG3/boiler",       "%",   None,           "mdi:pump"),
    33:  ("Regelaar groep SG1",              "%",   None,           "mdi:pump"),
    38:  ("Huidig boiler setpoint",          "°C",  "temperature",  "mdi:target"),
    123: ("Eindsetpoint verwarming SG1",     "°C",  "temperature",  "mdi:target"),
    124: ("Eindsetpoint verwarming SG2",     "°C",  "temperature",  "mdi:target"),
    125: ("Eindsetpoint verwarming SG3",     "°C",  "temperature",  "mdi:target"),
    128: ("Eindsetpoint koeling SG1",        "°C",  "temperature",  "mdi:target"),
    129: ("Eindsetpoint koeling SG2",        "°C",  "temperature",  "mdi:target"),
    130: ("Eindsetpoint koeling SG3",        "°C",  "temperature",  "mdi:target"),
    133: ("Actueel verwarmingsvermogen",     "kW",  "power",        "mdi:heat-wave"),
    134: ("Actueel koelvermogen",            "kW",  "power",        "mdi:snowflake"),
    135: ("Actueel elektrisch vermogen",     "kW",  "power",        "mdi:lightning-bolt"),
    136: ("COP verwarming",                  None,  None,           "mdi:chart-line"),
    137: ("EER koeling",                     None,  None,           "mdi:chart-line"),
    142: ("Eindsetpoint zwembad",            "°C",  "temperature",  "mdi:pool"),
    161: ("Ruimtetemperatuur zone 1",        "°C",  "temperature",  "mdi:home-thermometer"),
    162: ("Ruimtetemperatuur zone 2",        "°C",  "temperature",  "mdi:home-thermometer"),
    163: ("Ruimtetemperatuur zone 3",        "°C",  "temperature",  "mdi:home-thermometer"),
    197: ("DT aanvoer buitenunit",           "°C",  "temperature",  "mdi:thermometer"),
    198: ("DT aanvoer binnenunit",           "°C",  "temperature",  "mdi:thermometer"),
    199: ("DT ventilator",                   "°C",  "temperature",  "mdi:fan"),
    200: ("IJsvorming %",                    "%",   None,           "mdi:snowflake-melt"),
    223: ("Compressorreferentie actueel",    "%",   None,           "mdi:gauge"),
    226: ("SPF maandelijks",                 None,  None,           "mdi:chart-line"),
    227: ("SPF jaarlijks",                   None,  None,           "mdi:chart-line"),
}

# R/W analog registers: setpoints die de gebruiker kan schrijven
# adres: (naam, min_val, max_val, step, eenheid)
ANALOG_SETPOINTS = {
    168: ("BUS Boiler setpoint",         0.0,  70.0, 0.5, "°C"),
    169: ("BUS Zwembad setpoint",        0.0,  45.0, 0.5, "°C"),
    170: ("BUS Verwarmingssetpoint SG1", 0.0,  60.0, 0.5, "°C"),
    171: ("BUS Verwarmingssetpoint SG2", 0.0,  60.0, 0.5, "°C"),
    172: ("BUS Verwarmingssetpoint SG3", 0.0,  60.0, 0.5, "°C"),
    175: ("BUS Koelsetpoint SG1",        0.0,  25.0, 0.5, "°C"),
    176: ("BUS Koelsetpoint SG2",        0.0,  25.0, 0.5, "°C"),
    177: ("BUS Koelsetpoint SG3",        0.0,  25.0, 0.5, "°C"),
}

# --- INTEGER registers (Function Code 3, Read Holding Registers) ---
# Waarde = raw integer, geen deling
INTEGER_SENSORS = {
    5002: ("Compressorsnelheid", "rpm", None, "mdi:rotate-right"),
    5022: ("Jaarvermogen verwarming", "kWh", "energy", "mdi:fire"),
    5023: ("Jaarvermogen koeling",    "kWh", "energy", "mdi:snowflake"),
    5024: ("Jaarlijks elektraverbruik", "kWh", "energy", "mdi:lightning-bolt"),
}

# R/W integer registers: demands en programma
# adres: (naam, min, max, stap)
INTEGER_SETPOINTS = {
    5181: ("BUS Boiler vraag",     0, 1, 1),   # 0=uit, 1=aan
    5182: ("BUS Zwembad vraag",    0, 1, 1),   # 0=uit, 1=aan
    5183: ("BUS Vraag SG1",        0, 2, 1),   # 0=niets, 1=verwarmen, 2=koelen
    5184: ("BUS Vraag SG2",        0, 2, 1),
    5185: ("BUS Vraag SG3",        0, 2, 1),
    5188: ("BUS Programma",        0, 2, 1),   # 0=niets, 1=winter, 2=zomer
}

# --- COIL registers (Function Code 1, Read Coils / FC5 Write Single Coil) ---
# Boolean: True=aan, False=uit
COIL_SENSORS = {
    # adres: (naam, icon, invert_logic)
    180: ("Warmtepomp aan/uit via BUS", "mdi:heat-pump", False),
    201: ("Zomerprogramma actief",      "mdi:weather-sunny", False),
    202: ("Winterprogramma actief",     "mdi:weather-snowy", False),
    # Dout states (read-only actuatoren)
    21:  ("Circulatiepomp hydraulisch", "mdi:pump", False),
    22:  ("Zwembad actief",            "mdi:pool", False),
    23:  ("Boiler actief",             "mdi:water-boiler", False),
    24:  ("Boiler recirculatie",       "mdi:water-boiler", False),
    25:  ("Verwarmingsventiel",        "mdi:valve", False),
    26:  ("Koelventiel",               "mdi:valve", False),
    27:  ("SG1 actief",               "mdi:radiator", False),
    28:  ("SG2 actief",               "mdi:radiator", False),
    29:  ("SG3 actief",               "mdi:radiator", False),
    30:  ("Elektrisch element bufvat", "mdi:heating-coil", False),
    31:  ("Elektrisch element boiler", "mdi:heating-coil", False),
    32:  ("Alarmstatus",              "mdi:alarm-light", True),   # 0=alarm, invert=>True=alarm
    33:  ("Ventilator actief",        "mdi:fan", False),
    34:  ("Buitenproductiepompe",     "mdi:pump", False),
    35:  ("Cyclusomkeerventiel",      "mdi:valve", False),
    36:  ("EVI ventiel",              "mdi:valve", False),
}

# Coils die schrijfbaar zijn (FC5)
WRITABLE_COILS = {180}

# Maandelijkse energietellers ecoAIR (Integer, read-only)
# Koeling: 5221-5232, Verwarming: 5233-5244, Elektra: 5245-5256
_MONTHS = ["jan","feb","mrt","apr","mei","jun","jul","aug","sep","okt","nov","dec"]

MONTHLY_ENERGY_SENSORS = {}
for _i, _m in enumerate(_MONTHS):
    MONTHLY_ENERGY_SENSORS[5221 + _i] = (f"Koeling {_m}",   "kWh", "energy", "mdi:snowflake")
    MONTHLY_ENERGY_SENSORS[5233 + _i] = (f"Verwarming {_m}","kWh", "energy", "mdi:fire")
    MONTHLY_ENERGY_SENSORS[5245 + _i] = (f"Elektra {_m}",   "kWh", "energy", "mdi:lightning-bolt")

# Maandelijkse prestatiefactor (Analog, adres 211-222)
for _i, _m in enumerate(_MONTHS):
    ANALOG_SENSORS[211 + _i] = (f"PF {_m}", None, None, "mdi:chart-line")
