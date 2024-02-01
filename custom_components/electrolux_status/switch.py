"""Switch platform for Electrolux Status."""
from homeassistant.components.switch import SwitchEntity

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
#                     ElectroluxSwitch(coordinator, entry, appliance_id, entity.entity_type, entity.attr, entity.source)
#                     for entity in appliance.entities if entity.entity_type == SWITCH
#                 ]
#             )


class ElectroluxSwitch(ElectroluxEntity, SwitchEntity):
    """Electrolux Status switch class."""

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.get_value()

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        _LOGGER.error("Not supported yet")

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        _LOGGER.error("Not supported yet")