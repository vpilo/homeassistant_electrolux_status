"""Number platform for Electrolux Status."""
from homeassistant.components.number import NumberEntity
from homeassistant.const import UnitOfTime

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
        if self.unit == UnitOfTime.SECONDS:
            return self.extract_value()/60
        return self.extract_value()

    @property
    def native_max_value(self) -> float | None:
        """Return the max value."""
        if self.unit == UnitOfTime.SECONDS:
            return self.capability.get("max", 100)/60
        return self.capability.get("max", 100)

    @property
    def native_min_value(self) -> float | None:
        """Return the max value."""
        if self.unit == UnitOfTime.SECONDS:
            return self.capability.get("min", 0)/60
        return self.capability.get("min", 0)

    @property
    def native_step_value(self) -> float | None:
        """Return the max value."""
        if self.unit == UnitOfTime.SECONDS:
            return self.capability.get("step", 1)/60
        return self.capability.get("step", 1)

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        _LOGGER.error("Not implemented")

    @property
    def native_unit_of_measurement(self):
        if self.unit == UnitOfTime.SECONDS:
            return UnitOfTime.MINUTES
        return self.unit
