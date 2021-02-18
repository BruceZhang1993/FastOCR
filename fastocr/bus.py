import asyncio
from typing import Optional

import dbus
import dbus.mainloop.glib
import dbus.service

import fastocr.tray


# noinspection PyPep8Naming
class AppDBusObject(dbus.service.Object):
    INTERFACE = 'io.github.brucezhang1993.FastOCR'
    _instance = None

    def __init__(self, conn=None, object_path=None, bus_name=None):
        super().__init__(conn, object_path, bus_name)
        self.tray: Optional['fastocr.tray.AppTray'] = None
        self.session_bus: Optional[dbus.SessionBus] = None

    @classmethod
    def instance(cls) -> 'AppDBusObject':
        """
        AppDBusObject single instance
        :return: AppDBusObject instance
        :rtype: AppDBusObject
        """
        if cls._instance is None:
            cls._instance = cls.run()
        return cls._instance

    @staticmethod
    def run() -> 'AppDBusObject':
        """
        Run DBus mainloop
        :return: AppDBusObject instance
        :rtype: AppDBusObject
        """
        # noinspection PyUnresolvedReferences
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        session_bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(AppDBusObject.INTERFACE, session_bus)
        obj = AppDBusObject(session_bus, '/' + AppDBusObject.INTERFACE.replace('.', '/'), bus_name)
        obj.session_bus = session_bus
        return obj

    @dbus.service.signal(INTERFACE, signature='s')
    def captured(self, text):
        """
        DBus signal: captured
        Receive captured text recognized by OCR
        :param text: captured text
        :type text: str
        """
        pass

    @dbus.service.method(INTERFACE, in_signature='db', out_signature='')
    def captureToClipboard(self, seconds, no_copy):
        """
        DBus method: captureToClipboard
        :param seconds: seconds for delayed capture
        :type seconds: float
        :param no_copy: set True to not update clipboard
        :type no_copy: bool
        """
        asyncio.gather(self.tray.run_capture(seconds + .5, no_copy))

    @dbus.service.method(INTERFACE, in_signature='', out_signature='')
    def quitApp(self):
        """
        DBus method: quitApp
        """
        self.tray.quit_app('')


app_dbus = AppDBusObject.instance()
