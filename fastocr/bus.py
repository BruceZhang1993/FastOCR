import asyncio
from typing import Optional, Any

import dbus
import dbus.service
import dbus.mainloop.glib


# noinspection PyPep8Naming
class AppDBusObject(dbus.service.Object):
    INTERFACE = 'io.github.brucezhang1993.FastOCR'
    _instance = None

    def __init__(self, conn=None, object_path=None, bus_name=None):
        super().__init__(conn, object_path, bus_name)
        self.tray: Optional[Any] = None
        self.session_bus: Optional[dbus.SessionBus] = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.run()
        return cls._instance

    @staticmethod
    def run():
        # noinspection PyUnresolvedReferences
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(AppDBusObject.INTERFACE, session_bus)
        obj = AppDBusObject(session_bus, '/' + AppDBusObject.INTERFACE.replace('.', '/'), bus_name)
        obj.session_bus = session_bus
        return obj

    @dbus.service.method(INTERFACE, in_signature='d', out_signature='')
    def captureToClipboard(self, seconds: float):
        asyncio.gather(self.tray.run_capture(seconds + .5))

    @dbus.service.method(INTERFACE, in_signature='', out_signature='')
    def quitApp(self):
        self.tray.quit_app('')


app_dbus = AppDBusObject.instance()
