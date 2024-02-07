"""electrolux status integration."""
import asyncio
import json
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Config
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady, ConfigEntryAuthFailed, ConfigEntryError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .api import Appliance, Appliances, ElectroluxLibraryEntity
from .const import CONF_LANGUAGE, DEFAULT_LANGUAGE
from .const import CONF_PASSWORD, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
from .const import CONF_USERNAME
from .const import DOMAIN
from .const import PLATFORMS
from .const import languages
#from pyelectroluxocp import OneAppApi
from .electroluxwrapper import OneAppApi
from .pyelectroluxconnect_util import pyelectroluxconnect_util

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

    # For polling
    #coordinator = ElectroluxCoordinator(hass, client=client, update_interval=update_interval)
    coordinator = ElectroluxCoordinator(hass, client=client)
    if not await coordinator.async_login():
        raise Exception("Electrolux wrong credentials")

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Initialize entities
    await coordinator.setup_entities()
    await coordinator.listen_websocket()

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, coordinator.api.close)
    )

    # Fill in the values for first time
    await coordinator.async_config_entry_first_refresh()

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

    def __init__(self, hass: HomeAssistant, client: OneAppApi) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN)

    async def async_login(self) -> bool:
        try:
            # Check that one can extract the appliance list to confirm login
            token = await self.api.get_user_token()
            if token and token.token:
                _LOGGER.debug("Electrolux logged successfully, %s", token.token)
                return True
            _LOGGER.debug("Electrolux wrong credentials")
        except Exception as ex:
            _LOGGER.error("Could not log in to ElectroluxStatus, %s", ex)
            raise ex
        return False

    def incoming_data(self, data: dict[str, dict[str, any]]):
        _LOGGER.debug("Electrolux appliance state updated %s", json.dumps(data))
        self.async_set_updated_data(data)

    async def listen_websocket(self):
        appliances: Appliances = self.data.get('appliances', None)
        ids = appliances.get_appliance_ids()
        if ids is None or len(ids) == 0:
            return
        await self.api.watch_for_appliance_state_updates(ids, self.incoming_data)

    async def setup_entities(self):
        _LOGGER.debug("Electrolux setup_entities")
        appliances = Appliances({})
        self.data = {
            "appliances": appliances
        }
        try:
            appliances_list = await self.api.get_appliances_list()
            if appliances_list is None:
                _LOGGER.error("Electrolux unable to retrieve appliances list. Cancelling setup")
                raise ConfigEntryFailed
            _LOGGER.debug("Electrolux update appliances %s %s",self.api, json.dumps(appliances_list))
            for appliance_json in appliances_list:
                appliance_capabilities = None
                appliance_id = appliance_json.get('applianceId')
                connection_status = appliance_json.get('connectionState')
                _LOGGER.debug("Electrolux found appliance %s", appliance_id)
                # appliance_profile = await self.hass.async_add_executor_job(self.api.getApplianceProfile, appliance)
                appliance_name = appliance_json.get('applianceData').get('applianceName')
                appliance_infos = await self.api.get_appliances_info([appliance_id])
                appliance_state = await self.api.get_appliance_state(appliance_id)
                _LOGGER.debug("Electrolux get_appliance_status result %s", json.dumps(appliance_state))
                try:
                    appliance_capabilities = await self.api.get_appliance_capabilities(appliance_id)
                    _LOGGER.debug("Electrolux appliance capabilities %s", json.dumps(appliance_capabilities))
                except Exception as exception:
                    _LOGGER.warning("Electrolux unable to retrieve capabilities, we are going on our own")

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
                                                        state=appliance_state, appliance_info=appliance_info,
                                                        capabilities=appliance_capabilities))
            return self.data
        except Exception as exception:
            _LOGGER.exception(exception)
            raise UpdateFailed() from exception


    async def _async_update_data(self):
        """Update data via library."""
        appliances: Appliances = self.data.get('appliances', None)
        # Should not happen : wonder if this is not the cause of infinite loop of integrations creations => disabled
        # if appliances is None or len(appliances.get_appliances()) == 0:
        #     await self.setup_entities()
        #     appliances = self.data.get('appliances', None)

        for appliance_id in appliances.get_appliances():
            try:
                appliance: Appliance = appliances.get_appliances().get(appliance_id)
                appliance_status = await self.api.get_appliance_state(appliance_id)
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
    _LOGGER.debug("Electrolux async_reload_entry")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
