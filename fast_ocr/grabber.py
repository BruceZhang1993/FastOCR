import sys
from typing import Optional

from PySide2.QtCore import QObject, QRect, QPoint, Signal, QByteArray, QBuffer, QIODevice
from PySide2.QtGui import QGuiApplication, QScreen, QPixmap, QKeyEvent, Qt, QPaintEvent, QPainter, QColor, QMouseEvent, \
    QRegion
from PySide2.QtWidgets import QApplication, QWidget
from qasync import asyncSlot

from fast_ocr.service import OcrService
from fast_ocr.util import check_exists, run_command


class ScreenGrabber(QObject):
    def grab_entire_desktop(self) -> Optional[QPixmap]:
        if sys.platform == 'linux':
            return self.grab_entire_desktop_x11()
        return None

    @staticmethod
    def grab_entire_desktop_x11() -> QPixmap:
        geo = QRect()
        for screen in QGuiApplication.screens():
            screen: QScreen
            src_rect = screen.geometry()
            src_rect.moveTo(int(src_rect.x() / screen.devicePixelRatio()),
                            int(src_rect.y() / screen.devicePixelRatio()))
            geo = geo.united(src_rect)
        pixmap = QApplication.primaryScreen().grabWindow(
            QApplication.desktop().winId(),
            geo.x(),
            geo.y(),
            geo.width(),
            geo.height()
        )
        screen_no = QApplication.desktop().screenNumber()
        screen = QApplication.screens()[screen_no]
        pixmap.setDevicePixelRatio(screen.devicePixelRatio())
        return pixmap


class CaptureWidget(QWidget):
    captured = Signal(QPixmap)

    def __init__(self):
        super().__init__()
        self.painter = QPainter()
        self.setCursor(Qt.CrossCursor)
        self.setWindowState(Qt.WindowFullScreen)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool | Qt.BypassWindowManagerHint)
        self.screenshot = ScreenGrabber().grab_entire_desktop()
        self._clipping_state = 0
        self._startpos: Optional[QPoint] = None
        self._endpos: Optional[QPoint] = None
        self.move(0, 0)
        self.resize(self.screenshot.size())
        # noinspection PyUnresolvedReferences
        self.captured.connect(self.start_ocr)

    @staticmethod
    def pixmap_to_bytes(pixmap: QPixmap) -> bytes:
        ba = QByteArray()
        bf = QBuffer(ba)
        bf.open(QIODevice.WriteOnly)
        ok = pixmap.save(bf, 'PNG')
        assert ok
        return ba.data()

    @asyncSlot(QPixmap)
    async def start_ocr(self, pixmap: QPixmap):
        result = OcrService().basic_general_ocr(self.pixmap_to_bytes(pixmap))
        data = '\n'.join([w_.get('words', '') for w_ in result.get('words_result', [])])
        clipboard = QApplication.clipboard()
        clipboard.setText(data)
        _, ok = await check_exists('notify-send')
        if ok:
            arguments = ['-u', 'normal', '-t', '5000', '-a', 'FastOCR', '-i', 'Finished', 'OCR 识别成功', '已复制到系统剪切板']
            await run_command('notify-send', *arguments, allow_fail=True)
        self.close()
        QApplication.quit()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Escape:
            self.close()
            QApplication.quit()
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self._startpos is None or self._endpos is None:
                return
            screen = QApplication.screenAt(self._startpos)
            ratio = screen.devicePixelRatio()
            cropped = self.screenshot.copy(QRect(
                self._startpos.x() * ratio,
                self._startpos.y() * ratio,
                (self._endpos.x() - self._startpos.x()) * ratio,
                (self._endpos.y() - self._startpos.y()) * ratio,
            ))
            # noinspection PyUnresolvedReferences
            self.captured.emit(cropped)

    def mousePressEvent(self, event: QMouseEvent):
        self._clipping_state = 1
        self._startpos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._clipping_state != 1:
            return
        self._endpos = event.pos()
        self.repaint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._clipping_state = 2
        self._endpos = event.pos()
        self.repaint()

    def paintEvent(self, event: QPaintEvent):
        self.painter.begin(self)
        self.painter.drawPixmap(0, 0, self.screenshot)
        overlay = QColor(0, 0, 0, 120)
        self.painter.setBrush(overlay)
        grey = QRegion(self.rect())
        if self._clipping_state != 0:
            grey = grey.subtracted(QRegion(
                self._startpos.x(),
                self._startpos.y(),
                self._endpos.x() - self._startpos.x(),
                self._endpos.y() - self._startpos.y()
            ))
        self.painter.setClipRegion(grey)
        self.painter.drawRect(0, 0, self.rect().width(), self.rect().height())
        self.painter.setClipRegion(self.rect())
        self.painter.end()
