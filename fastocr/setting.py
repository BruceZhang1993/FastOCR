from configparser import ConfigParser, NoSectionError, NoOptionError
from pathlib import Path
from typing import Optional

from fastocr.util import Singleton


class Setting(metaclass=Singleton):
    def __init__(self):
        self.parser = ConfigParser()
        self.loaded = False
        self._callbacks = []

    @staticmethod
    def get_config_file() -> Path:
        file = Path.home() / '.config' / 'FastOCR' / 'config.ini'
        if not file.exists():
            file.parent.mkdir(parents=True, exist_ok=True)
            file.touch()
        return file

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
        self.reload()
        for cb in self._callbacks:
            try:
                cb()
            except:
                raise Exception('save callback error')

    def register_callback(self, callback):
        if callback not in self._callbacks:
            self._callbacks.append(callback)
