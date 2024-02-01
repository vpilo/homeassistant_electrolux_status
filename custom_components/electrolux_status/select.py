"""Select platform for Electrolux Status."""
from homeassistant.components.select import SelectEntity

from .entity import ElectroluxEntity


# async def async_setup_entry(hass, entry, async_add_devices):
#     """Setup select platform."""
#     coordinator = hass.data[DOMAIN][entry.entry_id]
#     appliances = coordinator.data.get('appliances', None)
#
#     if appliances is not None:
#         for appliance_id, appliance in appliances.appliances.items():
#             async_add_devices(
#                 [
#                     ElectroluxSelect(coordinator, entry, appliance_id, entity.entity_type, entity.attr, entity.source)
#                     for entity in appliance.entities if entity.entity_type == SELECT
#                 ]
#             )


class ElectroluxSelect(ElectroluxEntity, SelectEntity):
    """Electrolux Status binary_sensor class."""

    # @property
    # def icon(self) -> str:
    #     """Return a representative icon."""
    #     if not self.available or self.current_option == "TODO":
    #         return "mdi:XXX"
    #     return "mdi:YYY"

    @property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        if self.capability is None:
            return []
        values_dict: dict[str, any] | None = self.capability.get("values", None)
        if values_dict is None:
            return []
        return list(values_dict.keys())

        # return [TRANSLATABLE_POWER_OFF] + sorted(self._data.activity_names)
