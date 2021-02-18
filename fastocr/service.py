from aip import AipOcr

from fastocr.setting import Setting
from fastocr.util import Singleton


class OcrService(metaclass=Singleton):
    APP_ID = ''
    API_KEY = ''
    SECRET_KEY = ''
    USE_ACCURATE_MODE = False

    def __init__(self):
        self.read_config()
        if self.APP_ID == '':
            raise Exception('OCR 配置不存在')
        self.client = AipOcr(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        self.client.setConnectionTimeoutInMillis(5000)
        self.client.setSocketTimeoutInMillis(20000)

    def read_config(self):
        self.setting = Setting()
        self.APP_ID = self.setting.get('BaiduOCR', 'APP_ID')
        self.API_KEY = self.setting.get('BaiduOCR', 'API_KEY')
        self.SECRET_KEY = self.setting.get('BaiduOCR', 'SECRET_KEY')
        self.USE_ACCURATE_MODE = self.setting.get_boolean('BaiduOCR', 'USE_ACCURATE_MODE')

    def basic_general_ocr(self, image: bytes):
        options = {
            'language_type': 'CHN_ENG',
        }
        if self.USE_ACCURATE_MODE:
            return self.client.basicAccurate(image, options)
        else:
            return self.client.basicGeneral(image, options)
