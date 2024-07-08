"""API for Electrolux Status."""

import json
import logging
import re
from typing import Any

from pyelectroluxocp.apiModels import ApplianceInfoResponse, ApplienceStatusResponse

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.button import ButtonDeviceClass
from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import Platform, UnitOfTemperature

from .binary_sensor import ElectroluxBinarySensor
from .button import ElectroluxButton
from .const import (
    BINARY_SENSOR,
    BUTTON,
    COMMON_ATTRIBUTES,
    NUMBER,
    SELECT,
    SENSOR,
    STATIC_ATTRIBUTES,
    SWITCH,
    Catalog,
    icon_mapping,
)
from .entity import ElectroluxEntity
from .model import ElectroluxDevice
from .number import ElectroluxNumber
from .select import ElectroluxSelect
from .sensor import ElectroluxSensor
from .switch import ElectroluxSwitch

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class ElectroluxLibraryEntity:
    """Electrolux Library Entity."""

    def __init__(
        self,
        name,
        status: str,
        state: ApplienceStatusResponse,
        appliance_info: ApplianceInfoResponse,
        capabilities: dict[str, any],
    ) -> None:
        """Initaliaze the entity."""
        self.name = name
        self.status = status
        self.state = state
        self.reported_state = self.state["properties"]["reported"]
        self.appliance_info = appliance_info
        self.capabilities = capabilities

    def get_name(self):
        """Get entity name."""
        return self.name

    def get_value(self, attr_name, source=None):
        """Return value by attribute."""
        if source and source != "":
            container: dict[str, any] | None = self.reported_state.get(source, None)
            entry = None if container is None else container.get(attr_name, None)
        else:
            entry = self.reported_state.get(attr_name, None)
        return entry

    def get_sensor_name(self, attr_name: str, container: str | None = None):
        """Get the name of the sensor."""
        attr_name = attr_name.rpartition("/")[-1] or attr_name
        attr_name = attr_name[0].upper() + attr_name[1:]
        attr_name = attr_name.replace("_", " ")
        if container and "/" in container:
            attr_name = container.rpartition("/")[0] + attr_name
        group = ""
        words = []
        s = attr_name
        for i in range(len(s)):  # [consider-using-enumerate]
            char = s[i]
            if group == "":
                group = char
            else:
                if char == " " and len(group) > 0:
                    words.append(group)
                    group = ""
                    continue

                if (
                    (char.isupper() or char.isdigit())
                    and (s[i - 1].isupper() or s[i - 1].isdigit())
                    and (
                        (i == len(s) - 1) or (s[i + 1].isupper() or s[i + 1].isdigit())
                    )
                ):
                    group += char
                elif (char.isupper() or char.isdigit()) and s[i - 1].islower():
                    if re.match("^[A-Z0-9]+$", group):
                        words.append(group)
                    else:
                        words.append(group.lower())
                    group = char
                else:
                    group += char
        if len(group) > 0:
            if re.match("^[A-Z0-9]+$", group):
                words.append(group)
            else:
                words.append(group.lower())
        return " ".join(words)

    def get_sensor_name_old(self, attr_name: str, container: str | None = None):
        """Convert sensor format.

        ex: "fCMiscellaneousState/detergentExtradosage" to "Detergent extradosage".
        """
        attr_name = attr_name.rpartition("/")[-1] or attr_name
        attr_name = attr_name[0].upper() + attr_name[1:]
        attr_name = " ".join(re.findall("[A-Z][^A-Z]*", attr_name))
        return attr_name.capitalize()

    def get_category(self, attr_name: str):
        """Extract category.

        ex: "fCMiscellaneousState/detergentExtradosage" to "fCMiscellaneousState".
        or "" if none
        """
        return attr_name.rpartition("/")[0]

    def get_capability(self, attr_name: str) -> dict[str, any] | None:
        """Retrieve the capability from self.capabilities using the attribute name.

        May contain slashes for nested keys.
        """
        keys = attr_name.split("/")
        result = self.capabilities

        for key in keys:
            result = result.get(key)
            if result is None:
                return None

        return result
    def get_entity_name(self, attr_name: str, container: str | None = None):
        """Convert Entity Name.

        ex: Convert format "fCMiscellaneousState/detergentExtradosage" to "detergentExtradosage"
        """
        return attr_name.rpartition("/")[-1] or attr_name

    def get_entity_unit(self, attr_name: str):
        """Get entity unit type."""
        capability_def: dict[str, any] | None = self.get_capability(attr_name)
        if not capability_def:
            return None
        # Type : string, int, number, boolean (other values ignored)
        type_units = capability_def.get("type", None)
        if not type_units:
            return None
        if type_units == "temperature":
            return UnitOfTemperature.CELSIUS
        return None

    def get_entity_device_class(self, attr_name: str):
        """Get entity device class."""
        capability_def: dict[str, any] | None = self.get_capability(attr_name)
        if not capability_def:
            return None
        # Type : string, int, number, boolean (other values ignored)
        type_class = capability_def.get("type", None)
        if not type_class:
            return None
        if type_class == "temperature":
            return SensorDeviceClass.TEMPERATURE
        return None

    def get_entity_type(self, attr_name: str):
        """Get entity type."""
        capability_def: dict[str, any] | None = self.get_capability(attr_name)
        if not capability_def:
            return None

        # Type : string, int, number, boolean (other values ignored)
        type_object = capability_def.get("type", None)
        if not type_object:
            return None

        # Access : read, readwrite (other values ignored)
        access = capability_def.get("access", None)
        if not access:
            return None

        # Exception (Electrolux bug)
        if (
            type_object == "boolean"
            and access == "readwrite"
            and capability_def.get("values", None) is not None
        ):
            return SWITCH

        # List of values ? if values is defined and has at least 1 entry
        values: dict[str, any] | None = capability_def.get("values", None)
        if (
            values
            and access == "readwrite"
            and isinstance(values, dict)
            and len(values) > 0
        ):
            if type_object != "number" or capability_def.get("min", None) is None:
                return SELECT

        match type_object:
            case "boolean":
                if access == "read":
                    return BINARY_SENSOR
                if access == "readwrite":
                    return SWITCH
            case "temperature":
                if access == "read":
                    return SENSOR
                if access == "readwrite":
                    return NUMBER
            case _:
                if access == "read" and type_object in [
                    "number",
                    "int",
                    "boolean",
                    "string",
                ]:
                    return SENSOR
                if type_object in ("int", "number"):
                    return NUMBER
        _LOGGER.debug(
            "Electrolux unable to determine type for %s. Type: %s Access: %s",
            attr_name,
            type_object,
            access,
        )
        return None

    def sources_list(self):
        """List the capability types."""
        if self.capabilities is None:
            return None
        return [
            key
            for key in list(self.capabilities.keys())
            if not key.startswith("applianceCareAndMaintenance")
        ]


class Appliance:
    """Define the Appliance Class."""

    brand: str
    device: str
    entities: list[ElectroluxEntity]
    coordinator: any

    def __init__(
        self,
        coordinator: any,
        name: str,
        pnc_id: str,
        brand: str,
        model: str,
        state: ApplienceStatusResponse,
    ) -> None:
        """Initiate the appliance."""
        self.own_capabilties = False
        self.data = None
        self.coordinator = coordinator
        self.model = model
        self.pnc_id = pnc_id
        self.name = name
        self.brand = brand
        self.state: ApplienceStatusResponse = state

    def update_missing_entities(self) -> None:
        """Add missing entities when no capabilities returned by the API, do it dynamically."""
        if not self.own_capabilties:
            return
        properties = self.state.get("properties")
        capability = ""
        if properties:
            reported = properties.get("reported")
            if reported:
                for key, items in Catalog.items():
                    for item in items:
                        category = item.category
                        if (
                            category
                            and reported.get(category, None)
                            and reported.get(category, None).get(key)
                        ) or (not category and reported.get(key, None)):
                            found: bool = False
                            for entity in self.entities:
                                if (
                                    entity.entity_attr == key
                                    and entity.entity_source == category
                                ):
                                    found = True
                                    capability = (
                                        key if category is None else category + "/" + key
                                    )
                                    self.data.capabilities[capability] = item.capability_info
                                    break
                            if not found:
                                _LOGGER.debug(
                                    "Electrolux discovered new entity from extracted data. Category: %s Key: %s",
                                    category,
                                    key,
                                )
                                entity = self.get_entity(capability)
                                if entity:
                                    self.entities.append(entity)

    def get_entity(self, capability: str) -> list[ElectroluxEntity] | None:
        """Return the entity."""
        entity_type = self.data.get_entity_type(capability)
        entity_name = self.data.get_entity_name(capability)
        category = self.data.get_category(capability)
        capability_info: dict[str, any] = self.data.get_capability(capability)
        device_class = self.data.get_entity_device_class(capability)
        entity_category = None
        entity_icon = None
        unit = self.data.get_entity_unit(capability)
        display_name = f"{self.data.get_name()} {self.data.get_sensor_name(entity_name, capability)}"

        # item : capability, category, DeviceClass, Unit, EntityCategory
        catalog_item = Catalog.get(capability, None)
        if catalog_item:
            if capability_info is None:
                capability_info = catalog_item.capability_info
            elif (
                "values" not in capability_info
                and "values" in catalog_item.capability_info
            ):
                capability_info["values"] = catalog_item.capability_info["values"]

            device_class = catalog_item.device_class
            unit = catalog_item.unit
            entity_category = catalog_item.entity_category
            entity_icon = catalog_item.entity_icon

        if isinstance(device_class, BinarySensorDeviceClass):
            entity_type = BINARY_SENSOR
        if isinstance(device_class, ButtonDeviceClass):
            entity_type = BUTTON
        if isinstance(device_class, NumberDeviceClass):
            entity_type = NUMBER
        if isinstance(device_class, SensorDeviceClass):
            entity_type = SENSOR
        if isinstance(device_class, SwitchDeviceClass):
            entity_type = SWITCH

        if catalog_item and isinstance(catalog_item.entity_platform, Platform):
            entity_type = catalog_item.entity_platform

        _LOGGER.debug(
            "Electrolux get_entity. entity_type: %s entity_attr: %s entity_source: %s capability: %s device_class: %s unit: %s",
            entity_type,
            entity_name,
            category,
            capability_info,
            device_class,
            unit,
        )

        def electrolux_entity_factory(
            name,
            entity_type,
            entity_attr,
            entity_source,
            capability,
            unit,
            entity_category,
            device_class,
            icon,
            catalog_entry,
        ):
            entity_classes = {
                BINARY_SENSOR: ElectroluxBinarySensor,
                NUMBER: ElectroluxNumber,
                SELECT: ElectroluxSelect,
                SENSOR: ElectroluxSensor,
                SWITCH: ElectroluxSwitch,
            }

            entity_class = entity_classes.get(entity_type)

            if entity_class is None:
                raise ValueError(f"Unknown entity type: {entity_type}")

            return [
                entity_class(
                    coordinator=self.coordinator,
                    config_entry=self.coordinator.config_entry,
                    pnc_id=self.pnc_id,
                    name=name,
                    entity_type=entity_type,
                    entity_attr=entity_attr,
                    entity_source=entity_source,
                    capability=capability,
                    unit=unit,
                    entity_category=entity_category,
                    device_class=device_class,
                    icon=icon,
                    catalog_entry=catalog_entry,
                )
            ]

        if entity_type in [BINARY_SENSOR, NUMBER, SELECT, SENSOR, SWITCH]:
            return electrolux_entity_factory(
                name=display_name,
                entity_type=entity_type,
                entity_attr=entity_name,
                entity_source=category,
                capability=capability_info,
                unit=unit,
                entity_category=entity_category,
                device_class=device_class,
                icon=entity_icon,
                catalog_entry=catalog_item,
            )

        if entity_type == BUTTON:
            commands: dict[str, str] = capability_info.get("values", {})
            commands_keys = list(commands.keys())
            return [
                ElectroluxButton(
                    name=f"{display_name} {command.lower()}"
                    if len(commands_keys) > 1
                    else display_name,
                    coordinator=self.coordinator,
                    config_entry=self.coordinator.config_entry,
                    entity_type=entity_type,
                    entity_attr=entity_name,
                    entity_source=category,
                    pnc_id=self.pnc_id,
                    capability=capability_info,
                    entity_category=entity_category,
                    device_class=device_class,
                    icon=entity_icon
                    or icon_mapping.get(command, "mdi:gesture-tap-button"),
                    val_to_send=command,
                    catalog_entry=catalog_item,
                )
                for command in commands_keys
            ]
        return []

    def setup(self, data: ElectroluxLibraryEntity):
        """Configure the entity."""
        self.data: ElectroluxLibraryEntity = data
        self.entities: list[ElectroluxEntity] = []
        entities: list[ElectroluxEntity] = []
        # Extraction of the appliance capabilities & mapping to the known entities of the component
        capabilities_names = self.data.sources_list()  # [ "applianceState", "autoDosing",..., "userSelections/analogTemperature",...]

        if capabilities_names is None and self.state:
            # No capabilities returned (unstable API)
            # We could rebuild them from catalog but this creates entities that are
            # not required by each device type (fridge, dryer, vacumn etc are all different)
            _LOGGER.warning("Electrolux API returned no capability definition")

        # Add static attribute
        # these are attributes that are not in the capability entry
        # but are returned by the api independantly
        for static_attribute in STATIC_ATTRIBUTES:
            _LOGGER.debug("Electrolux static_attribute %s", static_attribute)
            # attr not found in state, next attr
            if self.get_state(static_attribute) is None:
                continue
            if catalog_item := Catalog.get(static_attribute, None):
                if (entity := self.get_entity(static_attribute)) is None:
                    # catalog definition and automatic checks fail to determine type
                    _LOGGER.debug(
                        "Electrolux static_attribute undefined %s", static_attribute
                    )
                    continue
                # add to the capability dict
                keys = static_attribute.split("/")
                capabilities = self.data.capabilities
                for key in keys[:-1]:
                    capabilities = capabilities.setdefault(key, {})
                capabilities[keys[-1]] = catalog_item.capability_info
                _LOGGER.debug("Electrolux adding static_attribute %s", static_attribute)
                entities.extend(entity)

        # For each capability src
        for capability in capabilities_names:
            if entity := self.get_entity(capability):
                entities.extend(entity)

        # Setup each found entity
        self.entities = entities
        for entity in entities:
            entity.setup(data)

    def update_reported_data(self, reported_data: dict[str, any]):
        """Update the reported data."""
        _LOGGER.debug("Electrolux update reported data %s", reported_data)
        try:
            local_reported_data = self.state.get("properties", None).get(
                "reported", None
            )
            local_reported_data.update(reported_data)
            _LOGGER.debug("Electrolux updated reported data %s", self.state)
            self.update_missing_entities()
            for entity in self.entities:
                entity.update(self.state)

        except Exception as ex:  # noqa: BLE001
            _LOGGER.debug(
                "Electrolux status could not update reported data with %s. %s",
                reported_data,
                ex,
            )

    def update(self, appliance_status: ApplienceStatusResponse):
        """Update appliance status."""
        self.state = appliance_status
        self.update_missing_entities()
        for entity in self.entities:
            entity.update(self.state)


class Appliances:
    """Appliance class definition."""

    def __init__(self, appliances: dict[str, Appliance]) -> None:
        """Initialize the class."""
        self.appliances = appliances

    def get_appliance(self, pnc_id) -> Appliance:
        """Return the appliance."""
        return self.appliances.get(pnc_id, None)

    def get_appliances(self) -> dict[str, Appliance]:
        """Return all appliances."""
        return self.appliances

    def get_appliance_ids(self) -> list[str]:
        """Return all appliance ids."""
        return list(self.appliances)
