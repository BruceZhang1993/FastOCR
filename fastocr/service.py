import json
from base64 import b64encode
from hashlib import sha256
from time import time
from typing import List
from uuid import uuid1

from fastocr.base import BaseOcr
from fastocr.consts import APP_CACHE_DIR
from fastocr.setting import Setting


class BaiduOcr(BaseOcr):
    TOKEN_FILE = APP_CACHE_DIR / 'baidu_token_data.json'
    API_BASE = 'https://aip.baidubce.com/rest/2.0/ocr/v1'
    AUTH_BASE = 'https://aip.baidubce.com/oauth/2.0/token'

    def __init__(self, setting: Setting):
        super().__init__()
        self.appid = setting.baidu_appid
        self.apikey = setting.baidu_apikey
        self.seckey = setting.baidu_seckey
        self.use_accurate_mode = setting.baidu_accurate

    @property
    async def token(self):
        if self.TOKEN_FILE.exists():
            with self.TOKEN_FILE.open('r') as f:
                token_data = json.load(f)
            expires_in = token_data.get('expires_in', 0)
            timestamp = token_data.get('timestamp', 0)
            if time() < timestamp + expires_in:
                return token_data.get('token', '')
        token, expires_in = await self.get_token()
        timestamp = int(time())
        if expires_in:
            with self.TOKEN_FILE.open('w') as f:
                json.dump({
                    'token': token,
                    'expires_in': expires_in,
                    'timestamp': timestamp
                }, f)
        return token

    async def get_token(self):
        async with self.session.post(
                f'{self.AUTH_BASE}?grant_type=client_credentials&client_id={self.apikey}&client_secret={self.seckey}') as r:
            data = await r.json()
            if data.get('error_code') is not None:
                raise Exception(f"{data.get('error_code')}: {data.get('error_msg')}")
            return data.get('access_token'), data.get('expires_in')

    async def basic_general(self, image: bytes, lang='') -> List[str]:
        api_type = '/accurate_basic' if self.use_accurate_mode else '/general_basic'
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
        super().__init__()
        self.appid = setting.get('YoudaoOCR', 'app_id')  # appKey in Youdao docs
        self.seckey = setting.get('YoudaoOCR', 'secret_key')  # appSecret in Youdao docs

    @staticmethod
    def truncate(image: bytes):
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


class FaceOcr(BaseOcr):
    API_BASE = 'https://api-cn.faceplusplus.com'
    MIN_SIZE = 48
    MAX_SIZE = 800

    def __init__(self, setting: Setting):
        super().__init__()
        self.apikey = setting.face_apikey
        self.apisec = setting.face_apisec

    async def basic_general(self, image: bytes, lang='') -> List[str]:
        data = {
            'api_key': self.apikey,
            'api_secret': self.apisec,
            'image_base64': b64encode(image).decode()
        }
        async with self.session.post(f'{self.API_BASE}/imagepp/v1/recognizetext', data=data) as r:
            res = await r.json()
            if res.get('error_message'):
                raise Exception(res.get('error_message', ''))
            result = filter(lambda x: x.get('type') == 'textline', res.get('result', []))
            return [r.get('value', '') for r in result]

    async def close(self):
        await self.session.close()


BACKENDS = {
    'baidu': BaiduOcr,
    'youdao': YoudaoOcr,
    'face': FaceOcr,
}


class OcrService:
    def __init__(self, backend: str = 'baidu'):
        backend_class = BACKENDS.get(backend)
        if not backend_class:
            raise Exception(f'{backend} 后端不存在')
        self.setting = Setting()
        self.setting.reload()
        self.backend = backend_class(self.setting)

    def image_scaling(self) -> tuple:
        min_size = 0
        max_size = 0
        if hasattr(self.backend, 'MIN_SIZE'):
            min_size = getattr(self.backend, 'MIN_SIZE')
        if hasattr(self.backend, 'MAX_SIZE'):
            max_size = getattr(self.backend, 'MAX_SIZE')
        return min_size, max_size

    async def close(self):
        await self.backend.close()

    async def basic_general_ocr(self, image: bytes, lang='') -> List[str]:
        return await self.backend.basic_general(image, lang=lang)
