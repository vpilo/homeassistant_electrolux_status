"""The electrolux Status constants."""
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfTime, UnitOfTemperature, UnitOfPower
from homeassistant.helpers.entity import EntityCategory

# Base component constants
NAME = "Elettrolux status"
DOMAIN = "electrolux_status"
DOMAIN_DATA = f"{DOMAIN}_data"

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
BUTTON = "button"
SELECT = "select"
SWITCH = "switch"
NUMBER = "number"
PLATFORMS = [BINARY_SENSOR, SENSOR, BUTTON, SELECT, SWITCH, NUMBER]

# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_LANGUAGE = "language"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_LANGUAGE = "English"

# Common entities
COMMON_ATTRIBUTES = ["connectivityState", "networkInterface/linkQualityIndicator"]

# capabilities model :
#
# key = "entry" or "category/entry"
# {
#   access = "read" or "readwrite" or "write" (other values ignored)
#   type = "boolean" or "string" or "number" (other values ignored including "int" type only used in maintenance section)
#   => problem to differentiate classic numbers to time : check after "time" string in key name ? or temperature
#   values (optional)= list of available values
#   min / max / step for type = number
# }

Catalog: dict[str, [dict, str, str, str, str]] = {
        "timeToEnd": [{"access": "read","type": "number"}, None, None, UnitOfTime.SECONDS, None],
        "runningTime": [{"access": "read","type": "number"}, None, None, UnitOfTime.SECONDS, None],
        "cyclePhase": [{"access": "read","type": "string"}, None, None, None, None],
        "cycleSubPhase": [{"access": "read","type": "string"}, None, None, None, None],
        "applianceState": [{"access": "read","type": "string"}, None, None, None, None],
        "displayTemperature": [{"access": "read","type": "string"}, None, SensorDeviceClass.TEMPERATURE, None, None],
        "displayFoodProbeTemperature": [{"access": "read","type": "number"}, None, SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None],
        "sensorTemperature": [{"access": "read","type": "number"}, None, SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None],
        "defrostTemperature": [{"access": "read","type": "number"}, None, SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None],
        "targetMicrowavePower": [{"access": "read","type": "number"}, None, SensorDeviceClass.ENERGY, UnitOfPower.WATT, None],
        "ovenProcessIdentifier": [{"access": "read","type": "string"}, None, None, None, None],
        "remoteControl": [{"access": "read","type": "string"}, None, None, None, None],
        "defaultExtraRinse": [{"access": "readwrite","type": "string", "values": {"EXTRA_RINSE_1": {},"EXTRA_RINSE_2": {},"EXTRA_RINSE_OFF": {}}}, None, None, None, None],
        "analogTemperature": [{"access": "readwrite","type": "string", "values": {"20_CELSIUS": {},"30_CELSIUS": {},"40_CELSIUS": {},"50_CELSIUS": {},"60_CELSIUS": {},"90_CELSIUS": {},"95_CELSIUS": {},"COLD": {}}}, "userSelections", None, None, None],
        # "targetTemperature": ["container", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS],
        "startTime": [{"access": "readwrite","type": "number","max": 72000,"min": 0,"step": 1800}, None, None, UnitOfTime.SECONDS, None],
        "waterSoftenerMode": [{"access": "read","type": "string"}, None, None, None, None],
        "steamValue": [{"access": "read","type": "string","values": {"STEAM_MAX": {},"STEAM_MED": {},"STEAM_MIN": {},"STEAM_OFF": {}}}, "userSelections", None, None, None],
        "analogSpinSpeed": [{"access": "readwrite","type": "string","values": {"0_RPM": {},"1000_RPM": {},"1200_RPM": {},"1400_RPM": {},"1600_RPM": {},"400_RPM": {},"600_RPM": {},"800_RPM": {},"DISABLED": {"disabled": True}}}, "userSelections", None, None, None],
        "programUID": [{"access": "read","type": "string"}, "userSelections", None, None, None],
        "doorState": [{"access": "read","type": "string"}, None, BinarySensorDeviceClass.DOOR, None, None],
        "doorLock": [{"access": "read","type": "string"}, None, BinarySensorDeviceClass.LOCK, None, None],
        "uiLockMode": [{"access": "readwrite","type": "boolean"}, None, None, None, None],
        "endOfCycleSound": [{"access": "readwrite","type": "string","values": {"NO_SOUND": {},"SHORT_SOUND": {}}}, None, None, None, None],
        "preWashPhase": [{"access": "read","type": "boolean"}, None, None, None, None],
        # "eLUXTimeManagerLevel": ["valTransl", None, None],
        # "waterTankWarningMode": [None, None, None],
        # "dryingTime": [None, None, None],
        # "humidityTarget": ["valTransl", None, None],
        # "antiCreaseValue": [None, None, None],
        # "drynessValue": ["valTransl", None, None],
        # "programUID": ["valTransl", None, None],
        # "sensorHumidity": ["numberValue", SensorDeviceClass.HUMIDITY, PERCENTAGE, None],
        # "ambientTemperature": ["container", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None],
        "applianceTotalWorkingTime": [{"access": "read", "type": "number"}, None, None, UnitOfTime.MINUTES, EntityCategory.DIAGNOSTIC],
        "totalCycleCounter": [{"access": "read", "type": "number"}, None, None, None, EntityCategory.DIAGNOSTIC],
        "waterHardness": [{"access": "read", "type": "string"}, None, None, None, EntityCategory.DIAGNOSTIC],
        "applianceMode": [{"access": "read", "type": "string"}, None, None, None, EntityCategory.DIAGNOSTIC],
        "totalWashingTime": [{"access": "read", "type": "number"}, None, None, UnitOfTime.SECONDS, EntityCategory.DIAGNOSTIC],
        "linkQualityIndicator": [{"access": "read", "type": "string", "values": {"EXCELLENT": {},"GOOD": {},"POOR": {},"UNDEFINED": {},"VERY_GOOD": {},"VERY_POOR": {}}}, "networkInterface", None, None, EntityCategory.DIAGNOSTIC],
        "executeCommand": [{"access": "write", "type": "string", "values": {"OFF": {},"ON": {},"PAUSE": {},"RESUME": {},"START": {},"STOPRESET": {}}}, None, None, None, None],
        # "rinseAidLevel": [None, None, None],
        # "fCTotalWashCyclesCount": [None, None, None],
        # "fCTotalWashingTime": [None, None, None],
        # "applianceMode": [None, None, None],
        "connectivityState": [{"access": "read","type": "string"}, None, None, None, EntityCategory.DIAGNOSTIC],
}

icon_mapping = {
    "OFF": "mdi:power-off",
    "ON": "mdi:power-on",
    "START": "mdi:play",
    "STOPRESET": "mdi:stop",
    "PAUSE": "mdi:pause",
    "RESUME": "mdi:play-pause",
}

# List of supported Mobile App languages (from https://emea-production.api.electrolux.net/masterdata-service/api/v1/languages)
languages = {
    "български": "bul",
    "český": "ces",
    "Dansk": "dan",
    "Deutsch": "deu",
    "ελληνικός": "ell",
    "English": "eng",
    "eesti": "est",
    "Soome": "fin",
    "Français": "fra",
    "Hrvatski": "hrv",
    "magyar": "hun",
    "Italiano": "ita",
    "lettone": "lav",
    "lituano": "lit",
    "Luxembourgish": "ltz",
    "nederlands": "nld",
    "Norsk": "nor",
    "Polski": "pol",
    "Português": "por",
    "Română": "ron",
    "rusesc": "rus",
    "slovenský": "slk",
    "slovinský": "slv",
    "Español": "spa",
    "Svenska": "swe",
    "Türk": "tur",
    "Ukrayna": "ukr",
}
