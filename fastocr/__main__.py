import asyncio
import signal
import sys
from functools import partial
from pathlib import Path

import click
import pkg_resources

from fastocr import __appname__
from fastocr.log import AppLogger
from fastocr.util import instance_already_running, DesktopInfo, get_environment_values

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
@click.option('--show-config', '-C', is_flag=True)
def run(show_config: bool):
    from PyQt5.QtWidgets import QApplication
    from qasync import QEventLoop
    from fastocr.i18n import Translation
    from fastocr.tray import AppTray

    if sys.platform not in ['win32', 'darwin', 'cygwin'] and instance_already_running():
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
    for s in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(s, partial(quit_application, s))
    if DesktopInfo.dbus_supported():
        from fastocr.bus import app_dbus
        app_dbus.tray = AppTray(bus=app_dbus)
        app_dbus.tray.show()
        if show_config:
            app_dbus.tray.open_setting()
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
    packages = ['PyQt5', 'aiohttp']
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
