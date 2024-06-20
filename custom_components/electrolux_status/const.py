"""The electrolux Status constants."""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTime,
    UnitOfTemperature,
    UnitOfPower,
    UnitOfVolume,
)
from homeassistant.helpers.entity import EntityCategory
from .model import ElectroluxDevice

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
BUTTON = "button"
NUMBER = "number"
SELECT = "select"
SENSOR = "sensor"
SWITCH = "switch"
PLATFORMS = [BINARY_SENSOR, BUTTON, NUMBER, SELECT, SENSOR, SWITCH]

# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_LANGUAGE = "language"
CONF_RENEW_INTERVAL = "renew_interval"

# Defaults
DEFAULT_LANGUAGE = "English"
DEFAULT_WEBSOCKET_RENEWAL_DELAY = 43200  # 12 hours

# Common entities
COMMON_ATTRIBUTES = [
    "connectivityState",
    "networkInterface/linkQualityIndicator",
    "applianceMode",
]

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

TIME_ENTITIES_TO_UPDATE = ["timeToEnd"]


Catalog: dict[str, list[ElectroluxDevice]] = {
    "timeToEnd": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "number"},
            category=None,
            device_class=None,
            unit=UnitOfTime.SECONDS,
            entity_category=None,
            entity_icon="mdi:av-timer",
        )
    ],
    "runningTime": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "number"},
            category=None,
            device_class=None,
            unit=UnitOfTime.SECONDS,
            entity_category=None,
            entity_icon="mdi:timelapse",
        )
    ],
    "cyclePhase": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "string"},
            category=None,
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon=None,
        )
    ],
    "cycleSubPhase": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "string"},
            category=None,
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon=None,
        )
    ],
    "applianceState": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "string"},
            category=None,
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon="mdi:state-machine",
        )
    ],
    "displayTemperature": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "string"},
            category=None,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit=None,
            entity_category=None,
            entity_icon="mdi:thermometer",
        )
    ],
    "displayFoodProbeTemperature": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "number"},
            category=None,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit=UnitOfTemperature.CELSIUS,
            entity_category=None,
            entity_icon="mdi:thermometer",
        )
    ],
    "sensorTemperature": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "number"},
            category=None,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit=UnitOfTemperature.CELSIUS,
            entity_category=None,
            entity_icon="mdi:thermometer",
        )
    ],
    "defrostTemperature": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "number"},
            category=None,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit=UnitOfTemperature.CELSIUS,
            entity_category=None,
            entity_icon="mdi:snowflake-thermometer",
        )
    ],
    "targetMicrowavePower": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "number"},
            category=None,
            device_class=SensorDeviceClass.ENERGY,
            unit=UnitOfPower.WATT,
            entity_category=None,
            entity_icon="mdi:microwave",
        )
    ],
    "ovenProcessIdentifier": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "string"},
            category=None,
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon="mdi:application-settings-outline",
        )
    ],
    "remoteControl": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "string"},
            category=None,
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon="mdi:remote",
        )
    ],
    "defaultExtraRinse": [
        ElectroluxDevice(
            capability_info={
                "access": "readwrite",
                "type": "string",
                "values": {
                    "EXTRA_RINSE_1": {},
                    "EXTRA_RINSE_2": {},
                    "EXTRA_RINSE_OFF": {},
                },
            },
            category=None,
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon=None,
        )
    ],
    "analogTemperature": [
        ElectroluxDevice(
            capability_info={
                "access": "readwrite",
                "type": "string",
                "values": {
                    "20_CELSIUS": {},
                    "30_CELSIUS": {},
                    "40_CELSIUS": {},
                    "50_CELSIUS": {},
                    "60_CELSIUS": {},
                    "90_CELSIUS": {},
                    "95_CELSIUS": {},
                    "COLD": {},
                },
            },
            category="userSelections",
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon="mdi:thermometer",
        )
    ],
    "targetTemperatureC": [
        ElectroluxDevice(
            capability_info={
                "access": "readwrite",
                "type": "number",
                "max": 300.0,
                "min": 0,
                "step": 5.0,
            },
            category=None,
            device_class=SensorDeviceClass.TEMPERATURE,
            unit=UnitOfTemperature.CELSIUS,
            entity_category=None,
            entity_icon="mdi:thermometer",
        )
    ],
    # "targetTemperature": ["container", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS],
    "startTime": [
        ElectroluxDevice(
            capability_info={
                "access": "readwrite",
                "type": "number",
                "max": 72000,
                "min": 0,
                "step": 1800,
            },
            category=None,
            device_class=None,
            unit=UnitOfTime.SECONDS,
            entity_category=None,
            entity_icon="mdi:clock-start",
        )
    ],
    "waterSoftenerMode": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "string"},
            category=None,
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon="mdi:water-check",
        )
    ],
    "steamValue": [
        ElectroluxDevice(
            capability_info={
                "access": "read",
                "type": "string",
                "values": {
                    "STEAM_MAX": {},
                    "STEAM_MED": {},
                    "STEAM_MIN": {},
                    "STEAM_OFF": {},
                },
            },
            category="userSelections",
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon="mdi:pot-steam",
        )
    ],
    "analogSpinSpeed": [
        ElectroluxDevice(
            capability_info={
                "access": "readwrite",
                "type": "string",
                "values": {
                    "0_RPM": {},
                    "1000_RPM": {},
                    "1200_RPM": {},
                    "1400_RPM": {},
                    "1600_RPM": {},
                    "400_RPM": {},
                    "600_RPM": {},
                    "800_RPM": {},
                    "DISABLED": {"disabled": True},
                },
            },
            category="userSelections",
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon="mdi:speedometer",
        )
    ],
    "programUID": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "string"},
            category="userSelections",
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon="mdi:application-settings-outline",
        )
    ],
    "doorState": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "string"},
            category=None,
            device_class=BinarySensorDeviceClass.DOOR,
            unit=None,
            entity_category=None,
            entity_icon="mdi:door",
        ),
    ],
    "doorLock": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "string"},
            category=None,
            device_class=BinarySensorDeviceClass.LOCK,
            unit=None,
            entity_category=None,
            entity_icon="mdi:door-closed-lock",
        )
    ],
    "uiLockMode": [
        ElectroluxDevice(
            capability_info={
                "access": "readwrite",
                "type": "boolean",
                "values": {"OFF": {}, "ON": {}},
            },
            category=None,
            device_class=BinarySensorDeviceClass.LOCK,
            unit=None,
            entity_category=None,
            entity_icon="mdi:lock",
        )
    ],
    "endOfCycleSound": [
        ElectroluxDevice(
            capability_info={
                "access": "readwrite",
                "type": "string",
                "values": {"NO_SOUND": {}, "SHORT_SOUND": {}},
            },
            category=None,
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon="mdi:cellphone-sound",
        )
    ],
    "preWashPhase": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "boolean"},
            category=None,
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon="mdi:washing-machine",
        )
    ],
    # "eLUXTimeManagerLevel": ["valTransl", None, None],
    # "waterTankWarningMode": [None, None, None],
    # "dryingTime": [None, None, None],
    # "humidityTarget": ["valTransl", None, None],
    # "antiCreaseValue": [None, None, None],
    # "drynessValue": ["valTransl", None, None],
    # "programUID": ["valTransl", None, None],
    # "sensorHumidity": ["numberValue", SensorDeviceClass.HUMIDITY, PERCENTAGE, None],
    # "ambientTemperature": ["container", SensorDeviceClass.TEMPERATURE, UnitOfTemperature.CELSIUS, None],
    "applianceTotalWorkingTime": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "number"},
            category=None,
            device_class=None,
            unit=UnitOfTime.SECONDS,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_icon="mdi:clock-time-eight-outline",
        )
    ],
    "totalCycleCounter": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "number"},
            category=None,
            device_class=None,
            unit=None,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_icon="mdi:counter",
        )
    ],
    "waterHardness": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "string"},
            category=None,
            device_class=None,
            unit=None,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_icon="mdi:water",
        )
    ],
    "applianceMode": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "string"},
            category=None,
            device_class=None,
            unit=None,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_icon="mdi:auto-mode",
        )
    ],
    "totalWashingTime": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "number"},
            category=None,
            device_class=None,
            unit=UnitOfTime.SECONDS,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_icon="mdi:washing-machine",
        )
    ],
    "linkQualityIndicator": [
        ElectroluxDevice(
            capability_info={
                "access": "read",
                "type": "string",
                "values": {
                    "EXCELLENT": {},
                    "GOOD": {},
                    "POOR": {},
                    "UNDEFINED": {},
                    "VERY_GOOD": {},
                    "VERY_POOR": {},
                },
            },
            category="networkInterface",
            device_class=None,
            unit=None,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_icon="mdi:wifi-strength-2",
        )
    ],
    "executeCommand": [
        ElectroluxDevice(
            capability_info={
                "access": "write",
                "type": "string",
                "values": {
                    "OFF": {},
                    "ON": {},
                    "PAUSE": {},
                    "RESUME": {},
                    "START": {},
                    "STOPRESET": {},
                },
            },
            category=None,
            device_class=None,
            unit=None,
            entity_category=None,
            entity_icon=None,
        )
    ],
    # "rinseAidLevel": [None, None, None],
    # "fCTotalWashCyclesCount": [None, None, None],
    # "fCTotalWashingTime": [None, None, None],
    # "applianceMode": [None, None, None],
    "connectivityState": [
        ElectroluxDevice(
            capability_info={"access": "read", "type": "string"},
            category=None,
            device_class=None,
            unit=None,
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_icon="mdi:wifi",
        )
    ],
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
