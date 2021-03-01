import asyncio
import json
from functools import partial
from pathlib import Path
from typing import Optional, List

import qasync
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice, QObject, pyqtSlot, pyqtProperty
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickWindow
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QApplication

from fastocr.grabber import CaptureWidget
from fastocr.service import OcrService
from fastocr.setting import Setting
from fastocr.util import DesktopInfo

if DesktopInfo.dbus_supported():
    from fastocr.bus import AppDBusObject


# noinspection PyPep8Naming
class SettingBackend(QObject):
    def __init__(self, parent=None):
        super(SettingBackend, self).__init__(parent)
        self.setting = Setting()

    @pyqtSlot()
    def save(self):
        self.setting.save()

    def getAppid(self) -> str:
        return self.setting.get('BaiduOCR', 'app_id')

    def setAppid(self, text: str):
        self.setting.set('BaiduOCR', 'app_id', text)

    appid = pyqtProperty(str, getAppid, setAppid)

    def getApikey(self) -> str:
        return self.setting.get('BaiduOCR', 'api_key')

    def setApikey(self, text: str):
        self.setting.set('BaiduOCR', 'api_key', text)

    apikey = pyqtProperty(str, getApikey, setApikey)

    def getSeckey(self) -> str:
        return self.setting.get('BaiduOCR', 'secret_key')

    def setSeckey(self, text: str):
        self.setting.set('BaiduOCR', 'secret_key', text)

    seckey = pyqtProperty(str, getSeckey, setSeckey)

    def getAccurate(self) -> bool:
        return self.setting.get_boolean('BaiduOCR', 'use_accurate_mode')

    def setAccurate(self, checked: bool):
        self.setting.set('BaiduOCR', 'use_accurate_mode', '1' if checked else '0')

    accurate = pyqtProperty(bool, getAccurate, setAccurate)

    def getLanguages(self) -> List[str]:
        languages_str = self.setting.get('BaiduOCR', 'languages')
        if languages_str is None or languages_str == '':
            return []
        return json.loads(languages_str)

    def setLanguages(self, langs: List[str]):
        self.setting.set('BaiduOCR', 'languages', json.dumps(langs))

    languages = pyqtProperty(list, getLanguages, setLanguages)

    def getYdAppid(self) -> str:
        return self.setting.get('YoudaoOCR', 'app_id')

    def setYdAppid(self, text: str):
        self.setting.set('YoudaoOCR', 'app_id', text)

    yd_appid = pyqtProperty(str, getYdAppid, setYdAppid)

    def getYdSeckey(self) -> str:
        return self.setting.get('YoudaoOCR', 'secret_key')

    def setYdSeckey(self, text: str):
        self.setting.set('YoudaoOCR', 'secret_key', text)

    yd_seckey = pyqtProperty(str, getYdSeckey, setYdSeckey)

    def getDefaultBackend(self) -> str:
        res = self.setting.get('General', 'default_backend')
        if res == '':
            return 'baidu'
        return res

    def setDefaultBackend(self, backend):
        self.setting.set('General', 'default_backend', backend)

    default_backend = pyqtProperty(str, getDefaultBackend, setDefaultBackend)


class AppTray(QSystemTrayIcon):
    def __init__(self, bus=None):
        super(AppTray, self).__init__()
        self.setting = None
        self.bus: Optional['AppDBusObject'] = bus
        self.capture_widget: Optional[CaptureWidget] = None
        self.engine: Optional[QQmlApplicationEngine] = None
        self.setting_window: Optional[QQuickWindow] = None
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
        loop = asyncio.get_event_loop()
        is_dark = loop.run_until_complete(DesktopInfo.is_dark_mode())
        if not is_dark:
            path = Path(__file__).parent / 'resource' / 'icon' / 'dark'
        else:
            path = Path(__file__).parent / 'resource' / 'icon' / 'light'
        self.setIcon(QIcon.fromTheme('fastocr-tray', QIcon((path / 'fastocr-tray.svg').as_posix())))
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
        default = self.setting.get('General', 'default_backend')
        if default == '':
            default = 'baidu'
        result = await OcrService(default).basic_general_ocr(self.pixmap_to_bytes(pixmap), lang=lang)
        data = '\n'.join(result)
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

    @qasync.asyncSlot()
    async def start_capture_lang(self, lang, _):
        await self.run_capture(.5, lang=lang)

    @qasync.asyncSlot()
    async def start_capture(self):
        await self.run_capture(.5)
