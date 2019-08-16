'''
Docker Monitor component

For more details about this component, please refer to the documentation at
https://github.com/Sanderhuisman/docker_monitor
'''
import logging
import time

import voluptuous as vol
from homeassistant.const import (
    CONF_EVENT,
    CONF_HOSTS,
    CONF_MONITORED_CONDITIONS,
    CONF_NAME,
    CONF_SCAN_INTERVAL,
    CONF_SENSORS,
    EVENT_HOMEASSISTANT_STOP
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import load_platform
from homeassistant.util import slugify as util_slugify

from .const import (
    CONF_CONTAINERS,
    CONF_MONITOR_CONTAINER_CONDITIONS,
    CONF_MONITOR_UTILISATION_CONDITIONS,
    CONF_CONTAINER_SWITCH,
    CONF_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    EVENT_CONTAINER,
    PLATFORMS,
    SERVICE_EXEC,
    SERVICE_RUN
)
from .helpers import DockerMonitorApi

VERSION = '0.1.0-b0'

_LOGGER = logging.getLogger(__name__)

CONF_MONITOR_UTILISATION_CONDITIONS_KEYS = list(
    CONF_MONITOR_UTILISATION_CONDITIONS.keys())
CONF_MONITOR_CONTAINER_CONDITIONS_KEYS = list(
    CONF_MONITOR_CONTAINER_CONDITIONS.keys())

CONTAINER_SCHEMA = vol.Schema({
    vol.Optional(CONF_SENSORS, default=CONF_MONITOR_CONTAINER_CONDITIONS_KEYS):
        vol.All(cv.ensure_list, [
                vol.In(CONF_MONITOR_CONTAINER_CONDITIONS_KEYS)]),
    vol.Optional(CONF_CONTAINER_SWITCH, default=True):
        cv.boolean,
})

SERVER_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME):
        cv.string,
    vol.Required(CONF_URL):
        cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL):
        cv.time_period,
    vol.Optional(CONF_EVENT, default=False):
        cv.boolean,
    vol.Optional(CONF_MONITORED_CONDITIONS,
                 default=CONF_MONITOR_UTILISATION_CONDITIONS_KEYS):
        vol.All(cv.ensure_list, [
            vol.In(CONF_MONITOR_UTILISATION_CONDITIONS_KEYS)]),
    vol.Required(CONF_CONTAINERS, default={}):
        vol.Schema({cv.string: CONTAINER_SCHEMA})
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOSTS):
            vol.All(cv.ensure_list, [SERVER_SCHEMA]),
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    hass.data[DOMAIN] = {}
    for host in config[DOMAIN][CONF_HOSTS]:
        name = host[CONF_NAME]

        try:
            api = DockerMonitorApi(host[CONF_URL])
        except ImportError as e:
            _LOGGER.error("Error setting up Docker API ({})".format(e))
            return False
        else:
            hass.data[DOMAIN][name] = api

            for component in PLATFORMS:
                load_platform(hass, component, DOMAIN, host, config)

            if host[CONF_EVENT]:
                def event_listener(message):
                    event = util_slugify("{} {}".format(name, EVENT_CONTAINER))
                    hass.bus.fire(event, message)
                api.start(event_listener)
            else:
                api.start()

    async def async_service_handler(service):
        """Handle service calls."""
        name = service.data.get(CONF_NAME, None)
        if name:
            if service.service == SERVICE_RUN:
                _LOGGER.error("Run on host {}".format(name))
                # client.containers.run('alpine', 'echo hello world')
                # container = client.containers.run('bfirsh/reticulate-splines', detach=True)
            elif service.service == SERVICE_EXEC:
                _LOGGER.error("Exec on host {}".format(name))
            else:
                _LOGGER.error("Service {} not found".format(service.service))

    SERVICE_SCHEMA = vol.Schema({
        vol.Required(CONF_NAME):
            vol.All(cv.string, vol.In([host[CONF_NAME] for host in config[DOMAIN][CONF_HOSTS]]))
    })

    service_runschema = SERVICE_SCHEMA.extend({
        vol.Required('image'):
            cv.string,
        vol.Optional('command'):
            cv.string,
        vol.Optional('remove'):
            cv.boolean,
    })
    service_exec_schema = SERVICE_SCHEMA.extend({
        vol.Required('container'):
            cv.string,
        vol.Required('command'):
            cv.boolean,
    })

    hass.services.async_register(DOMAIN, SERVICE_RUN, async_service_handler, schema=service_runschema)
    hass.services.async_register(DOMAIN, SERVICE_EXEC, async_service_handler, schema=service_exec_schema)

    def monitor_stop(_service_or_event):
        """Stop the monitor threads."""
        _LOGGER.info("Stopping threads for Docker monitor")
        for api in hass.data[DOMAIN].values():
            api.exit()

    hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, monitor_stop)

    return True
