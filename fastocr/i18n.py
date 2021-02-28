import locale
from pathlib import Path

from PyQt5.QtCore import QTranslator

from fastocr.util import Singleton


class Translation(metaclass=Singleton):
    def __init__(self):
        self.translator = QTranslator()

    def load(self, name: str = None):
        if name is None:
            name = locale.getdefaultlocale()[0]
            if name is not None:
                name = name.lower()
        trans = Path(__file__).parent / 'i18n' / f'{name}.qm'
        if trans.exists():
            self.translator.load(trans.as_posix())
        return self

    def install(self, app):
        app.installTranslator(self.translator)
