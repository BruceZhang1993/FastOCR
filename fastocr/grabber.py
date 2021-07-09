import sys
from abc import ABCMeta, abstractmethod
from typing import Optional

from PyQt5.QtCore import QObject, QRect, QPoint, QDir, pyqtSignal, Qt
from PyQt5.QtGui import QGuiApplication, QPixmap, QKeyEvent, QPaintEvent, QPainter, QColor, QMouseEvent, \
    QRegion
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QPushButton

from fastocr.util import DesktopInfo

if DesktopInfo.dbus_supported():
    from fastocr.bus import app_dbus


class ScreenGrabber(QObject):
    def grab_entire_desktop(self) -> Optional[QPixmap]:
        """
        Grab the entire desktop screenshot to QPixmap
        :return: QPixmap instance or None
        :rtype: Optional[QPixmap]
        """
        if sys.platform == 'linux':
            if DesktopInfo.is_wayland():
                # Implements screenshot on wayland linux
                try:
                    if DesktopInfo.desktop_environment() == DesktopInfo.GNOME:
                        return self.grab_entire_desktop_wayland_gnome()
                    if DesktopInfo.desktop_environment() == DesktopInfo.KDE:
                        return self.grab_entire_desktop_wayland_kde()
                    if DesktopInfo.desktop_environment() == DesktopInfo.SWAY:
                        return self.grab_entire_desktop_wayland_sway()
                except Exception as e:
                    print(e)
        return self.grab_entire_desktop_qt()

    @staticmethod
    def grab_entire_desktop_wayland_sway() -> Optional[QPixmap]:
        """
        Grab the entire desktop screenshot to QPixmap (Sway implementation)
        :return: QPixmap instance or None
        :rtype: Optional[QPixmap]
        """
        bus = app_dbus.session_bus
        obj = bus.get_object('org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop')
        reply = obj.get_dbus_method('Screenshot', 'org.freedesktop.portal.Screenshot')('', {})
        if reply:
            res = QPixmap(reply)
        else:
            res = None
        return res

    @staticmethod
    def grab_entire_desktop_wayland_kde() -> Optional[QPixmap]:
        """
        Grab the entire desktop screenshot to QPixmap (KDE implementation)
        :return: QPixmap instance or None
        :rtype: Optional[QPixmap]
        """
        bus = app_dbus.session_bus
        obj = bus.get_object('org.kde.KWin', '/Screenshot')
        reply = obj.get_dbus_method('screenshotFullscreen')()
        if reply:
            res = QPixmap(reply)
        else:
            res = None
        return res

    @staticmethod
    def grab_entire_desktop_wayland_gnome() -> Optional[QPixmap]:
        """
        Grab the entire desktop screenshot to QPixmap (Gnome implementation)
        :return: QPixmap instance or None
        :rtype: Optional[QPixmap]
        """
        bus = app_dbus.session_bus
        path = QDir.tempPath() + '/tmp_fastocr_screenshot.tmp'
        obj = bus.get_object('org.gnome.Shell', '/org/gnome/Shell/Screenshot')
        reply = obj.get_dbus_method('Screenshot', 'org.gnome.Shell.Screenshot')(False, False, path)
        if reply:
            res = QPixmap(path)
        else:
            res = None
        return res

    @staticmethod
    def grab_entire_desktop_qt() -> QPixmap:
        """
        Grab the entire desktop screenshot to QPixmap (Qt default implementation)
        :return: QPixmap instance or None
        :rtype: QPixmap
        """
        geo = QRect()
        for screen in QGuiApplication.screens():
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


class BaseToolButton(QPushButton):
    def __init__(self, parent=None, widget=None):
        super(BaseToolButton, self).__init__(parent=parent)
        self._capture_widget: CaptureWidget = widget
        self.setText(self.get_text())
        self.setStyleSheet(
            "QPushButton { background-color: #06b9d4; color: #ffffff; font-weight: 500; border: 0; padding: 5px 15px; "
            "font-size: 12px;}"
            "QPushButton:hover { background-color: #05a8be; color: #ffffff; }"
            "QPushButton:pressed { background-color: #05a8be; color: #ffffff; }")
        # noinspection PyUnresolvedReferences
        self.clicked.connect(self.click_triggered)

    def click_triggered(self, _):
        self.handle(self._capture_widget)

    @abstractmethod
    def get_text(self) -> str:
        pass

    @abstractmethod
    def handle(self, widget: 'CaptureWidget'):
        pass


class CloseButton(BaseToolButton):
    def get_text(self) -> str:
        return 'Close'

    def handle(self, widget: 'CaptureWidget'):
        widget._tool_panel.hide()
        widget.close()


class FastCopyButton(BaseToolButton):
    def get_text(self) -> str:
        return 'Copy'

    def handle(self, widget: 'CaptureWidget'):
        widget.fast_copy()


class ToolPanel(QFrame):
    def __init__(self, parent=None):
        super(ToolPanel, self).__init__(parent)
        self._layout: Optional[QHBoxLayout] = None
        self.setup_ui()
        self.setup_tools()

    def setup_ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool |
            Qt.BypassWindowManagerHint)
        self.setFocusPolicy(Qt.NoFocus)
        self.setStyleSheet("background-color: transparent;")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(.8)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

    def setup_tools(self):
        self._layout.addWidget(CloseButton(self, self.parentWidget()))
        self._layout.addWidget(FastCopyButton(self, self.parentWidget()))
        # self._layout.addWidget(QPushButton('Search Text', self))


class CaptureWidget(QWidget):
    captured = pyqtSignal(QPixmap)

    def __init__(self):
        """
        CapturedWidget __init__
        """
        super().__init__()
        self.painter = QPainter()
        self.setCursor(Qt.CursorShape.CrossCursor)
        # Make widget stay on top & fullscreen
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool |
            Qt.BypassWindowManagerHint)
        self.screenshot = ScreenGrabber().grab_entire_desktop()
        self._clipping_state = 0
        self._startpos: Optional[QPoint] = None
        self._endpos: Optional[QPoint] = None
        self._tool_panel = ToolPanel(self)
        self.move(0, 0)
        self.resize(self.screenshot.size())

    def keyPressEvent(self, event: QKeyEvent):
        """
        Keypress event
        This allows capture widget escape to close, return or enter to capture
        :param event: QKeyEvent instance
        :type event: QKeyEvent
        """
        if event.key() == Qt.Key.Key_Escape:
            self._tool_panel.hide()
            self.close()
        if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.fast_copy()

    def fast_copy(self):
        self._tool_panel.hide()
        if self._startpos is None or self._endpos is None:
            return
        screen = QApplication.screenAt(self._startpos)
        ratio = screen.devicePixelRatio()
        cropped = self.screenshot.copy(QRect(
            int(self._startpos.x() * ratio),
            int(self._startpos.y() * ratio),
            int((self._endpos.x() - self._startpos.x()) * ratio),
            int((self._endpos.y() - self._startpos.y()) * ratio),
        ))
        # noinspection PyUnresolvedReferences
        self.captured.emit(cropped)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Mouse press event, this marks capture start
        :param event: QMouseEvent instance
        :type event: QMouseEvent
        """
        self._clipping_state = 1
        self._startpos = event.pos()
        self._tool_panel.hide()

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        Mouse move event, this marks capture area
        :param event: QMouseEvent instance
        :type event: QMouseEvent
        """
        if self._clipping_state != 1:
            return
        self._endpos = event.pos()
        self.repaint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Mouse release event, this marks capture stop
        :param event: QMouseEvent instance
        :type event: QMouseEvent
        """
        self._clipping_state = 2
        self._endpos = event.pos()
        self.repaint()
        self.show_panel_at_mouse()

    def show_panel_at_mouse(self):
        self._tool_panel.show()
        pos_x = self._endpos.x() - self._tool_panel.width()
        pos_y = self._endpos.y() + 4
        # TODO: potentially move out of screen
        self._tool_panel.move(pos_x, pos_y)

    def paintEvent(self, event: QPaintEvent):
        """
        Paint event, draw cropped area
        :param event: QPaintEvent instance
        :type event: QPaintEvent
        """
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
        self.painter.setClipRegion(QRegion(self.rect()))
        self.painter.end()
