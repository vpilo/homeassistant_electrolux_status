import json
import logging
import re

from pyelectroluxocp.apiModels import ApplianceInfoResponse, ApplienceStatusResponse

from .binary_sensor import ElectroluxBinarySensor
from .const import BINARY_SENSOR, SENSOR, BUTTON, icon_mapping, SELECT, SWITCH, NUMBER, Catalog
from .entity import ElectroluxButtonEntity
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
        # if attr_name in ["TargetMicrowavePower"]:
        #     return self.fix_microwave_power(attr_name, field, source)
        # if attr_name in ["LinkQualityIndicator"]:
        #     return self.num_to_dbm(attr_name, field, source)
        # if attr_name in ['StartTime', 'TimeToEnd', 'RunningTime', 'DryingTime', 'ApplianceTotalWorkingTime',
        #                  "FCTotalWashingTime"]:
        #     return self.time_to_end_in_minutes(attr_name, field, source)
        # if attr_name in self.status:
        #     return self.status.get(attr_name)
        # if attr_name in [self.state[k].get("name") for k in self.state]:
        #     val = self.get_from_states(attr_name, field, source)
        #     if field == "container":
        #         if val["1"]["name"] == "Coefficient" and val["3"]["name"] == "Exponent":
        #             return val["1"]["numberValue"] * (10 ** val["3"]["numberValue"])
        #     else:
        #         return val
        # if attr_name in [self.state[st]["container"][cr].get("name") for st in self.state for cr in
        #                  self.state[st].get("container", [])]:
        #     return self.get_from_states(attr_name, field, source)
        # return None

    # def time_to_end_in_minutes(self, attr_name, field, source):
    #     seconds = self.get_from_states(attr_name, field, source)
    #     if seconds is not None:
    #         if seconds == -1:
    #             return -1
    #         return int(math.ceil((int(seconds) / 60)))
    #     return None
    #
    # def fix_microwave_power(self, attr_name, field, source):
    #     microwave_power = self.get_from_states(attr_name, field, source)
    #     if microwave_power is not None:
    #         if microwave_power == 65535:
    #             return 0
    #         return microwave_power
    #     return None
    #
    # def num_to_dbm(self, attr_name, field, source):
    #     number_from_0_to_5 = self.get_from_states(attr_name, field, source)
    #     if number_from_0_to_5 is not None:
    #         if int(number_from_0_to_5) == 0:
    #             return -110
    #         if int(number_from_0_to_5) == 1:
    #             return -80
    #         if int(number_from_0_to_5) == 2:
    #             return -70
    #         if int(number_from_0_to_5) == 3:
    #             return -60
    #         if int(number_from_0_to_5) == 4:
    #             return -55
    #         if int(number_from_0_to_5) == 5:
    #             return -20
    #     return None

    # def get_from_states(self, attr_name, field, source):
    #     for k in self.state:
    #         if attr_name == self.state[k].get("name") and source == self.state[k].get("source"):
    #             return self._get_states(self.state[k], field) if field else self._get_states(self.state[k])
    #         attr_val = None
    #         for c in self.state[k].get("container", []):
    #             if attr_name == self.state[k]["container"][c].get("name"):
    #                 attr_val = self._get_states(self.state[k]["container"][c], field) if field else self._get_states(
    #                     self.state[k]["container"][c])
    #         if attr_val is not None:
    #             return attr_val
    #     return None

    # @staticmethod
    # def _get_states(states, field=None):
    #     if field:
    #         if field in states.keys():
    #             return states.get(field)
    #         if field == "string":
    #             if "valueTransl" in states.keys():
    #                 return states.get("valueTransl").strip(" :.")
    #             if "valTransl" in states.keys():
    #                 return states.get("valTransl").strip(" :.")
    #             if "stringValue" in states.keys():
    #                 return states.get("stringValue").strip(" :.")
    #             return ""
    #     else:
    #         if "valueTransl" in states.keys():
    #             return states.get("valueTransl").strip(" :.")
    #         if "valTransl" in states.keys():
    #             return states.get("valTransl").strip(" :.")
    #         if "stringValue" in states.keys():
    #             return states.get("stringValue").strip(" :.")
    #         if "numberValue" in states.keys():
    #             return states.get("numberValue")

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
        if access == "readwrite" and isinstance(values, dict) and len(values) > 0:
            return SELECT

        match type:
            case "boolean":
                if access == "read":
                    return BINARY_SENSOR
                if access == "readwrite":
                    return SWITCH
            case _:
                if access == "read":
                    return SENSOR
                if type == "int" or type == "number":
                    return NUMBER
        return None

    # def value_exists(self, attr_name, source):
    #     _container_attr = []
    #     for k in self.state:
    #         for c in self.state[k].get("container", []):
    #             _container_attr.append(self.state[k]["container"][c].get("name"))
    #     return (attr_name in self.status) or \
    #         (attr_name in [self.state[k].get("name") for k in self.state if
    #                        self.state[k].get("source") == source]) or \
    #         (attr_name in [self.profile[k].get("name") for k in self.profile if
    #                        self.profile[k].get("source") == source]) or \
    #         (attr_name in _container_attr)

    def sources_list(self):
        if self.capabilities is None:
            return None
        return [key for key in list(self.capabilities.keys()) if not key.startswith("applianceCareAndMaintenance")]
        # return list(
        #     {self.state[k].get("source") for k in self.state if self.state[k].get("source") not in ["NIU", "APL"]}
        # )

    # def commands_list(self, source):
    #     commands = list(self.profile[k].get("steps") for k in self.profile if
    #                     self.profile[k].get("source") == source and self.profile[k].get("name") == "ExecuteCommand")
    #     if len(commands) > 0:
    #         return commands[0]
    #     else:
    #         return {}

    # def get_command_name(self, command_desc):
    #     if "transl" in command_desc:
    #         return command_desc["transl"]
    #     elif "key" in command_desc:
    #         return command_desc["key"]
    #     return None


# class ApplianceEntity:
#     entity_type = None
#
#     def __init__(self, name, attr, device_class=None, entity_category=None, source=None) -> None:
#         self.attr = attr
#         self.name = name
#         self.device_class = device_class
#         self.entity_category = entity_category
#         self.source = source
#         self.val_to_send = None
#         self.icon = None
#         self._state = None
#
#     def setup(self, data: ElectroluxLibraryEntity):
#         self._state = data.get_value(self.attr, self.source)
#         return self
#
#     def update(self, data: ElectroluxLibraryEntity):
#         self._state = data.get_value(self.attr, self.source)
#         return self
#
#     def clear_state(self):
#         self._state = None
#
#
# class ApplianceSensor(ApplianceEntity):
#     entity_type = SENSOR
#
#     def __init__(self, name, attr, unit=None, device_class=None, entity_category=None, source=None) -> None:
#         super().__init__(name, attr, device_class, entity_category, source)
#         self.unit = unit
#
#     @property
#     def state(self):
#         return self._state
#
#
# class ApplianceBinary(ApplianceEntity):
#     entity_type = BINARY_SENSOR
#
#     def __init__(self, name, attr, device_class=None, entity_category=None, invert=False,
#                  source=None) -> None:
#         super().__init__(name, attr, device_class, entity_category, source)
#         self.invert = invert
#
#     @property
#     def state(self):
#         state = self._state in [1, 'enabled', True, 'Connected', 'connect']
#         return not state if self.invert else state
#
#
# class ApplianceButton(ApplianceEntity):
#     entity_type = BUTTON
#
#     def __init__(self, name, attr, unit=None, device_class=None, entity_category=None, source=None, val_to_send=None,
#                  icon=None) -> None:
#         super().__init__(name, attr, device_class, entity_category, source)
#         self.val_to_send = val_to_send
#         self.icon = icon
#
#     def setup(self, data: ElectroluxLibraryEntity):
#         return self


class Appliance:
    brand: str
    device: str
    entities: []
    coordinator: any

    def __init__(self, coordinator: any,
                 name: str, pnc_id: str, brand: str, model: str,
                 state: ApplienceStatusResponse) -> None:
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

    # def get_entity(self, entity_type, entity_attr, entity_source, val_to_send):
    #     return next(
    #         entity
    #         for entity in self.entities
    #         if
    #         entity.attr == entity_attr and entity.entity_type == entity_type and entity.source == entity_source and entity.val_to_send == val_to_send
    #     )

    def setup(self, data: ElectroluxLibraryEntity):
        # TODO
        # entities = [
        #     ApplianceBinary(
        #         name=data.get_name(),
        #         attr='status',
        #         device_class=BinarySensorDeviceClass.CONNECTIVITY,
        #         entity_category=EntityCategory.DIAGNOSTIC,
        #         source='APL',
        #     ),
        #     ApplianceSensor(
        #         name=f"{data.get_name()} SSID",
        #         attr='Ssid',
        #         entity_category=EntityCategory.DIAGNOSTIC,
        #         source='NIU',
        #     ),
        #     ApplianceSensor(
        #         name=f"{data.get_name()} {data.get_sensor_name('LinkQualityIndicator', 'NIU')}",
        #         attr='LinkQualityIndicator',
        #         field='numberValue',
        #         device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        #         unit="dBm",
        #         entity_category=EntityCategory.DIAGNOSTIC,
        #         source='NIU',
        #     ),
        # ]
        self.entities = []
        entities = []
        # Extraction of the capabilities of the connected appliance and mapping to the known entities of the component
        capabilities_names = data.sources_list()  # [ "applianceState", "autoDosing",..., "userSelections/analogTemperature",...]

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
                                or (not category and reported.get(key, None))):

                            if category:
                                capabilities[category+"/"+key] = item[0]
                                capabilities_names.append(category+"/"+key)
                            else:
                                capabilities[key] = item[0]
                                capabilities_names.append(key)
                    data.capabilities = capabilities
                    _LOGGER.debug("Electrolux rebuilt capabilities due to API malfunction", json.dumps(capabilities, indent=2))

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
                entity_category = catalog_item[3] if 3 < len(catalog_item) else None
                unit = catalog_item[4] if 4 < len(catalog_item) else None


            # found = False
            # # For each sensor in the const definition
            # for sensor_type, sensors_list in sensors.items():
            #     for sensorName, params in sensors_list.items():
            #         # Check if the sensor exists in the capabilities
            #         if sensorName == entity_name:
            #             found = True
            #             entities.append(
            #                 ElectroluxSensor(
            #                     name=f"{data.get_name()} {data.get_sensor_name(entity_name, capability)}",
            #                     coordinator=self.coordinator,
            #                     config_entry=self.coordinator.config_entry,
            #                     entity_type=SENSOR,
            #                     entity_attr=entity_name,
            #                     entity_source=category,
            #                     pnc_id=self.pnc_id,
            #                     capability=capability_info
            #                 )
            #             )
            # for sensor_type, sensors_list in sensors_binary.items():
            #     for sensorName, params in sensors_list.items():
            #         if sensorName == entity_name:
            #             found = True
            #             entities.append(
            #                 ElectroluxBinarySensor(
            #                     name=f"{data.get_name()} {data.get_sensor_name(entity_name, capability)}",
            #                     coordinator=self.coordinator,
            #                     config_entry=self.coordinator.config_entry,
            #                     entity_type=SENSOR,
            #                     entity_attr=entity_name,
            #                     entity_source=category,
            #                     pnc_id=self.pnc_id,
            #                     capability=capability_info
            #                 )
            #             )
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
                            capability=capability_info
                        )
                    )
            # Capability is not defined in the catalog, add it dynamically
            entity_type = data.get_entity_type(capability)
            if entity_type == SENSOR:
                entities.append(
                    ElectroluxSensor(
                        name=f"{data.get_name()} {data.get_sensor_name(entity_name, capability)}",
                        coordinator=self.coordinator,
                        config_entry=self.coordinator.config_entry,
                        entity_type=entity_type,
                        entity_attr=entity_name,
                        entity_source=category,
                        pnc_id=self.pnc_id,
                        capability=capability_info,
                        unit=unit
                    )
                )
            if entity_type == BINARY_SENSOR:
                entities.append(
                    ElectroluxBinarySensor(
                        name=f"{data.get_name()} {data.get_sensor_name(entity_name, capability)}",
                        coordinator=self.coordinator,
                        config_entry=self.coordinator.config_entry,
                        entity_type=entity_type,
                        entity_attr=entity_name,
                        entity_source=category,
                        pnc_id=self.pnc_id,
                        capability=capability_info,
                        unit=unit
                    )
                )
            if entity_type == SELECT:
                entities.append(
                    ElectroluxSelect(
                        name=f"{data.get_name()} {data.get_sensor_name(entity_name, capability)}",
                        coordinator=self.coordinator,
                        config_entry=self.coordinator.config_entry,
                        entity_type=entity_type,
                        entity_attr=entity_name,
                        entity_source=category,
                        pnc_id=self.pnc_id,
                        capability=capability_info,
                        unit=unit
                    )
                )
            if entity_type == NUMBER:
                entities.append(
                    ElectroluxNumber(
                        name=f"{data.get_name()} {data.get_sensor_name(entity_name, capability)}",
                        coordinator=self.coordinator,
                        config_entry=self.coordinator.config_entry,
                        entity_type=entity_type,
                        entity_attr=entity_name,
                        entity_source=category,
                        pnc_id=self.pnc_id,
                        capability=capability_info,
                        unit=unit
                    )
                )
            if entity_type == SWITCH:
                entities.append(
                    ElectroluxSwitch(
                        name=f"{data.get_name()} {data.get_sensor_name(entity_name, capability)}",
                        coordinator=self.coordinator,
                        config_entry=self.coordinator.config_entry,
                        entity_type=entity_type,
                        entity_attr=entity_name,
                        entity_source=category,
                        pnc_id=self.pnc_id,
                        capability=capability_info,
                        unit=unit
                    )
                )

        # for capability in capabilities:
        #     entity_name = data.get_entity_name(capability)
        #     category = data.get_category(capability)
        #
        #     found = False
        #     # For each sensor in the const definition
        #     for sensor_type, sensors_list in sensors.items():
        #         for sensorName, params in sensors_list.items():
        #             # Check if the sensor exists in the capabilities
        #             if sensorName == entity_name:
        #                 found = True
        #                 entities.append(
        #                     ApplianceSensor(
        #                         name=f"{data.get_name()} {data.get_sensor_name(sensorName, capability)}",
        #                         attr=entity_name,
        #                         device_class=params[1],
        #                         entity_category=sensor_type,
        #                         unit=params[2],
        #                         source=category,
        #                     )
        #                 )
        #     for sensor_type, sensors_list in sensors_binary.items():
        #         for sensorName, params in sensors_list.items():
        #             if sensorName == entity_name:
        #                 found = True
        #                 entities.append(
        #                     ApplianceBinary(
        #                         name=f"{data.get_name()} {data.get_sensor_name(sensorName, capability)}",
        #                         attr=entity_name,
        #                         device_class=params[1],
        #                         entity_category=sensor_type,
        #                         invert=params[2],
        #                         source=category,
        #                     )
        #                 )
        #     if capability == "executeCommand":
        #         commands: dict[str, str] = data.capabilities[capability]["values"]
        #         commands_keys = list(commands.keys())
        #         found = True
        #         for command in commands_keys:
        #             entities.append(
        #                 ApplianceButton(
        #                     name=f"{data.get_name()} {command}",
        #                     attr='ExecuteCommand',
        #                     val_to_send=command,
        #                     source=category,
        #                     icon=icon_mapping.get(command, "mdi:gesture-tap-button"),
        #                 )
        #             )
        #     # Capability is not defined in the catalog, add it dynamically
        #     if not found:
        #         entity_type = data.get_entity_type(capability)
        #         if entity_type == SENSOR:
        #             entities.append(
        #                 ApplianceSensor(
        #                     name=f"{data.get_name()} {data.get_sensor_name(entity_name, capability)}",
        #                     attr=entity_name,
        #                     entity_category=None,
        #                     source=category,
        #                 )
        #             )
        #         if entity_type == BINARY_SENSOR:
        #             entities.append(
        #                 ApplianceBinary(
        #                     name=f"{data.get_name()} {data.get_sensor_name(entity_name, capability)}",
        #                     attr=entity_name,
        #                     entity_category=None,
        #                     source=category,
        #                 )
        #             )
        #         if entity_type == SELECT:
        #             entities.append(
        #                 ApplianceEntity(
        #                     name=f"{data.get_name()} {data.get_sensor_name(entity_name, capability)}",
        #                     attr=entity_name,
        #                     entity_category=None,
        #                     source=category,
        #                 )
        #             )
        #         if entity_type == NUMBER:
        #             entities.append(
        #                 ApplianceEntity(
        #                     name=f"{data.get_name()} {data.get_sensor_name(entity_name, capability)}",
        #                     attr=entity_name,
        #                     entity_category=None,
        #                     source=category,
        #                 )
        #             )
        #         if entity_type == SWITCH:
        #             entities.append(
        #                 ApplianceEntity(
        #                     name=f"{data.get_name()} {data.get_sensor_name(entity_name, capability)}",
        #                     attr=entity_name,
        #                     entity_category=None,
        #                     source=category,
        #                 )
        #             )

        # Setup each found entities
        self.entities = entities
        for entity in entities:
            entity.setup(data)


    def update(self, appliance_status: ApplienceStatusResponse):
        for entity in self.entities:
            entity.update(appliance_status)


class Appliances:
    def __init__(self, appliances: dict[str, Appliance]) -> None:
        self.appliances = appliances

    def get_appliance(self, pnc_id) -> Appliance:
        return self.appliances.get(pnc_id, None)

    def get_appliances(self) -> dict[str, Appliance]:
        return self.appliances
