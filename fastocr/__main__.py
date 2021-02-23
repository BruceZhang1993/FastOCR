import asyncio
import sys
from pathlib import Path

import click
import pkg_resources
from PySide2.QtWidgets import QApplication
from qasync import QEventLoop

from fastocr import __appname__
from fastocr.i18n import Translation
from fastocr.tray import AppTray
from fastocr.util import instance_already_running, DesktopInfo

__version__ = pkg_resources.get_distribution('fastocr').version


def print_version(ctx, _, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f'{__appname__} - Version {__version__}')
    ctx.exit()


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True)
@click.pass_context
def main(ctx):
    if ctx.invoked_subcommand is None:
        run()


@main.command()
def run():
    if sys.platform not in ['win32', 'darwin', 'cygwin'] and instance_already_running():
        print('Only one instance allowed')
        sys.exit(1)
    app = QApplication(sys.argv)
    Translation().load().install(app)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    if DesktopInfo.dbus_supported():
        from fastocr.bus import app_dbus
        app_dbus.tray = AppTray(bus=app_dbus)
        app_dbus.tray.show()
    else:
        tray = AppTray()
        tray.show()
    with loop:
        sys.exit(loop.run_forever())


@main.command()
@click.argument('formation', type=click.Choice(['desktop', 'config']), required=True)
def generate(formation):
    if formation == 'desktop':
        path = Path(__file__).parent / 'data' / 'FastOCR.desktop'
        with path.open('r') as f:
            print(f.read())
    elif formation == 'config':
        path = Path(__file__).parent / 'data' / 'config.example.ini'
        with path.open('r') as f:
            print(f.read())


@main.command()
def diagnose():
    # Application
    print('== Application ==')
    print(f'Version: {__version__}')
    print(f'File: {__file__}')
    print(f'Running: {instance_already_running()}')
    print()
    # Environment
    print('== Environment ==')
    import platform, PySide2.QtCore
    _version = sys.version.replace('\n', ' ')
    print(f'System: {platform.system()} {platform.version()}')
    print(f'Info: {" ".join(platform.uname())}')
    print(f'Python: {_version}')
    print(f'Platform: {sys.platform}')
    # noinspection PyUnresolvedReferences
    print(f'PySide2 Qt: {PySide2.QtCore.__version__}')
    print(f'Running Qt: {PySide2.QtCore.qVersion()}')
    print(f'DBus: {DesktopInfo.dbus_supported()}')
    if sys.platform not in ['win32', 'darwin', 'cygwin']:
        print(f'Desktop: {DesktopInfo.desktop_environment()}')
        print(f'Wayland: {DesktopInfo.is_wayland()}')
    print()

    # Dependency
    packages = ['PySide2', 'shiboken2', 'aiohttp']
    if sys.platform not in ['win32', 'darwin', 'cygwin']:
        packages.append('dbus')
    for p in packages:
        print_package_info(p)


def print_package_info(package_name):
    try:
        print(f'== {package_name} ==')
        package = __import__(package_name)
        print(f'Name: {package.__name__}')
        print(f'Version: {package.__version__}')
        print(f'Package: {package.__package__}')
        print(f'File: {package.__file__}')
        print(f'Path: {package.__path__}')
        print()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
