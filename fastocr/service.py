from base64 import b64encode

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


BACKENDS = {
    'baidu': BaiduOcr
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
