from homeassistant.components.sensor import ENTITY_ID_FORMAT
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pyelectroluxocp.apiModels import ApplienceStatusResponse

# from .api import Appliance, ElectroluxLibraryEntity

from .const import DOMAIN
import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup binary sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    appliances = coordinator.data.get('appliances', None)
    if appliances is not None:
        for appliance_id, appliance in appliances.appliances.items():
            entities = [entity for entity in appliance.entities if entity.entity_type == "entity"]
            _LOGGER.debug("Electrolux add %d entities to registry for appliance %s", len(entities), appliance_id)
            async_add_entities(entities)


class ElectroluxEntity(CoordinatorEntity):
    appliance_status: ApplienceStatusResponse

    def __init__(self, coordinator: any, name: str, config_entry,
                 pnc_id: str, entity_type: str, entity_attr, entity_source, capability: dict[str, any], unit):
        super().__init__(coordinator)
        self.data = None
        self.coordinator = coordinator
        self._name = name
        self.api = coordinator.api
        self.entity_attr = entity_attr
        self.entity_type = entity_type
        self.entity_source = entity_source
        self.config_entry = config_entry
        self.pnc_id = pnc_id
        self.unit = unit
        _LOGGER.debug("Electrolux new entity %s for appliance %s", name, pnc_id)
        self.entity_id = ENTITY_ID_FORMAT.format(
            f"{self.get_appliance.brand}_{self.get_appliance.name}_{self.entity_source}_{self.entity_attr}")
        self.capability = capability

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    # @property
    # def get_entity(self) -> ApplianceEntity:
    #     return self.get_appliance.get_entity(self.entity_type, self.entity_attr, self.entity_source, None)

    @property
    def get_appliance(self):
        return self.coordinator.data['appliances'].get_appliance(self.pnc_id)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.entity_attr}-{self.entity_source}-{self.pnc_id}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.get_appliance.name)},
            "name": self.get_appliance.name,
            "model": self.get_appliance.model,
            "manufacturer": self.get_appliance.brand,
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "integration": DOMAIN,
        }

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return None
        # return self.get_entity.device_class

    def extract_value(self):
        """Return the appliance attributes of the entity."""
        if self.appliance_status:
            properties = self.appliance_status.get("properties", None)
            if properties:
                reported = properties.get("reported", None)
                if reported:
                    if self.entity_source:
                        category: dict[str, any] | None = reported.get(self.entity_source, None)
                        if category:
                            return category.get(self.entity_attr)
                    else:
                        return reported.get(self.entity_attr, None)
        return None

    def setup(self, data):
        self.data = data

    def update(self, appliance_status: ApplienceStatusResponse):
        self.appliance_status = appliance_status


class ElectroluxButtonEntity(ElectroluxEntity):
    def __init__(self, coordinator: any, name: str, config_entry,
                 pnc_id: str, entity_type: str, entity_attr, entity_source, capability: dict[str, any],
                 val_to_send, icon):
        super().__init__(coordinator=coordinator, capability=capability, name=name, config_entry=config_entry,
                         pnc_id=pnc_id, entity_type=entity_type, entity_attr=entity_attr, entity_source=entity_source, unit=None)
        self.val_to_send = val_to_send
        self.button_icon = icon
        self.entity_id = ENTITY_ID_FORMAT.format(
            f"{self.get_appliance.brand}_{self.get_appliance.name}_{self.entity_source}_{self.entity_attr}_{self.val_to_send}")

    @property
    def get_appliance(self):
        return self.coordinator.data['appliances'].get_appliance(self.pnc_id)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self.config_entry.entry_id}-{self.val_to_send}-{self.entity_attr}-{self.entity_source}-{self.pnc_id}"

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "integration": DOMAIN,
        }

    @property
    def icon(self):
        """Return the icon of the button."""
        return self.button_icon

    @property
    def available(self):
        # available state should depends on connect state
        return True
