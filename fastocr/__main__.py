import asyncio
import sys

from PySide2.QtWidgets import QApplication
from qasync import QEventLoop

from fastocr.tray import AppTray
from fastocr.util import instance_already_running


def main():
    if instance_already_running():
        print('Only one instance allowed')
        sys.exit(1)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    from fastocr.bus import app_dbus
    app_dbus.tray = AppTray()
    app_dbus.tray.show()
    with loop:
        sys.exit(loop.run_forever())


if __name__ == '__main__':
    main()
