from homeassistant.const import UnitOfTime

from .entity import ElectroluxEntity, time_seconds_to_minutes

from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, SENSOR
import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    appliances = coordinator.data.get('appliances', None)
    if appliances is not None:
        for appliance_id, appliance in appliances.appliances.items():
            entities = [entity for entity in appliance.entities if entity.entity_type == SENSOR]
            _LOGGER.debug("Electrolux add %d sensors to registry for appliance %s", len(entities), appliance_id)
            async_add_entities(entities)


class ElectroluxSensor(ElectroluxEntity, SensorEntity):
    """Electrolux Status Sensor class."""

    @property
    def native_value(self):
        """Return the state of the sensor."""
        value = self.extract_value()
        if value is not None and self.unit == UnitOfTime.SECONDS:
            return time_seconds_to_minutes(value)
        if isinstance(value, str) and "_" in value:
            value = value.replace("_", " ").title()
        return value

    @property
    def native_unit_of_measurement(self):
        if self.unit == UnitOfTime.SECONDS:
            return UnitOfTime.MINUTES
        return self.unit
