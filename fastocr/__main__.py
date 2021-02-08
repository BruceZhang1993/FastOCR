import asyncio
import sys

from PySide2.QtWidgets import QApplication
from dbus.mainloop import glib
from qasync import QEventLoop

from fastocr.grabber import CaptureWidget


def main():
    glib.DBusGMainLoop(set_as_default=True)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    w = CaptureWidget()
    w.showFullScreen()
    with loop:
        sys.exit(loop.run_forever())


if __name__ == '__main__':
    main()
