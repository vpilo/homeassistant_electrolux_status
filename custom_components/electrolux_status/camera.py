"""Camera platform for Electrolux Status."""

import logging
from typing import Any

from pyelectroluxocp import OneAppApi

from homeassistant.components.camera import Camera as CameraEntity, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CAMERA, DOMAIN
from .entity import ElectroluxEntity
from .model import ElectroluxDevice

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configure camera platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    if appliances := coordinator.data.get("appliances", None):
        for appliance_id, appliance in appliances.appliances.items():
            entities = [
                entity for entity in appliance.entities if entity.entity_type == CAMERA
            ]
            _LOGGER.debug(
                "Electrolux add %d CAMERA entities to registry for appliance %s",
                len(entities),
                appliance_id,
            )
            async_add_entities(entities)


# https://developers.home-assistant.io/docs/core/entity/camera/
# tip Properties should always only return information from memory
# and not do I/O (like network requests). Implement update() or
# async_update() to fetch data.
class ElectroluxCamera(ElectroluxEntity, CameraEntity):
    """Electrolux Status camera class."""

    _attr_supported_features = CameraEntityFeature.ON_OFF

    def __init__(
        self,
        coordinator: Any,
        name: str,
        config_entry,
        pnc_id: str,
        entity_type: Platform,
        entity_name,
        entity_attr,
        entity_source,
        capability: dict[str, Any],
        unit: str,
        device_class: str,
        entity_category: EntityCategory,
        icon: str,
        catalog_entry: ElectroluxDevice | None = None,
    ) -> None:
        """Initaliaze the Electrolux Camera."""
        super().__init__(
            coordinator=coordinator,
            capability=capability,
            name=name,
            config_entry=config_entry,
            pnc_id=pnc_id,
            entity_type=entity_type,
            entity_name=entity_name,
            entity_attr=entity_attr,
            entity_source=entity_source,
            unit=None,
            device_class=device_class,
            entity_category=entity_category,
            icon=icon,
            catalog_entry=catalog_entry,
        )
        CameraEntity.__init__(self)

    @property
    def entity_domain(self):
        """Entity domain for this entry. Used for consistent entity_id."""
        _LOGGER.debug(
            "VALERIO - Camera entity_domain, entity source=%s entry=%s",
            self.entity_source,
            self.config_entry,
        )
        return CAMERA

    @property
    def is_on(self) -> bool:
        """Return true if the camera is on."""
        _LOGGER.debug(
            "VALERIO - Camera is_on, entity source=%s entry=%s",
            self.entity_source,
            self.config_entry,
        )
        value = False

        # if value is None:
        #     if self.catalog_entry and self.catalog_entry.state_mapping:
        #         mapping = self.catalog_entry.state_mapping
        #         value = self.get_state_attr(mapping)
        # # Electrolux returns strings for some true/false states
        # if value is not None and isinstance(value, str):
        #     value = string_to_boolean(value, False)

        # if value is None:
        #     return self._cached_value
        # self._cached_value = value
        return value

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image response from the camera."""

        # TODO
        _LOGGER.debug("VALERIO - async_camera_image(%dx%d)", width, height)
        return None

    @property
    def is_recording(self) -> bool:
        """Return true if the device is recording."""

        _LOGGER.debug(
            "VALERIO - Camera is_recording, entity source=%s entry=%s",
            self.entity_source,
            self.config_entry,
        )
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        _LOGGER.debug("VALERIO - Camera turn_on req")
        await self.switch(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        _LOGGER.debug("VALERIO - Camera turn_off req")
        await self.switch(False)

    def appliance_state_update_callback(update_json):
        _LOGGER.debug("VALERIO appliance state updated", update_json)
        # json_object = json.dumps(update_json, indent=4)
        # now = str(datetime.now()).replace(" ", "_")
        # dump(f"samples/update_{now}.json", json_object)

    async def send_command(self) -> bool:
        """Send a command to the device."""
        client: OneAppApi = self.api

        # Electrolux bug - needs string not bool
        # if "values" in self.capability:
        #    value = "ON" if value else "OFF"

        # if self.entity_source:
        #     command = {self.entity_source: {self.entity_attr: value}}
        # else:
        #     command = {self.entity_attr: value}
        # client.wat
        # _LOGGER.debug("Electrolux send command %s", command)
        # result = await client.execute_appliance_command(self.pnc_id, "snapshotTake")
        # _LOGGER.debug("Electrolux send command result %s", result)
        _LOGGER.debug("send command")
        return True
