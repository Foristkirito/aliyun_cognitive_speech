import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.tts import PLATFORM_SCHEMA, Provider
from .const import (
    DEFAULT_LANGUAGE, SUPPORT_LANGUAGES,
    OPT_VOICE, OPT_SPEED, OPT_VOL,
    OPT_PITCH, CONF_DEFAULT_VOICE, CONF_ACCESS_SECRET, CONF_ACCESS_KEY, CONF_APP_KEY
)
from .speech import CognitiveSpeech

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_ACCESS_KEY): cv.string,
        vol.Required(CONF_ACCESS_SECRET): cv.string,
        vol.Required(CONF_APP_KEY): cv.string
    }
)


async def async_get_engine(hass, config, discovery_info=None):
    return CognitiveProvider(hass, config)


class CognitiveProvider(Provider):
    def __init__(self, hass, config):
        self.hass = hass
        self.name = "Azure Cognitive Speech"
        self._access_key = config.get(CONF_ACCESS_KEY)
        self._access_secret = config.get(CONF_ACCESS_SECRET)
        self._app_key = config.get(CONF_APP_KEY)

    @property
    def default_language(self):
        return DEFAULT_LANGUAGE

    @property
    def supported_languages(self):
        return SUPPORT_LANGUAGES

    @property
    def supported_options(self):
        return [OPT_VOICE, OPT_SPEED, OPT_PITCH, OPT_VOL]

    @property
    def default_options(self):
        return {OPT_VOICE: "aixia", OPT_SPEED: 0, OPT_PITCH: 0, OPT_VOL: 60}

    def get_tts_audio(self, message, language, options=None):
        voice = options.get(OPT_VOICE) if options is not None else None
        speed = options.get(OPT_SPEED) if options is not None else None
        pitch = options.get(OPT_PITCH) if options is not None else None
        tts_vol = options.get(OPT_VOL) if options is not None else None
        speech = CognitiveSpeech(self.hass, self._access_key, self._access_secret, self._app_key, voice)
        r = speech.speech(message, voice=voice, speed=speed, pitch=pitch, vol=tts_vol)
        if r is not None:
            return "mp3", r
        return None, None

