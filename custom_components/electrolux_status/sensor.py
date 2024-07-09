"""Switch platform for Electrolux Status."""

import contextlib
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime, UnitOfVolume
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
        if self.unit == UnitOfTemperature.FAHRENHEIT:
            return 2
        if self.unit == UnitOfVolume.LITERS:
            return 0
        if self.unit == UnitOfTime.SECONDS:
            return 0
        return None

    @property
    def native_value(self) -> str | int | float:
        """Return the state of the sensor."""
        value = self.extract_value()
        if value is not None and isinstance(self.unit, UnitOfTime):
            # Electrolux bug - prevent negative/disabled timers
            value = max(value, 0)
        if self.catalog_entry and self.catalog_entry.value_mapping:
            # Electrolux presents as string but returns an int
            mapping = self.catalog_entry.value_mapping
            if value in mapping:
                value = mapping.get(value, value)
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
        # store the value of the sensor in the native format
        return self.unit

    @property
    def suggested_unit_of_measurement(self) -> str | None:
        """Return suggested unit of measurement."""
        # change the display unit in the HA frontend
        if self.unit == UnitOfTime.SECONDS:
            return UnitOfTime.MINUTES
        with contextlib.suppress(ValueError):
            if self._is_valid_suggested_unit(self.unit):
                return self.unit
        return None

