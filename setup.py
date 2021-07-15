# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
    ['fastocr']

package_data = \
    {'': ['*'],
     'fastocr': ['data/*',
                 'i18n/*',
                 'qml/*',
                 'qml/component/*',
                 'qml/dummydata/*',
                 'resource/icon/dark/*',
                 'resource/icon/light/*']}

install_requires = \
    ['PyQt5', 'PyQt5-sip', 'aiohttp', 'click', 'qasync']

extras_require = \
    {'linux': ['dbus-python']}

entry_points = \
    {'console_scripts': ['fastocr = fastocr.__main__:main']}

setup_kwargs = {
    'name': 'fastocr',
    'version': '0.3.3',
    'description': 'FastOCR is a desktop application for OCR API.',
    'long_description': '# FastOCR\n\n[![GitHub top language](https://img.shields.io/github/languages/top/BruceZhang1993/FastOCR?style=flat-square)](https://github.com/BruceZhang1993/FastOCR/search?l=python)\n[![GitHub](https://img.shields.io/github/license/BruceZhang1993/FastOCR?style=flat-square)](https://github.com/BruceZhang1993/FastOCR/blob/master/LICENSE)\n[![GitHub version](https://img.shields.io/github/v/tag/BruceZhang1993/FastOCR?label=Version&style=flat-square)](https://github.com/BruceZhang1993/FastOCR/releases)\n\nFastOCR is a desktop application for OCR API.\n\n## Supported OCR API\n\n- 百度 AI 文字识别服务  https://ai.baidu.com/tech/ocr\n- 有道文字识别服务  https://ai.youdao.com/product-ocr-print.s\n- 旷视 Face++ 文字识别服务 (Experimental)  https://www.faceplusplus.com.cn/general-text-recognition/\n\n### Features\n\n- 通用文字识别\n- 多语言支持 / Baidu\n- 高精度接口支持 / Baidu\n\n## Supported environment\n\n- Linux X11\n- Windows\n- macOS\n- Linux Wayland (Experimental)\n\n### Supported wayland environment\n\n- Gnome Wayland\n- KDE Wayland\n- Sway\n\n## Installation\n\n### Arch Linux\n\nStable version: https://aur.archlinux.org/packages/fastocr\n\nGit version: https://aur.archlinux.org/packages/fastocr-git\n\nBuild from AUR or install with your favorite AUR helper.\n\n```shell\nyay -S fastocr  # Using yay\npikaur -S fastocr  # Using pikaur\n# ...\n```\n\n### Nix/NixOS\n \nUse [NixOS CN flakes](https://github.com/nixos-cn/flakes) or [berberman flakes](https://github.com/berberman/flakes)\n\nRun FastOCR\n\n```shell\nnix run github:berberman/flakes#fastocr\n```\n\n\n### PyPI\n\n[fastocr @ PyPI](https://pypi.org/project/fastocr/)\n\n```shell\npip install --user fastocr\n# Then copy desktop file to ~/.local/share/applications\n```\n\n### Manually\n\nProudly use [DepHell](https://dephell.readthedocs.io/) to generate\nsetup.py file.\n\n```shell\npython setup.py install\n# Then copy desktop file to ~/.local/share/applications\n```\n\n## Development\n\nProudly use [Poetry](https://python-poetry.org/docs/) for developing.\n\n```shell\npoetry install\n```\n\n## Usage\n\n```shell\nfastocr\n```\n\n## DBus\n\nService name: `io.github.brucezhang1993.FastOCR`\n\nObject: `/io/github/brucezhang1993/FastOCR`\n\n### Methods\n\n| Actions            | Arguments           | Description                                                 |\n|:-------------------|:--------------------|:------------------------------------------------------------|\n| captureToClipboard | {seconds} {no_copy} | Capture and OCR to system clipboard or dbus signal          |\n|                    |                     | seconds: Delay capture in seconds                           |\n|                    |                     | no_copy: If true, the result will not be saved in clipboard |\n| quitApp            | --                  | Quit app                                                    |\n\n### Signal\n\n| Signals  | Arguments | Description                            |\n|:---------|:----------|:---------------------------------------|\n| captured | {text}    | OCR result will be sent to this signal |\n|          |           | text: OCR result in plain text         |\n\n## Contributing\n\nPull requests are welcome.\n\nFor major changes, please open an issue first to discuss what you would\nlike to change.\n\n## License\n\nLGPL3\n',
    'author': 'Bruce Zhang',
    'author_email': 'zttt183525594@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/BruceZhang1993/FastOCR',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}

setup(**setup_kwargs)
