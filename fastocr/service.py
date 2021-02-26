from base64 import b64encode
from hashlib import sha256
from time import time
from typing import List
from uuid import uuid1

from aiohttp import ClientSession

from fastocr.base import BaseOcr
from fastocr.setting import Setting
from fastocr.util import Singleton


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

    async def basic_general(self, image: bytes, lang='') -> List[str]:
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
            return [w_.get('words', '') for w_ in data.get('words_result', [])]

    async def close(self):
        await self.session.close()


class YoudaoOcr(BaseOcr):
    API_BASE = 'https://openapi.youdao.com/ocrapi'
    SALT = str(uuid1())

    def __init__(self, setting: Setting):
        self.appid = setting.get('YoudaoOCR', 'app_id')  # appKey in Youdao docs
        self.seckey = setting.get('YoudaoOCR', 'secret_key')  # appSecret in Youdao docs
        self.session = ClientSession()

    def truncate(self, image: bytes):
        q = b64encode(image).decode()
        q_size = len(q)
        if q is None:
            return None
        else:
            return q if q_size <= 20 else q[0:10] + str(q_size) + q[q_size - 10:q_size]

    def get_sign(self, image: bytes, timestamp: str):
        sign_str = f'{self.appid}{self.truncate(image)}{self.SALT}{timestamp}{self.seckey}'
        hasher = sha256()
        hasher.update(sign_str.encode())
        return hasher.hexdigest()

    async def basic_general(self, image: bytes, lang='') -> List[str]:
        curtime = str(int(time()))
        data = {
            'img': b64encode(image).decode(),
            'langType': lang if lang != '' else 'auto',
            'detectType': '10012',
            'imageType': '1',
            'appKey': self.appid,
            'salt': self.SALT,
            'sign': self.get_sign(image, curtime),
            'docType': 'json',
            'signType': 'v3',
            'curtime': curtime
        }
        async with self.session.post(f'{self.API_BASE}', data=data) as r:
            data = await r.json()
            if int(data.get('errorCode')) != 0:
                raise Exception(f"YoudaoOCR Error: {data.get('errorCode')}")
            rs = data.get('Result', {}).get('regions', [])
            result = []
            for r_ in rs:
                result += [l_.get('text') for l_ in r_.get('lines', [])]
            return result

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

    async def basic_general_ocr(self, image: bytes, lang='') -> List[str]:
        return await self.backend.basic_general(image, lang=lang)
