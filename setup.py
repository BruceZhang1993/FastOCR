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
['PyQt5', 'aiohttp', 'click', 'qasync']

extras_require = \
{':sys_platform == "linux"': ['dbus-next']}

entry_points = \
{'console_scripts': ['fastocr = fastocr.__main__:main']}

setup_kwargs = {
    'name': 'fastocr',
    'version': '0.3.7',
    'description': 'FastOCR is a desktop application for OCR API.',
    'long_description': '# FastOCR\n\n[![GitHub top language](https://img.shields.io/github/languages/top/BruceZhang1993/FastOCR?style=flat-square)](https://github.com/BruceZhang1993/FastOCR/search?l=python)\n[![GitHub](https://img.shields.io/github/license/BruceZhang1993/FastOCR?style=flat-square)](https://github.com/BruceZhang1993/FastOCR/blob/master/LICENSE)\n[![GitHub version](https://img.shields.io/github/v/tag/BruceZhang1993/FastOCR?label=Version&style=flat-square)](https://github.com/BruceZhang1993/FastOCR/releases)\n![PyPI](https://img.shields.io/pypi/v/fastocr?style=flat-square)\n\nFastOCR 是一款开源免费的提供在线 OCR 文字识别的桌面工具\n\n## 支持的 OCR API 后端\n\n- [x] 百度 AI 文字识别服务  https://ai.baidu.com/tech/ocr\n- [x] 有道文字识别服务  https://ai.youdao.com/product-ocr-print.s\n- [x] 旷视 Face++ 文字识别服务 (Experimental)  https://www.faceplusplus.com.cn/general-text-recognition/\n- [ ] 本地 OCR\n\n### 特性\n\n- [x] 通用文字识别 / 多个在线 OCR API 支持\n- [x] 多语言支持 / 百度\n- [x] 高精度接口支持 / 百度\n- [x] 识别文字搜索\n- [ ] 本地 OCR 后端\n- [ ] 自定义快捷动作\n\n## 支持操作系统\n\n- Linux X11\n- Windows\n- macOS (Experimental)\n- Linux Wayland (Experimental)\n\n### 支持的 Wayland 环境 (Linux)\n\n- Gnome Wayland\n- KDE Wayland\n- Sway\n\n## 安装\n\n### Windows  \n 64 位预编译版，解压即可使用\n\n点击下载 -> [Download](https://github.com/BruceZhang1993/FastOCR/releases/latest) 解压到安装目录，执行 FastOCR.exe\n\n### macOS\n\n理论上支持但无构建环境，打包过程类似 Windows 如下，生成的文件位于项目的 dist 目录下\n\n```shell\npip install poetry\npoetry update\npoetry run pyinstaller build.spec\n```\n\n### Arch Linux\n\n稳定版本 https://aur.archlinux.org/packages/fastocr\n\n开发版本 https://aur.archlinux.org/packages/fastocr-git\n\n 从 AUR 下载脚本编译或使用你喜欢的 AUR 辅助工具\n\n```shell\nyay -S fastocr  # 使用 yay\npikaur -S fastocr  # 使用 pikaur\n```\n\n### Nix/NixOS\n \n使用 [NixOS CN flakes](https://github.com/nixos-cn/flakes) 或 [berberman flakes](https://github.com/berberman/flakes) 安装\n\n```shell\nnix run github:berberman/flakes#fastocr\n```\n\n### 通用 (PyPI)\n\n[fastocr @ PyPI](https://pypi.org/project/fastocr/)\n\n```shell\npip install --user fastocr\n# Linux 复制 desktop 文件到 ~/.local/share/applications\n```\n\n### 通用 (手动安装)\n\n```shell\npython setup.py install\n# Linux 复制 desktop 文件到 ~/.local/share/applications\n```\n\n### 通用 (仅本地开发)\n\n 自豪地使用 [Poetry](https://python-poetry.org/docs/) 进行开发\n\n```shell\npoetry install\n```\n\n## 使用方法\n\n```shell\nfastocr  # 运行\nfastocr --help  # 查看帮助\n```\n\n## DBus (Linux only)\n\nService name: `io.github.brucezhang1993.FastOCR`\n\nObject: `/io/github/brucezhang1993/FastOCR`\n\n### 方法\n\n| Actions            | Arguments           | Description                                                 |\n|:-------------------|:--------------------|:------------------------------------------------------------|\n| captureToClipboard | {seconds} {no_copy} | 执行 OCR 捕获到系统剪贴板或触发 dbus 信号                      |\n|                    |                     | seconds: 延迟执行单位为秒                                    |\n|                    |                     | no_copy: 如果为 true 则仅触发 dbus 信号而不复制到系统剪贴板    |\n| quitApp            | --                  | 退出应用                                                    |\n\n### 信号\n\n| Signals  | Arguments | Description                            |\n|:---------|:----------|:---------------------------------------|\n| captured | {text}    | OCR 识别结果文本会触发此信号             |\n|          |           | text: 文本识别结果                      |\n\n## 贡献\n\nPull requests are welcome.\n\nFor major changes, please open an issue first to discuss what you would\nlike to change.\n\n## License\n\nLGPL3\n',
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
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)

