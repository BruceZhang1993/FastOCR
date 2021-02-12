import asyncio
from pathlib import Path
from typing import Optional

import qasync
from PySide2.QtCore import QByteArray, QBuffer, QIODevice
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtWidgets import QSystemTrayIcon, QMenu, QApplication

from fastocr.grabber import CaptureWidget
from fastocr.service import OcrService
from fastocr.util import open_in_default


class AppTray(QSystemTrayIcon):
    def __init__(self):
        super(AppTray, self).__init__()
        self.capture_widget: Optional[CaptureWidget] = None
        self.initialize()

    # noinspection PyUnresolvedReferences
    def initialize(self):
        self.setIcon(QIcon.fromTheme('edit-find-symbolic'))
        self.setContextMenu(QMenu())
        context_menu = self.contextMenu()
        capture_action = context_menu.addAction('Capture')
        setting_action = context_menu.addAction('Setting')
        quit_action = context_menu.addAction('Quit')
        capture_action.triggered.connect(self.start_capture)
        setting_action.triggered.connect(self.open_setting)
        quit_action.triggered.connect(self.quit_app)

    @qasync.asyncSlot()
    async def open_setting(self):
        setting_dir = Path.home() / '.config' / 'FastOCR'
        setting_dir.mkdir(parents=True, exist_ok=True)
        setting_file = setting_dir / 'config.ini'
        if not setting_file.exists():
            setting_file.touch()
        await open_in_default(setting_file.as_posix())

    def quit_app(self, _):
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
    async def start_ocr(self, pixmap: QPixmap):
        self.capture_widget.close()
        result = OcrService().basic_general_ocr(self.pixmap_to_bytes(pixmap))
        data = '\n'.join([w_.get('words', '') for w_ in result.get('words_result', [])])
        clipboard = qasync.QApplication.clipboard()
        clipboard.setText(data)
        self.showMessage('OCR 识别成功', '已复制到系统剪切板', QIcon.fromTheme('object-select-symbolic'), 5000)

    async def run_capture(self, seconds=.5):
        self.contextMenu().close()
        await asyncio.sleep(seconds)
        self.capture_widget = CaptureWidget()
        self.capture_widget.captured.connect(self.start_ocr)
        self.capture_widget.showFullScreen()

    @qasync.asyncSlot()
    async def start_capture(self):
        await self.run_capture(.5)
