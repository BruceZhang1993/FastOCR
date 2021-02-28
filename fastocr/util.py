import asyncio
import os
import sys


class Singleton(type):
    """ singleton metaclass """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DesktopInfo:
    GNOME = 'gnome'
    KDE = 'kde'
    SWAY = 'sway'
    OTHER = 'other'

    XDG_CURRENT_DESKTOP = os.environ.get('XDG_CURRENT_DESKTOP', '')
    WAYLAND_DISPLAY = os.environ.get('WAYLAND_DISPLAY', '')
    XDG_SESSION_TYPE = os.environ.get('XDG_SESSION_TYPE', '')
    GNOME_DESKTOP_SESSION_ID = os.environ.get('GNOME_DESKTOP_SESSION_ID', '')
    DESKTOP_SESSION = os.environ.get('DESKTOP_SESSION', '')
    KDE_FULL_SESSION = os.environ.get('KDE_FULL_SESSION', '')

    @staticmethod
    def dbus_supported():
        return sys.platform not in ['win32', 'darwin', 'cygwin']

    @staticmethod
    def is_wayland():
        return DesktopInfo.XDG_SESSION_TYPE == 'wayland' \
               or 'wayland' in DesktopInfo.WAYLAND_DISPLAY.lower()

    @staticmethod
    def desktop_environment():
        ret = DesktopInfo.OTHER
        if 'gnome' in DesktopInfo.XDG_CURRENT_DESKTOP.lower() \
                or DesktopInfo.GNOME_DESKTOP_SESSION_ID != '':
            ret = DesktopInfo.GNOME
        elif DesktopInfo.KDE_FULL_SESSION != '' \
                or DesktopInfo.DESKTOP_SESSION.lower() == 'kde-plasma':
            ret = DesktopInfo.KDE
        elif 'sway' in DesktopInfo.XDG_CURRENT_DESKTOP.lower():
            ret = DesktopInfo.SWAY
        return ret

    @staticmethod
    async def is_dark_mode():
        if sys.platform == 'darwin':
            # macOS darkmode
            out, _, __ = await run_command('defaults', 'read', '-g', 'AppleInterfaceStyle', allow_fail=True)
            if out.strip().lower() == 'dark':
                return True
            else:
                return False
        elif sys.platform == 'win32':
            # Windows 10 darkmode
            try:
                import winreg
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                regpath = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
                try:
                    regkey = winreg.OpenKey(registry, regpath)
                except:
                    return False
                for i in range(1024):
                    try:
                        value_name, value, _ = winreg.EnumValue(regkey, i)
                        if value_name == 'SystemUsesLightTheme':
                            return value == 0
                    except OSError:
                        break
                return False
            except:
                return False
        else:
            # Qt darkmode
            from PyQt5.QtWidgets import QApplication
            palette = QApplication.palette()
            back_color = palette.color(palette.Normal, palette.Window)
            lightness = back_color.lightness()
            return lightness <= 160


async def check_exists(command):
    _, __, returncode = await run_command('which', command, allow_fail=True)
    return command, returncode == 0


async def run_command(*args, allow_fail=False):
    process = await asyncio.create_subprocess_exec(
        *args,
        stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    if not allow_fail and process.returncode != 0:
        raise Exception(stderr.decode().strip())
    return stdout.decode().strip(), stderr.decode().strip(), process.returncode


async def open_in_default(filename):
    if sys.platform == 'darwin':
        await run_command('open', filename)
    if sys.platform == 'win32':
        await run_command('start', filename)
    if sys.platform == 'linux':
        await run_command('xdg-open', filename)


def instance_already_running(label="default"):
    """
    Detect if an an instance with the label is already running, globally
    at the operating system level.
    """
    import fcntl
    lock_file_pointer = os.open(f"/tmp/fastocr_{label}.lock", os.O_WRONLY | os.O_CREAT)

    try:
        fcntl.lockf(lock_file_pointer, fcntl.LOCK_EX | fcntl.LOCK_NB)
        already_running = False
    except IOError:
        already_running = True

    return already_running
