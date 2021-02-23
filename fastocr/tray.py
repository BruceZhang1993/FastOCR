import asyncio
import json
from functools import partial
from pathlib import Path
from typing import Optional, List

import qasync
from PySide2.QtCore import QByteArray, QBuffer, QIODevice, QObject, Property, Slot
from PySide2.QtGui import QPixmap, QIcon, QWindow
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtWidgets import QSystemTrayIcon, QMenu, QApplication

from fastocr.bus import AppDBusObject
from fastocr.grabber import CaptureWidget
from fastocr.service import OcrService
from fastocr.setting import Setting


# noinspection PyPep8Naming
class SettingBackend(QObject):
    def __init__(self, parent=None):
        super(SettingBackend, self).__init__(parent)
        self.setting = Setting()

    @Slot()
    def save(self):
        self.setting.save()

    def getAppid(self) -> str:
        return self.setting.get('BaiduOCR', 'app_id')

    def setAppid(self, text: str):
        self.setting.set('BaiduOCR', 'app_id', text)

    appid = Property(str, getAppid, setAppid)

    def getApikey(self) -> str:
        return self.setting.get('BaiduOCR', 'api_key')

    def setApikey(self, text: str):
        self.setting.set('BaiduOCR', 'api_key', text)

    apikey = Property(str, getApikey, setApikey)

    def getSeckey(self) -> str:
        return self.setting.get('BaiduOCR', 'secret_key')

    def setSeckey(self, text: str):
        self.setting.set('BaiduOCR', 'secret_key', text)

    seckey = Property(str, getSeckey, setSeckey)

    def getAccurate(self) -> bool:
        return self.setting.get_boolean('BaiduOCR', 'use_accurate_mode')

    def setAccurate(self, checked: bool):
        self.setting.set('BaiduOCR', 'use_accurate_mode', '1' if checked else '0')

    accurate = Property(bool, getAccurate, setAccurate)

    def getLanguages(self) -> List[str]:
        languages_str = self.setting.get('BaiduOCR', 'languages')
        if languages_str is None or languages_str == '':
            return []
        return json.loads(languages_str)

    def setLanguages(self, langs: List[str]):
        self.setting.set('BaiduOCR', 'languages', json.dumps(langs))

    languages = Property(list, getLanguages, setLanguages)


class AppTray(QSystemTrayIcon):
    def __init__(self, bus=None):
        super(AppTray, self).__init__()
        self.setting = None
        self.bus: Optional[AppDBusObject] = bus
        self.capture_widget: Optional[CaptureWidget] = None
        self.engine: Optional[QQmlApplicationEngine] = None
        self.setting_window: Optional[QWindow] = None
        self.backend: Optional[SettingBackend] = None
        self.language_actions = dict()
        self.load_qml()
        self.initialize()

    def load_qml(self):
        self.engine = QQmlApplicationEngine()
        self.setting = Setting()
        self.backend = SettingBackend()
        self.engine.rootContext().setContextProperty('backend', self.backend)
        self.engine.load((Path(__file__).parent / 'qml' / 'setting.qml').as_posix())
        self.setting_window = self.engine.rootObjects()[0]

    # noinspection PyUnresolvedReferences
    def initialize(self):
        palette = QApplication.palette()
        back_color = palette.color(palette.Normal, palette.Window)
        lightness = back_color.lightness()
        if lightness >= 180:
            QIcon.setFallbackSearchPaths(
                QIcon.fallbackSearchPaths() + [(Path(__file__).parent / 'resource' / 'icon' / 'dark').as_posix()])
        else:
            QIcon.setFallbackSearchPaths(
                QIcon.fallbackSearchPaths() + [(Path(__file__).parent / 'resource' / 'icon' / 'light').as_posix()])
        self.setIcon(QIcon.fromTheme('fastocr-tray'))
        self.activated.connect(self.activate_action)
        # Context menu
        self.setContextMenu(QMenu())
        context_menu = self.contextMenu()
        capture_action = context_menu.addAction(self.tr('Capture'))

        self.language_menu = QMenu(self.tr('Capture (Other Languages)'))
        context_menu.addMenu(self.language_menu)
        self.update_menu()

        setting_action = context_menu.addAction(self.tr('Setting'))
        quit_action = context_menu.addAction(self.tr('Quit'))
        capture_action.triggered.connect(self.start_capture)
        setting_action.triggered.connect(self.open_setting)
        quit_action.triggered.connect(self.quit_app)
        self.setting.register_callback(self.update_menu)

    def update_menu(self):
        self.language_menu.clear()
        self.language_actions.clear()
        language_str = self.setting.get('BaiduOCR', 'languages')
        if language_str is None or language_str == '':
            languages = []
        else:
            languages = json.loads(language_str)
        for lang in languages:
            self.language_actions[lang] = self.language_menu.addAction(lang)
            # noinspection PyUnresolvedReferences
            self.language_actions[lang].triggered.connect(partial(self.start_capture_lang, lang))

    def activate_action(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.open_setting()
        elif reason == QSystemTrayIcon.Trigger:
            self.start_capture()

    @qasync.asyncSlot()
    async def open_setting(self):
        setting_dir = Path.home() / '.config' / 'FastOCR'
        setting_dir.mkdir(parents=True, exist_ok=True)
        setting_file = setting_dir / 'config.ini'
        if not setting_file.exists():
            setting_file.touch()
        # await open_in_default(setting_file.as_posix())
        self.setting_window.show()

    def quit_app(self, _):
        self.setting_window.close()
        self.hide()
        QApplication.quit()

    @staticmethod
    def pixmap_to_bytes(pixmap: QPixmap) -> bytes:
        ba = QByteArray()
        bf = QBuffer(ba)
        bf.open(QIODevice.WriteOnly)
        ok = pixmap.save(bf, 'PNG')
        assert ok
        return ba.data()

    @qasync.asyncSlot(QPixmap)
    async def start_ocr(self, no_copy: bool = False, lang='', pixmap: QPixmap = None):
        self.capture_widget.close()
        result = await OcrService().basic_general_ocr(self.pixmap_to_bytes(pixmap), lang=lang)
        data = '\n'.join([w_.get('words', '') for w_ in result.get('words_result', [])])
        if no_copy:
            if self.bus is not None:
                self.bus.captured(data)
                self.showMessage('OCR 识别成功', '已发送 DBus 信号', QIcon.fromTheme('object-select-symbolic'), 5000)
            else:
                self.showMessage('OCR 识别成功', '当前平台不支持 DBus', QIcon.fromTheme('object-select-symbolic'), 5000)
        else:
            clipboard = qasync.QApplication.clipboard()
            clipboard.setText(data)
            if self.bus is not None:
                self.bus.captured(data)
            self.showMessage('OCR 识别成功', '已复制到系统剪切板', QIcon.fromTheme('object-select-symbolic'), 5000)

    async def run_capture(self, seconds=.5, no_copy=False, lang=''):
        self.contextMenu().close()
        await asyncio.sleep(seconds)
        self.capture_widget = CaptureWidget()
        self.capture_widget.captured.connect(partial(self.start_ocr, no_copy, lang))
        self.capture_widget.showFullScreen()

    @qasync.asyncSlot(str)
    async def start_capture_lang(self, lang):
        await self.run_capture(.5, lang=lang)

    @qasync.asyncSlot()
    async def start_capture(self):
        await self.run_capture(.5)
