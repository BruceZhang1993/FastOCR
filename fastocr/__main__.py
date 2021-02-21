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
    if instance_already_running():
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


if __name__ == '__main__':
    main()
