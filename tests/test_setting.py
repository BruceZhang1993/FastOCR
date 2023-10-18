from pathlib import Path

from fastocr.consts import APP_CONFIG_DIR
from fastocr.setting import Setting

MOCKED_APP_SETTING_FILE = APP_CONFIG_DIR / 'mocked_config.ini'


class TestSetting:
    def setup_method(self):
        self._instance = Setting(MOCKED_APP_SETTING_FILE)

    def teardown_method(self):
        self._instance.setting_file.unlink(missing_ok=True)

    def test_get_file(self):
        path = self._instance.get_config_file()
        assert isinstance(path, Path)
        assert path.exists() is True
        assert path.name == 'mocked_config.ini'

    def test_sections(self):
        assert self._instance.loaded is False
        sections = self._instance.sections()
        assert isinstance(sections, list)
        if len(sections) > 0:
            assert isinstance(sections[0], str)
        assert self._instance.loaded is True
