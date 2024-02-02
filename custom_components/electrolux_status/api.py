import json
import logging
import re

from pyelectroluxocp.apiModels import ApplianceInfoResponse, ApplienceStatusResponse

from .binary_sensor import ElectroluxBinarySensor
from .button import ElectroluxButtonEntity
from .const import BINARY_SENSOR, SENSOR, BUTTON, icon_mapping, SELECT, SWITCH, NUMBER, Catalog
from .entity import ElectroluxEntity
from .number import ElectroluxNumber
from .select import ElectroluxSelect
from .sensor import ElectroluxSensor
from .switch import ElectroluxSwitch

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class ElectroluxLibraryEntity:
    def __init__(self, name, status: str, state: ApplienceStatusResponse, appliance_info: ApplianceInfoResponse,
                 capabilities: dict[str, any]):
        self.name = name
        self.status = status
        self.state = state
        self.reported_state = self.state["properties"]["reported"]
        self.appliance_info = appliance_info
        self.capabilities = capabilities

    def get_name(self):
        return self.name

    def get_value(self, attr_name, source=None):
        if source and source != '':
            container: dict[str, any] | None = self.reported_state.get(source, None)
            entry = None if container is None else container.get(attr_name, None)
        else:
            entry = self.reported_state.get(attr_name, None)
        return entry

    def get_sensor_name(self, attr_name: str, container: str = None):
        # Convert format "fCMiscellaneousState/detergentExtradosage" to "Detergent extradosage"
        attr_name = attr_name.rpartition('/')[-1] or attr_name
        attr_name = attr_name[0].upper() + attr_name[1:]
        attr_name = " ".join(re.findall('[A-Z][^A-Z]*', attr_name))
        attr_name = attr_name.capitalize()
        return attr_name

    def get_category(self, attr_name: str):
        # Extract category ex: "fCMiscellaneousState/detergentExtradosage" to "fCMiscellaneousState"
        # or "" if none
        return attr_name.rpartition('/')[0]

    def get_entity_name(self, attr_name: str, container: str = None):
        # Convert format "fCMiscellaneousState/detergentExtradosage" to "detergentExtradosage"
        return attr_name.rpartition('/')[-1] or attr_name

    def get_entity_type(self, attr_name: str):
        capability_def: dict[str, any] | None = self.capabilities.get(attr_name, None)
        if not capability_def:
            return None
        # Type : string, int, number, boolean (other values ignored)
        type = capability_def.get("type", None)
        if not type:
            return None
        # Access : read, readwrite (other values ignored)
        access = capability_def.get("access", None)
        if not access:
            return None

        # List of values ? if values is defined and has at least 1 entry
        values: dict[str, any] | None = capability_def.get("values", None)
        if values and access == "readwrite" and isinstance(values, dict) and len(values) > 0:
            return SELECT

        match type:
            case "boolean":
                if access == "read":
                    return BINARY_SENSOR
                if access == "readwrite":
                    return SWITCH
            case _:
                if access == "read" and type in ["number", "int", "boolean", "string"]:
                    return SENSOR
                if type == "int" or type == "number":
                    return NUMBER
        return None

    def sources_list(self):
        if self.capabilities is None:
            return None
        return [key for key in list(self.capabilities.keys()) if not key.startswith("applianceCareAndMaintenance")]


class Appliance:
    brand: str
    device: str
    entities: []
    coordinator: any

    def __init__(self, coordinator: any,
                 name: str, pnc_id: str, brand: str, model: str,
                 state: ApplienceStatusResponse) -> None:
        self.own_capabilties = False
        self.data = None
        self.coordinator = coordinator
        self.model = model
        self.pnc_id = pnc_id
        self.name = name
        self.brand = brand
        self.state = state

    def getItemFromCatalog(self, entity_name: str):
        for key, item in Catalog.items():
            if key == entity_name:
                return item
        return None

    def update_missing_entities(self):
        """Add missing entities when no capabilities returned by the API, do it dynamically"""
        if not self.own_capabilties:
            return
        properties = self.state.get("properties")
        capability = ""
        if properties:
            reported = properties.get("reported")
            if reported:
                for key, item in Catalog.items():
                    category = item[1]
                    if ((category and reported.get(category, None) and reported.get(category, None).get(key))
                            or (not category and reported.get(key, None))):
                        found: bool = False
                        for entity in self.entities:
                            if entity.entity_attr == key and entity.entity_source == category:
                                found = True
                                capability = key if category is None else category + "/" + key
                                self.data.capabilities[capability] = item[0]
                                break
                        if not found:
                            _LOGGER.debug("Electrolux discovered new entity from extracted data", category, key)
                            entity = self.get_entity(capability)
                            if entity:
                                self.entities.append(entity)

    def get_entity(self, capability: str) -> ElectroluxEntity | None:
        entity_type = self.data.get_entity_type(capability)
        entity_name = self.data.get_entity_name(capability)
        category = self.data.get_category(capability)
        capability_info: dict[str, any] = self.data.capabilities[capability]
        device_class = None
        entity_category = None
        unit = None
        # item : capability, category, DeviceClass, Unit, EntityCategory
        catalog_item = self.getItemFromCatalog(entity_name)
        if catalog_item:
            device_class = catalog_item[2] if 2 < len(catalog_item) else None
            unit = catalog_item[3] if 3 < len(catalog_item) else None
            entity_category = catalog_item[4] if 4 < len(catalog_item) else None

        if entity_type == SENSOR:
            return ElectroluxSensor(
                name=f"{self.data.get_name()} {self.data.get_sensor_name(entity_name, capability)}",
                coordinator=self.coordinator,
                config_entry=self.coordinator.config_entry,
                entity_type=entity_type,
                entity_attr=entity_name,
                entity_source=category,
                pnc_id=self.pnc_id,
                capability=capability_info,
                unit=unit,
                entity_category=entity_category,
                device_class=device_class
            )
        if entity_type == BINARY_SENSOR:
            return ElectroluxBinarySensor(
                name=f"{self.data.get_name()} {self.data.get_sensor_name(entity_name, capability)}",
                coordinator=self.coordinator,
                config_entry=self.coordinator.config_entry,
                entity_type=entity_type,
                entity_attr=entity_name,
                entity_source=category,
                pnc_id=self.pnc_id,
                capability=capability_info,
                unit=unit,
                entity_category=entity_category,
                device_class=device_class
            )
        if entity_type == SELECT:
            return ElectroluxSelect(
                name=f"{self.data.get_name()} {self.data.get_sensor_name(entity_name, capability)}",
                coordinator=self.coordinator,
                config_entry=self.coordinator.config_entry,
                entity_type=entity_type,
                entity_attr=entity_name,
                entity_source=category,
                pnc_id=self.pnc_id,
                capability=capability_info,
                unit=unit,
                entity_category=entity_category,
                device_class=device_class
            )
        if entity_type == NUMBER:
            return ElectroluxNumber(
                name=f"{self.data.get_name()} {self.data.get_sensor_name(entity_name, capability)}",
                coordinator=self.coordinator,
                config_entry=self.coordinator.config_entry,
                entity_type=entity_type,
                entity_attr=entity_name,
                entity_source=category,
                pnc_id=self.pnc_id,
                capability=capability_info,
                unit=unit,
                entity_category=entity_category,
                device_class=device_class
            )
        if entity_type == SWITCH:
            return ElectroluxSwitch(
                name=f"{self.data.get_name()} {self.data.get_sensor_name(entity_name, capability)}",
                coordinator=self.coordinator,
                config_entry=self.coordinator.config_entry,
                entity_type=entity_type,
                entity_attr=entity_name,
                entity_source=category,
                pnc_id=self.pnc_id,
                capability=capability_info,
                unit=unit,
                entity_category=entity_category,
                device_class=device_class
            )
        return None

    def setup(self, data: ElectroluxLibraryEntity):
        self.data = data
        self.entities = []
        entities = []
        # Extraction of the capabilities of the connected appliance and mapping to the known entities of the component
        capabilities_names = self.data.sources_list()  # [ "applianceState", "autoDosing",..., "userSelections/analogTemperature",...]

        # No capabilities returned (unstable API) => rebuild them from catalog + sample data
        if capabilities_names is None and self.state:
            capabilities_names = []
            capabilities = {}
            properties = self.state.get("properties")
            if properties:
                reported = properties.get("reported")
                if reported:
                    for key, item in Catalog.items():
                        category = item[1]
                        if ((category and reported.get(category, None) and reported.get(category, None).get(key))
                                or (not category and reported.get(key, None))
                                or key == "executeCommand"):
                            if category:
                                capabilities[category + "/" + key] = item[0]
                                capabilities_names.append(category + "/" + key)
                            else:
                                capabilities[key] = item[0]
                                capabilities_names.append(key)
                    self.data.capabilities = capabilities
                    _LOGGER.debug("Electrolux rebuilt capabilities due to API malfunction",
                                  json.dumps(capabilities, indent=2))

        # For each capability src
        for capability in capabilities_names:
            capability_info: dict[str, any] = data.capabilities[capability]
            entity_name = data.get_entity_name(capability)
            category = data.get_category(capability)
            device_class = None
            entity_category = None
            unit = None
            # item : capability, category, DeviceClass, Unit, EntityCategory
            catalog_item = self.getItemFromCatalog(entity_name)
            if catalog_item:
                device_class = catalog_item[2] if 2 < len(catalog_item) else None
                unit = catalog_item[3] if 3 < len(catalog_item) else None
                entity_category = catalog_item[4] if 4 < len(catalog_item) else None

            if capability == "executeCommand":
                commands: dict[str, str] = capability_info["values"]
                commands_keys = list(commands.keys())
                for command in commands_keys:
                    entities.append(
                        ElectroluxButtonEntity(
                            name=f"{data.get_name()} {data.get_sensor_name(entity_name, capability)}",
                            coordinator=self.coordinator,
                            config_entry=self.coordinator.config_entry,
                            entity_type=BUTTON,
                            entity_attr=entity_name,
                            entity_source=category,
                            pnc_id=self.pnc_id,
                            icon=icon_mapping.get(command, "mdi:gesture-tap-button"),
                            val_to_send=command,
                            capability=capability_info,
                            entity_category=entity_category,
                            device_class=device_class
                        )
                    )
            entity = self.get_entity(capability)
            if entity:
                entities.append(entity)

        # Setup each found entities
        self.entities = entities
        for entity in entities:
            entity.setup(data)

    def update(self, appliance_status: ApplienceStatusResponse):
        self.update_missing_entities()
        for entity in self.entities:
            entity.update(appliance_status)


class Appliances:
    def __init__(self, appliances: dict[str, Appliance]) -> None:
        self.appliances = appliances

    def get_appliance(self, pnc_id) -> Appliance:
        return self.appliances.get(pnc_id, None)

    def get_appliances(self) -> dict[str, Appliance]:
        return self.appliances
