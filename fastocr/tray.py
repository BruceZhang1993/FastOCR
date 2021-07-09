import asyncio
from functools import partial
from pathlib import Path
from typing import Optional, List

import qasync
# noinspection PyUnresolvedReferences
from PyQt5.QtCore import QByteArray, QBuffer, QIODevice, QObject, pyqtSlot, pyqtProperty
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtQuick import QQuickWindow
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QApplication

from fastocr.consts import APP_SETTING_FILE
from fastocr.grabber import CaptureWidget, CaptureAction
from fastocr.service import OcrService, BaiduOcr
from fastocr.setting import Setting
from fastocr.util import DesktopInfo, open_in_default, get_environment_values

if DesktopInfo.dbus_supported():
    from fastocr.bus import AppDBusObject


# noinspection PyPep8Naming,PyPropertyDefinition
class SettingBackend(QObject):
    def __init__(self, tray=None, parent=None):
        super(SettingBackend, self).__init__(parent)
        self.setting = Setting()
        self.tray: Optional[AppTray] = tray

    @pyqtSlot()
    def save(self):
        self.setting.save()
        self.setting.reload()
        if self.tray is not None:
            self.tray.update_menu()
            self.tray.update_token()

    @pyqtSlot()
    def open_setting_file(self):
        asyncio.gather(open_in_default(APP_SETTING_FILE.as_posix()))

    # Consts
    @pyqtProperty(str, constant=True)
    def appver(self) -> str:
        import pkg_resources
        return pkg_resources.get_distribution('fastocr').version

    @appver.setter
    def appver(self, text: str):
        pass

    @pyqtProperty(list, constant=True)
    def all_language_tags(self) -> list:
        return ['JAP', 'KOR', 'FRE', 'SPA', 'GER', 'RUS']

    @pyqtProperty(list, constant=True)
    def all_language_names(self) -> list:
        return ['Japanese', 'Korea', 'French', 'Spanish', 'Germany', 'Russian']

    # Environment
    @pyqtProperty(list, constant=True)
    def about_data(self) -> list:
        result = []
        values = get_environment_values()
        for k, v in values.items():
            result.append({'name': k, 'value': str(v)})
        return result

    # Settings
    @pyqtProperty(str, constant=True)
    def appid(self) -> str:
        return self.setting.baidu_appid

    @appid.setter
    def appid(self, text: str):
        self.setting.baidu_appid = text

    @pyqtProperty(str, constant=True)
    def apikey(self) -> str:
        return self.setting.baidu_apikey

    @apikey.setter
    def apikey(self, text: str):
        self.setting.baidu_apikey = text

    @pyqtProperty(str, constant=True)
    def seckey(self) -> str:
        return self.setting.baidu_seckey

    @seckey.setter
    def seckey(self, text: str):
        self.setting.baidu_seckey = text

    @pyqtProperty(bool, constant=True)
    def accurate(self) -> bool:
        return self.setting.baidu_accurate

    @accurate.setter
    def accurate(self, checked: bool):
        self.setting.baidu_accurate = checked

    @pyqtProperty(list, constant=True)
    def languages(self) -> List[str]:
        return self.setting.baidu_languages

    @languages.setter
    def languages(self, langs: List[str]):
        self.setting.baidu_languages = langs

    @pyqtProperty(str, constant=True)
    def yd_appid(self) -> str:
        return self.setting.get('YoudaoOCR', 'app_id')

    @yd_appid.setter
    def yd_appid(self, text: str):
        self.setting.set('YoudaoOCR', 'app_id', text)

    @pyqtProperty(str, constant=True)
    def yd_seckey(self) -> str:
        return self.setting.get('YoudaoOCR', 'secret_key')

    @yd_seckey.setter
    def yd_seckey(self, text: str):
        self.setting.set('YoudaoOCR', 'secret_key', text)

    @pyqtProperty(str, constant=True)
    def face_apikey(self) -> str:
        return self.setting.face_apikey

    @face_apikey.setter
    def face_apikey(self, value: str):
        self.setting.face_apikey = value

    @pyqtProperty(str, constant=True)
    def face_apisec(self) -> str:
        return self.setting.face_apisec

    @face_apisec.setter
    def face_apisec(self, value: str):
        self.setting.face_apisec = value

    @pyqtProperty(str, constant=True)
    def default_backend(self) -> str:
        res = self.setting.get('General', 'default_backend')
        if res == '':
            return 'baidu'
        return res

    @default_backend.setter
    def default_backend(self, backend):
        self.setting.set('General', 'default_backend', backend)

    @pyqtProperty(str, constant=True)
    def icon_theme(self) -> str:
        return self.setting.general_icon_theme

    @icon_theme.setter
    def icon_theme(self, value):
        self.setting.general_icon_theme = value

    @pyqtProperty(int, constant=True)
    def mode(self) -> int:
        return self.setting.general_mode

    @mode.setter
    def mode(self, value: int):
        self.setting.general_mode = value


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
        self.saved_data = None
        self.load_qml()
        self.initialize()

    def load_qml(self):
        self.engine = QQmlApplicationEngine()
        self.setting = Setting()
        self.backend = SettingBackend(tray=self)
        self.engine.setOutputWarningsToStandardError(False)
        self.engine.rootContext().setContextProperty('backend', self.backend)
        self.engine.load((Path(__file__).parent / 'qml' / 'main.qml').as_posix())
        self.setting_window = self.engine.rootObjects()[0]

    # noinspection PyUnresolvedReferences
    def initialize(self):
        if not DesktopInfo.tray_supported():
            self.showMessage('错误信息', '当前环境不支持系统托盘显示，应用将正常退出', QIcon.fromTheme('dialog-error-symbolic'), 5000)
            print('当前环境不支持系统托盘显示，应用将正常退出')
            QApplication.quit()
        self.setToolTip('FastOCR')
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
        # self.setting.register_callback(self.update_menu)
        # self.setting.register_callback(self.update_token)
        self.messageClicked.connect(self.message_clicked)

    def message_clicked(self):
        if self.saved_data is not None:
            clipboard = qasync.QApplication.clipboard()
            clipboard.setText(self.saved_data)
            self.saved_data = None

    def update_icon(self):
        icon_theme = self.setting.general_icon_theme
        if icon_theme in ['', 'auto']:
            is_dark = DesktopInfo.is_dark_mode()
            if not is_dark:
                path = Path(__file__).parent / 'resource' / 'icon' / 'dark'
            else:
                path = Path(__file__).parent / 'resource' / 'icon' / 'light'
        else:
            path = Path(__file__).parent / 'resource' / 'icon' / icon_theme
        self.setIcon(QIcon.fromTheme('fastocr-tray', QIcon((path / 'fastocr-tray.png').as_posix())))

    def update_token(self):
        default_backend = self.setting.get('General', 'default_backend')
        if default_backend == '':
            default_backend = 'baidu'
        if default_backend == 'baidu':
            BaiduOcr.TOKEN_FILE.unlink(missing_ok=True)

    def update_menu(self):
        self.update_icon()
        default_backend = self.setting.get('General', 'default_backend')
        if default_backend == '':
            default_backend = 'baidu'
        self.setToolTip(f'FastOCR ({default_backend})')
        self.language_menu.clear()
        self.language_actions.clear()
        for lang in self.setting.baidu_languages:
            self.language_actions[lang] = self.language_menu.addAction(lang)
            # noinspection PyUnresolvedReferences
            self.language_actions[lang].triggered.connect(partial(self.start_capture_lang, lang))

    def activate_action(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.open_setting()
        elif reason == QSystemTrayIcon.Trigger:
            self.start_capture()

    @pyqtSlot()
    def open_setting(self):
        setting_dir = Path.home() / '.config' / 'FastOCR'
        setting_dir.mkdir(parents=True, exist_ok=True)
        setting_file = setting_dir / 'config.ini'
        if not setting_file.exists():
            setting_file.touch()
        # await open_in_default(setting_file.as_posix())
        self.setting_window.show()
        self.setting_window.requestActivate()

    def quit_app(self, _):
        self.setting_window.close()
        self.hide()
        QApplication.quit()

    @staticmethod
    def pixmap_to_bytes(pixmap: QPixmap) -> bytes:
        image = pixmap.toImage()
        grayed = image.convertToFormat(QImage.Format.Format_Grayscale8)
        ba = QByteArray()
        bf = QBuffer(ba)
        bf.open(QIODevice.WriteOnly)
        ok = grayed.save(bf, 'PNG')
        assert ok
        return ba.data()

    @staticmethod
    def image_resize(pixmap: QPixmap, min_size, max_size) -> QPixmap:
        from_width, from_height = pixmap.width(), pixmap.height()
        if max(from_width, from_height) > max_size:
            if from_height > from_width:
                pixmap = pixmap.scaledToHeight(max_size)
            else:
                pixmap = pixmap.scaledToWidth(max_size)
        if min(from_height, from_width) < min_size:
            if from_height > from_width:
                pixmap = pixmap.scaledToWidth(min_size)
            else:
                pixmap = pixmap.scaledToHeight(min_size)
        return pixmap

    @qasync.asyncSlot(QPixmap)
    async def start_ocr(self, no_copy: bool = False, lang='', pixmap: QPixmap = None, action: CaptureAction = None):
        self.capture_widget.hide()
        self.setting.reload()
        default = self.setting.get('General', 'default_backend')
        if default == '':
            default = 'baidu'
        try:
            service = OcrService(default)
            min_size, max_size = service.image_scaling()
            if min_size > 0 or max_size > 0:
                pixmap = self.image_resize(pixmap, min_size, max_size)
            result = await service.basic_general_ocr(self.pixmap_to_bytes(pixmap), lang=lang)
            await service.close()
            data = '\n'.join(result)
            del service
        except Exception as err:
            self.showMessage('OCR 识别异常', str(err), QIcon.fromTheme('dialog-error-symbolic'), 5000)
            return
        if action == CaptureAction.search:
            await open_in_default(f'https://www.google.com/search?q={data.strip()}')
            return
        if no_copy:
            if self.bus is not None:
                self.bus.captured(data)
                self.showMessage('OCR 识别成功', '已发送 DBus 信号', QIcon.fromTheme('object-select-symbolic'), 5000)
            else:
                self.showMessage('OCR 识别成功', '当前平台不支持 DBus', QIcon.fromTheme('object-select-symbolic'), 5000)
        else:
            if self.bus is not None:
                self.bus.captured(data)
            mode = self.setting.general_mode
            if mode == 1:
                self.saved_data = data
                self.showMessage('OCR 识别成功', '点击复制到系统剪切板', QIcon.fromTheme('object-select-symbolic'), 8000)
            else:
                clipboard = qasync.QApplication.clipboard()
                clipboard.setText(data)
                self.showMessage('OCR 识别成功', '已复制到系统剪切板', QIcon.fromTheme('object-select-symbolic'), 5000)

    async def run_capture(self, seconds=.5, no_copy=False, lang=''):
        self.contextMenu().close()
        await asyncio.sleep(seconds)
        if self.capture_widget is None:
            self.capture_widget = CaptureWidget()
        self.capture_widget.captured.connect(partial(self.start_ocr, no_copy, lang))
        self.capture_widget.showFullScreen()

    @qasync.asyncSlot()
    async def start_capture_lang(self, lang, _):
        await self.run_capture(.5, lang=lang)

    @qasync.asyncSlot()
    async def start_capture(self):
        await self.run_capture(.5)
