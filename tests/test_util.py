import sys
import pytest

from PyQt5.QtWidgets import QApplication

from fastocr.util import DesktopInfo, get_registry_value, run_command, check_exists, instance_already_running, \
    get_environment_values


class TestUtilQt:
    app: QApplication

    @classmethod
    def setup_class(cls):
        cls.app = QApplication(sys.argv)

    def test_tray_supported(self):
        assert isinstance(DesktopInfo.tray_supported(), bool)
        assert DesktopInfo.tray_supported() is True


class TestUtil:
    def test_environment_variables(self):
        assert isinstance(DesktopInfo.XDG_CURRENT_DESKTOP, str)
        assert isinstance(DesktopInfo.WAYLAND_DISPLAY, str)
        assert isinstance(DesktopInfo.XDG_SESSION_TYPE, str)
        assert isinstance(DesktopInfo.GNOME_DESKTOP_SESSION_ID, str)
        assert isinstance(DesktopInfo.DESKTOP_SESSION, str)
        assert isinstance(DesktopInfo.KDE_FULL_SESSION, str)

    def test_dbus_platforms(self):
        assert isinstance(DesktopInfo.dbus_supported(), bool)

    def test_is_wayland(self):
        assert isinstance(DesktopInfo.is_wayland(), bool)

    def test_desktop_environment(self):
        assert isinstance(DesktopInfo.desktop_environment(), str)
        assert DesktopInfo.desktop_environment() in [DesktopInfo.GNOME, DesktopInfo.KDE, DesktopInfo.SWAY,
                                                     DesktopInfo.OTHER]

    def test_dark_mode_detect(self):
        assert isinstance(DesktopInfo.is_dark_mode(), bool)

    def test_windows_registry(self):
        if sys.platform != 'win32':
            pytest.skip('windows platform only')
        import winreg
        assert get_registry_value(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes'
                                                            r'\Personalize', 'SystemUsesLightTheme')

    @pytest.mark.asyncio
    async def test_commands(self):
        ret = await run_command('echo', 'helloworld', allow_fail=True)
        assert isinstance(ret, tuple)
        assert len(ret) == 3
        assert isinstance(ret[0], str)
        assert isinstance(ret[1], str)
        assert ret[2] is None or isinstance(ret[2], int)

    @pytest.mark.asyncio
    async def test_open_command(self):
        exists = False
        if sys.platform == 'darwin':
            exists = await check_exists('open')
        if sys.platform == 'win32':
            exists = await check_exists('start')
        if sys.platform == 'linux':
            exists = await check_exists('xdg-open')
        exists = exists[1]
        assert isinstance(exists, bool)
        assert exists is True

    def test_instance_not_running(self):
        if sys.platform in ['win32', 'darwin', 'cygwin']:
            pytest.skip('linux only')
        assert instance_already_running('test_label_01') is False

    def test_get_environment_values(self):
        values = get_environment_values()
        assert isinstance(values, dict)
        assert 'System' in values
        assert 'Infomation' in values
        assert 'Python' in values
        assert 'Platform' in values
        assert 'Qt' in values
        assert 'DBus' in values
        if sys.platform not in ['win32', 'darwin', 'cygwin']:
            assert 'Desktop' in values
            assert 'Wayland' in values
