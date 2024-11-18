"""Camera platform for Electrolux Status."""

import logging
from typing import Any

import io
from PIL import Image, ImageDraw, ImageFont
from pyelectroluxocp import OneAppApi

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, IMAGE
from .entity import ElectroluxEntity
from .model import ElectroluxDevice

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Configure image platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    if appliances := coordinator.data.get("appliances", None):
        for appliance_id, appliance in appliances.appliances.items():
            entities = [
                entity for entity in appliance.entities if entity.entity_type == IMAGE
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
class ElectroluxCamera(ElectroluxEntity, ImageEntity):
    """Electrolux Status camera class."""

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
        """Initialize the Electrolux Camera."""
        super().__init__(
            coordinator=coordinator,
            capability=capability,
            name=name,
            config_entry=config_entry,
            pnc_id=pnc_id,
            entity_type=entity_type,
            entity_name=entity_name,
            entity_attr="snapshotDone",
            entity_source=entity_source,
            unit=None,
            device_class=device_class,
            entity_category=entity_category,
            icon=icon,
            catalog_entry=catalog_entry,
        )
        ImageEntity.__init__(self, coordinator.hass)
        self._client: OneAppApi = self.api
        self._last_snapshot: str = None
        self.content_type = "image/png"

    @property
    def entity_domain(self):
        """Entity domain for this entry. Used for consistent entity_id."""
        return IMAGE

    def update_last_snapshot(self):
        """Update last taken image name, and save state."""
        value = self.extract_value()

        _LOGGER.debug("VALERIO - New snapshot retrieved: %s", value)
        if value != self._last_snapshot:
            self._last_snapshot = value

    async def async_image(self) -> bytes | None:
        """Return a still image response from the camera."""

        width = 300
        height = 200
        _LOGGER.debug("VALERIO - async_camera_image(%s x %ss)", width, height)

        if self._attr_image_last_updated is None:
            self.update_last_snapshot()
            await self.send_command({"camera": {"snapshotTake": ""}})

        font = ImageFont.load_default()
        image = Image.new("RGB", (width, height), color=(0, 0, 0))
        buffer = io.BytesIO()

        text = "No image available yet"
        if self._last_snapshot is not None:
            text = self._last_snapshot
        brush = ImageDraw.Draw(image)
        brush.text((10, 10), text, font=font, fill=(255, 255, 255))
        image.save(buffer, format="PNG")

        return buffer.getvalue()

    async def async_turn_on(self) -> None:
        """Turn on the camera."""
        _LOGGER.debug("VALERIO - Requesting camera to turn on")
        await self.send_command({"camera": {"snapshotTake": ""}})

    async def send_command(self, command_json) -> bool:
        """Send a command to the device."""

        # Electrolux bug - needs string not bool
        # if "values" in self.capability:
        #    value = "ON" if value else "OFF"

        _LOGGER.debug("VALERIO send command %s", command_json)
        result = await self._client.execute_appliance_command(self.pnc_id, command_json)
        _LOGGER.debug("VALERIO send command result %s", result)
        return True
