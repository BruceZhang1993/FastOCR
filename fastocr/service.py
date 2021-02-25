from base64 import b64encode
from hashlib import sha256
from uuid import uuid1
from time import time

from aiohttp import ClientSession

from fastocr.setting import Setting
from fastocr.util import Singleton


class BaseOcr:
    pass


class BaiduOcr(BaseOcr):
    API_BASE = 'https://aip.baidubce.com/rest/2.0/ocr/v1'
    AUTH_BASE = 'https://aip.baidubce.com/oauth/2.0/token'

    def __init__(self, setting: Setting):
        self._token = ''
        self.appid = setting.get('BaiduOCR', 'app_id')
        self.apikey = setting.get('BaiduOCR', 'api_key')
        self.seckey = setting.get('BaiduOCR', 'secret_key')
        self.use_accurate_mode = setting.get_boolean('BaiduOCR', 'use_accurate_mode')
        self.session = ClientSession()

    @property
    async def token(self):
        if self._token == '':
            token, _ = await self.get_token()
            self._token = token
        return self._token

    async def get_token(self):
        async with self.session.post(
                f'{self.AUTH_BASE}?grant_type=client_credentials&client_id={self.apikey}&client_secret={self.seckey}') as r:
            data = await r.json()
            return data.get('access_token'), data.get('expires_in')

    async def basic_general(self, image: bytes, lang=''):
        if self.use_accurate_mode:
            api_type = '/accurate_basic'
        else:
            api_type = '/general_basic'
        data = {
            'image': b64encode(image).decode(),
            'language_type': lang if lang != '' else 'CHN_ENG'
        }
        async with self.session.post(f'{self.API_BASE}{api_type}?access_token={await self.token}', data=data) as r:
            data = await r.json()
            if data.get('error_code') is not None:
                raise Exception(f"{data.get('error_code')}: {data.get('error_msg')}")
            return data

    async def close(self):
        await self.session.close()

class YoudaoOcr(BaseOcr):
    API_BASE = 'https://openapi.youdao.com/ocrapi'
    CURTIME = str(int(time))
    SALT = str(uuid1)

    def __init__(self, setting: Setting):
        self._sign = ''
        self.appid = setting.get('YoudaoOCR', 'app_id') # appKey in Youdao docs
        self.seckey = setting.get('YoudaoOCR', 'secret_key') # appSecret in Youdao docs
        self.session = ClientSession()

    @property
    def sign(self):
        if self._sign == '':
            sign, _ = self.get_sign()
            self._sign = sign
        return self._sign

    def truncate(self, image: bytes):
        q = b64encode(image).decode()
        q_size = len(q)
        if q is None:
            return None
        else:
            return q if q_size <= 20 else q[0:10] + str(q_size) + q[q_size - 10:q_size]

    def get_sign(self):
        sign_str = f'{self.app_id}{self.truncate()}{self.SALT}{self.CURTIME}{self.seckey}'
        sign_hash = sha256().update(sign_str)
        return sha256().hexdigest

    async def basic_general(self, image: bytes, lang=''):
        data = {
            'img': b64encode(image).decode(),
            'langType': lang if lang != '' else 'auto',
            'detectType': '10012',
            'imageType': '1',
            'appKey': self.appid,
            'salt': self.SALT,
            'sign': self.sign,
            'docType': 'json',
            'signType': 'v3',
            'curtime': self.CURTIME
        }
        async with self.session.post(f'{self.API_BASE}', data=data) as r:
            data = await r.json()
            if data.get('errorCode') is not None:
                raise Exception(f"{data.get('errorCode')}")
            return data

    async def close(self):
        await self.session.close()

BACKENDS = {
    'baidu': BaiduOcr,
    'youdao': YoudaoOcr
}


class OcrService(metaclass=Singleton):
    def __init__(self, backend: str = 'baidu'):
        backend_class = BACKENDS.get(backend)
        if not backend_class:
            raise Exception(f'{backend} 后端不存在')
        self.setting = Setting()
        self.backend = backend_class(self.setting)

    async def close(self):
        await self.backend.close()

    async def basic_general_ocr(self, image: bytes, lang=''):
        return await self.backend.basic_general(image, lang=lang)
