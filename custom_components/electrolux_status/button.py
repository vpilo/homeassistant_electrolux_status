"""Button platform for Electrolux Status."""
from homeassistant.components.button import ButtonEntity

from .const import BUTTON, DOMAIN
from .entity import ElectroluxButtonEntity
import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    appliances = coordinator.data.get('appliances', None)
    if appliances is not None:
        for appliance_id, appliance in appliances.appliances.items():
            entities = [entity for entity in appliance.entities if entity.entity_type == BUTTON]
            _LOGGER.debug("Electrolux add %d buttons to registry for appliance %s", len(entities), appliance_id)
            async_add_entities(entities)


class ElectroluxButton(ElectroluxButtonEntity, ButtonEntity):
    """Electrolux Status button class."""

    async def async_press(self) -> None:
        _LOGGER.error("Not supported yet")
        # if self.entity_attr == "ExecuteCommand":
        #     await self.hass.async_add_executor_job(self.coordinator.api.setHacl, self.get_appliance.pnc_id, "0x0403", self.val_to_send, self.entity_source)
