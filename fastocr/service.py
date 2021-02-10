from pathlib import Path
from configparser import ConfigParser

from aip import AipOcr

from fastocr.util import Singleton


class OcrService(metaclass=Singleton):
    APP_ID = ''
    API_KEY = ''
    SECRET_KEY = ''

    def __init__(self):
        self.read_config()
        if self.APP_ID == '':
            raise Exception('OCR 配置不存在')
        self.client = AipOcr(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        self.client.setConnectionTimeoutInMillis(5000)
        self.client.setSocketTimeoutInMillis(20000)

    def read_config(self):
        file = Path.home() / '.config' / 'FastOCR' / 'config.ini'
        if not file.exists():
            file = Path(__file__).parent.parent / 'config.ini'
            if not file.exists():
                return
        parser = ConfigParser()
        parser.read(file)
        self.APP_ID = parser.get('BaiduOCR', 'APP_ID')
        self.API_KEY = parser.get('BaiduOCR', 'API_KEY')
        self.SECRET_KEY = parser.get('BaiduOCR', 'SECRET_KEY')

    def basic_general_ocr(self, image: bytes):
        return self.client.basicGeneral(image, {
            'language_type': 'CHN_ENG',
            'detect_language': True
        })
