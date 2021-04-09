import json
from configparser import ConfigParser, NoSectionError, NoOptionError
from pathlib import Path
from typing import Optional, List

from fastocr.consts import APP_SETTING_FILE
from fastocr.util import Singleton


class Setting(metaclass=Singleton):
    def __init__(self):
        self.parser = ConfigParser()
        self.loaded = False
        self._callbacks = []

    @staticmethod
    def get_config_file() -> Path:
        if not APP_SETTING_FILE.exists():
            APP_SETTING_FILE.parent.mkdir(parents=True, exist_ok=True)
            APP_SETTING_FILE.touch()
        return APP_SETTING_FILE

    def reload(self):
        self.parser.read(self.get_config_file())

    def lazy_load(self):
        if not self.loaded:
            self.parser.read(self.get_config_file())
            self.loaded = True

    def sections(self):
        self.lazy_load()
        return self.parser.sections()

    def get_boolean(self, section, key):
        self.lazy_load()
        try:
            return self.parser.getboolean(section, key)
        except NoSectionError:
            return False
        except NoOptionError:
            return False

    def set_boolean(self, section, key, value: bool):
        self.lazy_load()
        return self.set(section, key, '1' if value else '0')

    def get(self, section, key):
        self.lazy_load()
        try:
            return self.parser.get(section, key)
        except NoSectionError:
            return ''
        except NoOptionError:
            return ''

    def set(self, section, key, value: Optional[str]):
        self.lazy_load()
        try:
            return self.parser.set(section, key, value)
        except NoSectionError:
            self.parser.add_section(section)
            return self.parser.set(section, key, value)

    def save(self):
        self.lazy_load()
        with self.get_config_file().open('w') as f:
            self.parser.write(f)
            f.flush()
        for cb in self._callbacks:
            try:
                cb()
            except Exception as e:
                print(e)

    def register_callback(self, callback):
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    @property
    def baidu_appid(self) -> str:
        return self.get('BaiduOCR', 'app_id')

    @baidu_appid.setter
    def baidu_appid(self, value: str):
        self.set('BaiduOCR', 'app_id', value)

    @property
    def baidu_apikey(self) -> str:
        return self.get('BaiduOCR', 'api_key')

    @baidu_apikey.setter
    def baidu_apikey(self, value: str):
        self.set('BaiduOCR', 'api_key', value)

    @property
    def baidu_seckey(self) -> str:
        return self.get('BaiduOCR', 'secret_key')

    @baidu_seckey.setter
    def baidu_seckey(self, value: str):
        self.set('BaiduOCR', 'secret_key', value)

    @property
    def baidu_accurate(self) -> bool:
        return self.get_boolean('BaiduOCR', 'use_accurate_mode')

    @baidu_accurate.setter
    def baidu_accurate(self, value: bool):
        self.set_boolean('BaiduOCR', 'use_accurate_mode', value)

    @property
    def baidu_languages(self) -> List[str]:
        languages_str = self.get('BaiduOCR', 'languages')
        if languages_str is None or languages_str == '':
            return []
        return json.loads(languages_str)

    @baidu_languages.setter
    def baidu_languages(self, value: List[str]):
        self.set('BaiduOCR', 'languages', json.dumps(value))

    @property
    def face_apikey(self) -> str:
        return self.get('FaceOCR', 'face_apikey')

    @face_apikey.setter
    def face_apikey(self, value: str):
        self.set('FaceOCR', 'face_apikey', value)

    @property
    def face_apisec(self) -> str:
        return self.get('FaceOCR', 'face_apisec')

    @face_apisec.setter
    def face_apisec(self, value: str):
        self.set('FaceOCR', 'face_apisec', value)

    @property
    def general_icon_theme(self) -> str:
        r = self.get('General', 'icon_theme')
        return r if r != '' else 'auto'

    @general_icon_theme.setter
    def general_icon_theme(self, value):
        self.set('General', 'icon_theme', value)

    @property
    def general_mode(self) -> int:
        """
        mode
        0: Copy to clipboard and send notification (Default)
        1: Send notification which can be clicked to copy to clipboard
        2: Open a new dialog with results (With more actions) [WIP]
        3: Do not send notification or clipboard (Send dbus signal for Linux)
        :return: mode int value
        :rtype: int
        """
        v = self.get('General', 'mode')
        return int(v) if v != '' else 0

    @general_mode.setter
    def general_mode(self, mode: int):
        self.set('General', 'mode', str(mode))
