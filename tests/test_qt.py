import sys

import pytest

from PyQt5.QtWidgets import QApplication
from qasync import QEventLoop

from fastocr.util import DesktopInfo


class TestUtilQt:
    @pytest.fixture(scope='session')
    def event_loop(self):
        app = QApplication(sys.argv)
        loop = QEventLoop(app)
        yield loop
        loop.close()

    @pytest.mark.asyncio
    def test_tray_supported(self, event_loop):
        assert isinstance(DesktopInfo.tray_supported(), bool)
