"""
Component that will perform scene recognition with deepstack.
"""
import io
import logging

import deepstack.core as ds
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.image_processing import (
    ATTR_CONFIDENCE,
    CONF_ENTITY_ID,
    CONF_NAME,
    CONF_SOURCE,
    DOMAIN,
    PLATFORM_SCHEMA,
    ImageProcessingEntity,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_NAME,
    CONF_IP_ADDRESS,
    CONF_PORT,
)
from homeassistant.core import split_entity_id

_LOGGER = logging.getLogger(__name__)

CONF_API_KEY = "api_key"
CONF_TIMEOUT = "timeout"

DEFAULT_API_KEY = ""
DEFAULT_TIMEOUT = 10


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_IP_ADDRESS): cv.string,
        vol.Required(CONF_PORT): cv.port,
        vol.Optional(CONF_API_KEY, default=DEFAULT_API_KEY): cv.string,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
    }
)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the integration."""

    entities = []
    for camera in config[CONF_SOURCE]:
        object_entity = SceneEntity(
            config.get(CONF_IP_ADDRESS),
            config.get(CONF_PORT),
            config.get(CONF_API_KEY),
            config.get(CONF_TIMEOUT),
            camera.get(CONF_ENTITY_ID),
            camera.get(CONF_NAME),
        )
        entities.append(object_entity)
    add_devices(entities)


class SceneEntity(ImageProcessingEntity):
    """Perform a face classification."""

    def __init__(
        self, ip_address, port, api_key, timeout, camera_entity, name=None,
    ):
        """Init with the API key and model id."""
        super().__init__()
        self._dsscene = ds.DeepstackScene(ip_address, port, api_key, timeout)
        self._camera = camera_entity
        if name:
            self._name = name
        else:
            camera_name = split_entity_id(camera_entity)[1]
            self._name = "deepstack_scene_{}".format(camera_name)

        self._state = None
        self._predictions = {}

    def process_image(self, image):
        """Process an image."""
        self._state = None
        self._predictions = {}

        try:
            self._dsscene.detect(image)
        except ds.DeepstackException as exc:
            _LOGGER.error("Deepstack error : %s", exc)
            return

        self._predictions = self._dsscene.predictions.copy()
        self._state = self._predictions["label"]

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        attr = {}
        if self._predictions != {}:
            confidence = ds.format_confidence(self._predictions["confidence"])
            attr["confidence"]: f"{confidence} %"
        return attr
