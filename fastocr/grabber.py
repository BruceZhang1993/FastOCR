import asyncio
import sys
import time
import traceback
from abc import abstractmethod
from asyncio import Task
from enum import Enum
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QScreen
from PyQt6.QtCore import QObject, QRect, QPoint, QDir, pyqtSignal, Qt
from PyQt6.QtGui import QGuiApplication, QPixmap, QKeyEvent, QPaintEvent, QPainter, QColor, QMouseEvent, \
    QRegion
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QPushButton

from fastocr.log import AppLogger
from fastocr.util import DesktopInfo

if DesktopInfo.dbus_supported():
    from dbus_next.aio import MessageBus


class ScreenGrabber(QObject):
    pixmap = None

    async def grab_entire_desktop(self) -> Optional[QPixmap]:
        """
        Grab the entire desktop screenshot to QPixmap
        :return: QPixmap instance or None
        :rtype: Optional[QPixmap]
        """
        if sys.platform == 'linux':
            try:
                return await self.grab_entire_desktop_freedesktop_portal()
            except Exception as e:
                AppLogger().info('DBus screenshot API not working, falling back to Qt: ' + str(e))
                print(traceback.format_exc())
        return self.grab_entire_desktop_qt()

    @staticmethod
    async def grab_entire_desktop_freedesktop_portal() -> Optional[QPixmap]:
        """
        Grab the entire desktop screenshot to QPixmap (Sway implementation)
        :return: QPixmap instance or None
        :rtype: Optional[QPixmap]
        """
        bus = await MessageBus().connect()
        # introspection = await bus.introspect('org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop')
        with (Path(__file__).parent / 'data' / 'introspection.xml').open('r') as f:
            introspection = f.read()
        # noinspection PyTypeChecker
        proxy_object = bus.get_proxy_object('org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop',
                                            introspection)
        interface = proxy_object.get_interface('org.freedesktop.portal.Screenshot')

        response_event = asyncio.Event()

        def response_notify(_, result):
            if 'uri' not in result:
                print('cannot get screenshot result')
                return
            path = result['uri'].value
            ScreenGrabber.pixmap = None
            ScreenGrabber.pixmap = QPixmap()
            ScreenGrabber.pixmap.load(path.replace('file://', ''))
            Path(path.replace('file://', '')).unlink(missing_ok=True)
            response_event.set()

        # noinspection PyUnresolvedReferences
        reply_handle = await interface.call_screenshot('', {})
        introspection1 = await bus.introspect('org.freedesktop.portal.Desktop', reply_handle)
        request_object = bus.get_proxy_object('org.freedesktop.portal.Desktop', reply_handle, introspection1)
        request_interface = request_object.get_interface('org.freedesktop.portal.Request')
        # noinspection PyUnresolvedReferences
        request_interface.on_response(response_notify)
        await response_event.wait()
        # await request_interface.call_close()
        return ScreenGrabber.pixmap

    @staticmethod
    async def grab_entire_desktop_wayland_kde() -> Optional[QPixmap]:
        """
        Grab the entire desktop screenshot to QPixmap (KDE implementation)
        :return: QPixmap instance or None
        :rtype: Optional[QPixmap]
        """
        bus = await MessageBus().connect()
        introspection = await bus.introspect('org.kde.KWin', '/Screenshot')
        proxy_object = bus.get_proxy_object('org.kde.KWin', '/Screenshot',
                                            introspection)
        interface = proxy_object.get_interface('org.kde.kwin.Screenshot')
        # noinspection PyUnresolvedReferences
        reply = await interface.call_screenshot_fullscreen(False)
        if reply:
            res = QPixmap(reply)
        else:
            res = None
        return res

    @staticmethod
    async def grab_entire_desktop_wayland_gnome() -> Optional[QPixmap]:
        """
        Grab the entire desktop screenshot to QPixmap (Gnome implementation)
        :return: QPixmap instance or None
        :rtype: Optional[QPixmap]
        """
        path = QDir.tempPath() + '/tmp_fastocr_screenshot.tmp'
        bus = await MessageBus().connect()
        introspection = await bus.introspect('org.gnome.Shell', '/org/gnome/Shell/Screenshot')
        proxy_object = bus.get_proxy_object('org.gnome.Shell', '/org/gnome/Shell/Screenshot',
                                            introspection)
        interface = proxy_object.get_interface('org.gnome.Shell.Screenshot')
        # noinspection PyUnresolvedReferences
        reply = await interface.call_screenshot(False, False, path)
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
        widget.fast_action()


class SearchButton(BaseToolButton):
    def get_text(self) -> str:
        return 'Web Search'

    def handle(self, widget: 'CaptureWidget'):
        widget.fast_action(CaptureAction.search)


class ToolPanel(QFrame):
    def __init__(self, parent=None):
        super(ToolPanel, self).__init__(parent)
        self._layout: Optional[QHBoxLayout] = None
        self.setup_ui()
        self.setup_tools()

    def setup_ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool |
            Qt.WindowType.BypassWindowManagerHint)
        # self.setFocusPolicy(Qt.WindowType.NoFocus)
        self.setStyleSheet("background-color: transparent;")
        # self.setAttribute(Qt.WindowType.WA_TranslucentBackground)
        self.setWindowOpacity(.8)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

    def setup_tools(self):
        self._layout.addWidget(CloseButton(self, self.parentWidget()))
        self._layout.addWidget(FastCopyButton(self, self.parentWidget()))
        self._layout.addWidget(SearchButton(self, self.parentWidget()))


class CaptureAction(Enum):
    copy = 1
    search = 2


class CaptureWidget(QWidget):
    captured = pyqtSignal(QPixmap, CaptureAction)

    def __init__(self, screen: QScreen):
        """
        CapturedWidget __init__
        """
        super().__init__()
        self._screen = screen
        self.setScreen(self._screen)
        print(self._screen.geometry().x())
        self._task = None
        self.painter = QPainter()
        self.setCursor(Qt.CursorShape.CrossCursor)
        # Make widget stay on top & fullscreen
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool |
            Qt.WindowType.BypassWindowManagerHint)
        self.screenshot = None
        self._clipping_state = 0
        self._startpos: Optional[QPoint] = None
        self._endpos: Optional[QPoint] = None
        self._tool_panel = None

    def on_desktop_grabbed(self, task: 'Task[QPixmap]'):
        self.screenshot = task.result()
        self.screenshot.setDevicePixelRatio(self.devicePixelRatio())
        self.resize(self.screenshot.deviceIndependentSize().toSize())
        self.move(self._screen.geometry().x(), 0)
        self.repaint()
        self.showFullScreen()

    def start_screenshot(self):
        if self._tool_panel is None:
            self._tool_panel = ToolPanel(self)
        self._clipping_state = 0
        self._task = asyncio.get_event_loop().create_task(ScreenGrabber().grab_entire_desktop())
        self._task.add_done_callback(self.on_desktop_grabbed)

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
            self.fast_action()

    def fast_action(self, action=None):
        if action is None:
            action = CaptureAction.copy
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
        self.captured.emit(cropped, action)

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
        if self.screenshot is not None:
            self.painter.begin(self)
            self.painter.drawPixmap(QPoint(0, 0), self.screenshot, QRect(self._screen.geometry().x(), 0, self.screenshot.width(), self.screenshot.height()))
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
