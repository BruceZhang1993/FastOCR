from dbus_next.service import ServiceInterface, signal, method
from dbus_next.aio import MessageBus

import fastocr.tray


class AppDBusInterface(ServiceInterface):
    def __init__(self, tray: 'fastocr.tray.AppTray'):
        super(AppDBusInterface, self).__init__('io.github.brucezhang1993.FastOCR')
        self._tray = tray

    @signal()
    def captured(self, text: 's') -> None:
        pass

    @method(name='captureToClipboard')
    async def capture_to_clipboard(self, seconds: 'd', no_copy: 'b') -> None:
        await self._tray.run_capture(seconds + .5, no_copy)

    @method(name='quitApp')
    def quit_app(self):
        self._tray.quit_app('')

    @staticmethod
    def init(tray: 'fastocr.tray.AppTray') -> 'AppDBusInterface':
        return AppDBusInterface(tray)

    async def run(self):
        bus = await MessageBus().connect()
        bus.export('/io/github/brucezhang1993/FastOCR', self)
        await bus.request_name('io.github.brucezhang1993.FastOCR')
        await bus.wait_for_disconnect()
