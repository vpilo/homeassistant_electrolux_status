"""Switch platform for Electrolux Status."""

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SENSOR
from .entity import ElectroluxEntity

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configure sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    if appliances := coordinator.data.get("appliances", None):
        for appliance_id, appliance in appliances.appliances.items():
            entities = [
                entity for entity in appliance.entities if entity.entity_type == SENSOR
            ]
            _LOGGER.debug(
                "Electrolux add %d SENSOR entities to registry for appliance %s",
                len(entities),
                appliance_id,
            )
            async_add_entities(entities)


class ElectroluxSensor(ElectroluxEntity, SensorEntity):
    """Electrolux Status Sensor class."""

    @property
    def suggested_display_precision(self) -> int | None:
        """Get the display precision."""
        if self.unit == UnitOfTemperature.CELSIUS:
            return 2
        if self.unit == UnitOfTime.SECONDS:
            return 0
        return None

    @property
    def native_value(self) -> str | int | float:
        """Return the state of the sensor."""
        value = self.extract_value()
        if value is not None and self.unit == UnitOfTime.SECONDS:
            value = time_seconds_to_minutes(value)
            if value is not None and value < 0:
                value = 0
        if isinstance(value, str):
            if "_" in value:
                value = value.replace("_", " ")
            value = value.title()
        if value is not None:
            self._cached_value = value
        else:
            value = self._cached_value
        return value

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return unit of measurement."""
        if self.unit == UnitOfTime.SECONDS:
            return UnitOfTime.MINUTES
        return self.unit
