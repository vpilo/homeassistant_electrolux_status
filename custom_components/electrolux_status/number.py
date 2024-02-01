"""Number platform for Electrolux Status."""
from homeassistant.components.number import NumberEntity

from .const import NUMBER, DOMAIN
from .entity import ElectroluxEntity
import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    appliances = coordinator.data.get('appliances', None)
    if appliances is not None:
        for appliance_id, appliance in appliances.appliances.items():
            entities = [entity for entity in appliance.entities if entity.entity_type == NUMBER]
            _LOGGER.debug("Electrolux add %d selects to registry for appliance %s", len(entities), appliance_id)
            async_add_entities(entities)


class ElectroluxNumber(ElectroluxEntity, NumberEntity):
    """Electrolux Status number class."""

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        return self.extract_value()
        #return self._attr_native_value

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        _LOGGER.error("Not implemented")

    @property
    def native_unit_of_measurement(self):
        return self.unit
