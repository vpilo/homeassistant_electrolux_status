"""Select platform for Electrolux Status."""
from homeassistant.components.select import SelectEntity

from .const import SELECT, DOMAIN
from .entity import ElectroluxEntity

import logging

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    appliances = coordinator.data.get('appliances', None)
    if appliances is not None:
        for appliance_id, appliance in appliances.appliances.items():
            entities = [entity for entity in appliance.entities if entity.entity_type == SELECT]
            _LOGGER.debug("Electrolux add %d selects to registry for appliance %s", len(entities), appliance_id)
            async_add_entities(entities)


class ElectroluxSelect(ElectroluxEntity, SelectEntity):
    """Electrolux Status binary_sensor class."""

    # @property
    # def icon(self) -> str:
    #     """Return a representative icon."""
    #     if not self.available or self.current_option == "TODO":
    #         return "mdi:XXX"
    #     return "mdi:YYY"

    @property
    def current_option(self) -> str:
        return self.extract_value()

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        _LOGGER.warning("Electrolux not supported yet")

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
