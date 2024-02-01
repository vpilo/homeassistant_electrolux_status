from .entity import ElectroluxEntity

from homeassistant.components.sensor import SensorEntity


# async def async_setup_entry(hass, entry, async_add_devices):
#     """Setup sensor platform."""
#     coordinator: ElectroluxCoordinator = hass.data[DOMAIN][entry.entry_id]
#     appliances: Appliances = coordinator.data.get('appliances', None)
#
#     if appliances is not None:
#         for appliance_id, appliance in appliances.appliances.items():
#             async_add_devices(
#                 [
#                     ElectroluxSensor(coordinator, entry, appliance_id, entity.entity_type, entity.attr, entity.source)
#                     for entity in appliance.entities if entity.entity_type == SENSOR
#                 ]
#             )


class ElectroluxSensor(ElectroluxEntity, SensorEntity):
    """Electrolux Status Sensor class."""

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.get_value()

    # @property
    # def native_unit_of_measurement(self):
    #     return cast(ApplianceSensor, self.get_entity).unit
