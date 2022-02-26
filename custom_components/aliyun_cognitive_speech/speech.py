import time
import requests
import logging
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json
from .const import (
    DOMAIN, DEFAULT_VOICE, TTS_URL, ENDPOINT_URI,
    TOKEN_OUTDATE, VOICES_LIST)

_LOGGER = logging.getLogger(__name__)


class CognitiveToken:
    def __init__(self, hass, access_key, access_secret):
        if DOMAIN not in hass.data:
            hass.data[DOMAIN] = {}
        self._hass = hass
        self.t_client = AcsClient(
            access_key,
            access_secret,
            "cn-shanghai"
        )

    def get_token(self):
        request = CommonRequest()
        request.set_method('POST')
        request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
        request.set_version('2019-02-28')
        request.set_action_name('CreateToken')
        response = self.t_client.do_action_with_exception(request)
        response_json = json.loads(response)
        if "Token" in response_json:
            token = response_json["Token"]
            if "Id" in token:
                return token["Id"]
            else:
                _LOGGER.error(f"No id in token:{token}")
        else:
            _LOGGER.error(f"Token not in response:{response_json}")


class CognitiveSpeech:
    def __init__(self, hass, access_key, access_secret, app_key, default_voice):
        self._token = CognitiveToken(hass, access_key, access_secret)
        self._app_key = app_key
        self._default_voice = default_voice

    def speech(self, text, voice, speed=0, pitch=0, vol=50):
        token = self._token.get_token()
        if token is not None:
            headers = {
                "X-NLS-Token": token,
                "content-type": "application/json"
            }
            data = {
                "appkey": self._app_key,
                "text": text,
                "format": "mp3",
                "voice": voice,
                "volume": int(vol),
                "speech_rate": int(speed),
                "pitch_rate": int(pitch)
            }
            try:
                r = requests.post(TTS_URL, headers=headers, data=json.dumps(data), timeout=10)
                if r.status_code == 200:
                    return r.content
                else:
                    _LOGGER.error(f"Text to speech failed, reason: {r.reason}")
            except Exception as e:
                _LOGGER.error(f"Text to speech failed, reason: {e}")
                pass
        return None
