import asyncio
import os
import platform
import signal
import sys
from functools import partial
from pathlib import Path

import click

from fastocr import __appname__
from fastocr.log import AppLogger
from fastocr.util import instance_already_running, DesktopInfo, get_environment_values

if sys.version_info.major == 3 and sys.version_info.minor >= 11:
    from importlib import metadata

    __version__ = metadata.version('fastocr')
else:
    import pkg_resources

    __version__ = pkg_resources.get_distribution('fastocr').version


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_exception


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
@click.option('--show-config', '-C', is_flag=True)
def run(show_config: bool):
    if sys.platform == 'win32':
        os.environ['QT_QUICK_CONTROLS_STYLE'] = 'Universal'
    elif sys.platform == 'darwin':
        os.environ['QT_QUICK_CONTROLS_STYLE'] = 'macOS'
    else:
        os.environ['QT_QUICK_CONTROLS_STYLE'] = 'Material'

    from PyQt6.QtWidgets import QApplication
    from qasync import QEventLoop
    from fastocr.i18n import Translation
    from fastocr.tray import AppTray

    if instance_already_running():
        AppLogger().info('only one instance running allowed')
        sys.exit(1)

    def quit_application(code):
        QApplication.quit()
        sys.exit(code)

    app = QApplication(sys.argv)
    Translation().load().install(app)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    loop = asyncio.get_event_loop()
    if sys.platform != 'win32':
        # add_signal_handler is not available on Windows
        for s in [signal.SIGINT, signal.SIGTERM]:
            loop.add_signal_handler(s, partial(quit_application, s))
    if DesktopInfo.dbus_supported():
        from fastocr.bus import AppDBusInterface
        tray = AppTray()
        bus = AppDBusInterface.init(tray)
        loop.create_task(bus.run()).add_done_callback(lambda _: print('DBus service stopped'))
        tray.bus = bus
        tray.show()
        if show_config:
            tray.open_setting()
    else:
        tray = AppTray()
        tray.show()
        if show_config:
            tray.open_setting()
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
    if sys.platform not in ['win32', 'darwin', 'cgywin']:
        print(f'Running: {instance_already_running()}')
    print()
    # Environment
    print('== Environment ==')
    values = get_environment_values()
    for k, v in values.items():
        print(f'{k}: {v}')
    print()
    # Dependency
    packages = ['PyQt6', 'aiohttp']
    if sys.platform not in ['win32', 'darwin', 'cygwin']:
        packages.append('dbus')
    for p in packages:
        print_package_info(p)


def print_package_info(package_name):
    try:
        print(f'== {package_name} ==')
        package = __import__(package_name)
        print(f'Name: {package.__name__}')
        if hasattr(package, '__version__'):
            print(f'Version: {package.__version__}')
        print(f'Package: {package.__package__}')
        print(f'File: {package.__file__}')
        print(f'Path: {package.__path__}')
        print()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
