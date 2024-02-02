"""electrolux status integration."""
import json

from pyelectroluxocp import OneAppApi

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed
from pyelectroluxocp.apiModels import ApplienceStatusResponse

from .pyelectroluxconnect_util import pyelectroluxconnect_util
from .api import Appliance, Appliances, ElectroluxLibraryEntity
from .const import CONF_PASSWORD, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .const import CONF_LANGUAGE, DEFAULT_LANGUAGE
from .const import CONF_USERNAME
from .const import DOMAIN
from .const import PLATFORMS
from .const import languages

_LOGGER: logging.Logger = logging.getLogger(__package__)


# noinspection PyUnusedLocal
async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    if entry.options.get(CONF_SCAN_INTERVAL):
        update_interval = timedelta(seconds=entry.options[CONF_SCAN_INTERVAL])
    else:
        update_interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    language = languages.get(entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE), "eng")

    client = pyelectroluxconnect_util.get_session(username, password, language)

    coordinator = ElectroluxCoordinator(hass, client=client, update_interval=update_interval)
    if not await coordinator.async_login():
        raise ConfigEntryAuthFailed

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Initialize entities
    await coordinator.setup_entities()

    # Fill in the values for first time
    await coordinator.async_config_entry_first_refresh()

    # Add entities in registry
    # for applianceId in appliances:
    #     appliance = appliances[applianceId]
    #     for entity in appliance.entities:
    #         _LOGGER.debug("Electrolux add entity to registry %s", entity.name)
    #         async_add_entities(entity)

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    coordinator.platforms.extend(PLATFORMS)
    # Call async_setup_entry in entity files
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.add_update_listener(async_reload_entry)
    return True


class ElectroluxCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""
    api: OneAppApi = None

    def __init__(self, hass: HomeAssistant, client: OneAppApi, update_interval: timedelta) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def async_login(self) -> bool:
        try:
            # Check that one can extract the appliance list to confirm login
            await self.hass.async_add_executor_job(self.api.get_appliances_list)
        except Exception as ex:
            _LOGGER.error("Could not log in to ElectroluxStatus, %s", ex)
            return False
        return True

    async def setup_entities(self):
        await self.async_login()
        appliances = Appliances({})
        self.data = {
            "appliances": appliances
        }
        try:
            appliances_json: list[ApplienceStatusResponse] = await self.api.get_appliances_list()
            _LOGGER.debug("Electrolux update appliances %s", json.dumps(appliances_json))
            for appliance_json in appliances_json:
                appliance_id = appliance_json.get('applianceId')
                connection_status = appliance_json.get('connectionState')
                # appliance_profile = await self.hass.async_add_executor_job(self.api.getApplianceProfile, appliance)
                appliance_name = appliance_json.get('applianceData').get('applianceName')
                appliance_infos = await self.api.get_appliances_info([appliance_id])
                appliance_state = None
                try:
                    appliance_capabilities = await self.api.get_appliance_capabilities(appliance_id)
                    _LOGGER.debug("Electrolux appliance capabilities %s", json.dumps(appliance_capabilities))
                except Exception as exception:
                    #_LOGGER.exception(exception)
                    _LOGGER.warning("Electrolux unable to retrieve capabilities, we are going on our own")
                    appliance_capabilities = None
                    # Extract appliance state if no capabilities returned
                    appliance_state = await self.api.get_appliance_status(appliance_id)
                    _LOGGER.debug("Electrolux get_appliance_status result", appliance_state)

                appliance_status = await self.api.get_appliance_status(appliance_id)
                appliance_info = None if len(appliance_infos) == 0 else appliance_infos[0]
                appliance_model = appliance_info.get('model') if appliance_info else ""
                brand = appliance_info.get('brand') if appliance_info else ""
                # appliance_profile not reported
                appliance = Appliance(coordinator=self,
                                      pnc_id=appliance_id,
                                      name=appliance_name,
                                      brand=brand,
                                      model=appliance_model,
                                      state=appliance_state)
                appliances.appliances[appliance_id] = appliance

                appliance.setup(ElectroluxLibraryEntity(name=appliance_name, status=connection_status,
                                                        state=appliance_status, appliance_info=appliance_info,
                                                        capabilities=appliance_capabilities))
            _LOGGER.debug("Electrolux found appliance %s", ", ".join(list(appliances.appliances.keys())))
            return self.data
        except Exception as exception:
            _LOGGER.exception(exception)
            raise UpdateFailed() from exception

    async def _async_update_data(self):
        """Update data via library."""
        await self.async_login()
        appliances: Appliances = self.data.get('appliances', None)
        # Should not happen
        if appliances is None or len(appliances.get_appliances()) == 0:
            await self.setup_entities()
            appliances = self.data.get('appliances', None)

        for appliance_id in appliances.get_appliances():
            try:
                appliance: Appliance = appliances.get_appliances().get(appliance_id)
                appliance_status = await self.api.get_appliance_status(appliance_id)
                appliance.update(appliance_status)
            except Exception as exception:
                _LOGGER.exception(exception)
                raise UpdateFailed() from exception
        return self.data

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry, None)
