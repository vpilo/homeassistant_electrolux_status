"""Number platform for Electrolux Status."""
from homeassistant.components.number import NumberEntity

from .entity import ElectroluxEntity
import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)

# async def async_setup_entry(hass, entry, async_add_devices):
#     """Setup binary sensor platform."""
#     coordinator = hass.data[DOMAIN][entry.entry_id]
#     appliances = coordinator.data.get('appliances', None)
#
#     if appliances is not None:
#         for appliance_id, appliance in appliances.appliances.items():
#             async_add_devices(
#                 [
#                     ElectroluxNumber(coordinator, entry, appliance_id, entity.entity_type, entity.attr, entity.source)
#                     for entity in appliance.entities if entity.entity_type == NUMBER
#                 ]
#             )


class ElectroluxNumber(ElectroluxEntity, NumberEntity):
    """Electrolux Status number class."""

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        return self._attr_native_value

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        _LOGGER.error("Not implemented")
