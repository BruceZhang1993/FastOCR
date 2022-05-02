import json
import sys
from configparser import ConfigParser, NoSectionError, NoOptionError
from pathlib import Path
from typing import Optional, List

from fastocr.consts import APP_SETTING_FILE
from fastocr.util import Singleton, get_registry_value_new, set_registry_value, get_pyinstaller_path, \
    remove_registry_value


class Setting(metaclass=Singleton):
    def __init__(self, setting_file: Path = None):
        self.setting_file = setting_file
        if setting_file is None:
            self.setting_file = APP_SETTING_FILE
        self.parser = ConfigParser()
        self.loaded = False
        self._callbacks = []

    def get_config_file(self) -> Path:
        if not self.setting_file.exists():
            self.setting_file.parent.mkdir(parents=True, exist_ok=True)
            self.setting_file.touch()
        return self.setting_file

    def reload(self):
        self.parser.read(self.get_config_file())
        self.loaded = True

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
    def autostart(self) -> bool:
        return self.check_is_autostart()

    @autostart.setter
    def autostart(self, value: bool):
        self.set_is_autostart(value)

    @staticmethod
    def set_is_autostart(value: bool):
        if sys.platform == 'linux':
            if value:
                target_path = Path('/usr/share/applications/FastOCR.desktop')
                if target_path.exists() and not (Path.home() / '.config' / 'autostart' / 'FastOCR.desktop').exists():
                    (Path.home() / '.config' / 'autostart').mkdir(parents=True, exist_ok=True)
                    (Path.home() / '.config' / 'autostart' / 'FastOCR.desktop').symlink_to(target_path)
            else:
                (Path.home() / '.config' / 'autostart' / 'FastOCR.desktop').unlink(missing_ok=True)
        elif sys.platform == 'win32':
            import winreg
            if value:
                set_registry_value(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run',
                                   'FastOCR', get_pyinstaller_path())
            else:
                remove_registry_value(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run',
                                      'FastOCR')

    @staticmethod
    def check_is_autostart():
        if sys.platform == 'linux':
            if (Path.home() / '.config' / 'autostart' / 'FastOCR.desktop').exists():
                return True
        elif sys.platform == 'win32':
            import winreg
            return get_registry_value_new(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run',
                                          'FastOCR') is not None
        return False

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
