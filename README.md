# FastOCR

[![GitHub top language](https://img.shields.io/github/languages/top/BruceZhang1993/FastOCR?style=flat-square)](https://github.com/BruceZhang1993/FastOCR/search?l=python)
[![GitHub](https://img.shields.io/github/license/BruceZhang1993/FastOCR?style=flat-square)](https://github.com/BruceZhang1993/FastOCR/blob/master/LICENSE)
[![GitHub version](https://img.shields.io/github/v/tag/BruceZhang1993/FastOCR?label=Version&style=flat-square)](https://github.com/BruceZhang1993/FastOCR/releases)
![PyPI](https://img.shields.io/pypi/v/fastocr?style=flat-square)

FastOCR 是一款开源免费的提供在线 OCR 文字识别的桌面工具

## 支持的 OCR API 后端

- [x] 百度 AI 文字识别服务  https://ai.baidu.com/tech/ocr
- [x] 有道文字识别服务  https://ai.youdao.com/product-ocr-print.s
- [x] 旷视 Face++ 文字识别服务 (Experimental)  https://www.faceplusplus.com.cn/general-text-recognition/
- [ ] 本地 OCR

### 特性

- [x] 通用文字识别 / 多个在线 OCR API 支持
- [x] 多语言支持 / 百度
- [x] 高精度接口支持 / 百度
- [x] 识别文字搜索
- [ ] 本地 OCR 后端
- [ ] 自定义快捷动作

## 支持操作系统

- Linux X11
- Windows
- macOS (Experimental)
- Linux Wayland (Experimental)

### 支持的 Wayland 环境 (Linux)

- Gnome Wayland
- KDE Wayland
- Sway

## 安装

### Windows  
 64 位预编译版，解压即可使用

点击下载 -> [Download](https://github.com/BruceZhang1993/FastOCR/releases/latest) 解压到安装目录，执行 FastOCR.exe

### macOS

理论上支持但无构建环境，打包过程类似 Windows 如下，生成的文件位于项目的 dist 目录下

```shell
pip install poetry
poetry update
poetry run pyinstaller build.spec
```

### Arch Linux

稳定版本 https://aur.archlinux.org/packages/fastocr

开发版本 https://aur.archlinux.org/packages/fastocr-git

 从 AUR 下载脚本编译或使用你喜欢的 AUR 辅助工具

```shell
yay -S fastocr  # 使用 yay
pikaur -S fastocr  # 使用 pikaur
```

### Nix/NixOS
 
使用 [NixOS CN flakes](https://github.com/nixos-cn/flakes) 或 [berberman flakes](https://github.com/berberman/flakes) 安装

```shell
nix run github:berberman/flakes#fastocr
```

### 通用 (PyPI)

[fastocr @ PyPI](https://pypi.org/project/fastocr/)

```shell
pip install --user fastocr
# Linux 复制 desktop 文件到 ~/.local/share/applications
```

### 通用 (手动安装)

```shell
python setup.py install
# Linux 复制 desktop 文件到 ~/.local/share/applications
```

### 通用 (仅本地开发)

 自豪地使用 [Poetry](https://python-poetry.org/docs/) 进行开发

```shell
poetry install
```

## 使用方法

```shell
fastocr  # 运行
fastocr --help  # 查看帮助
```

## DBus (Linux only)

Service name: `io.github.brucezhang1993.FastOCR`

Object: `/io/github/brucezhang1993/FastOCR`

### 方法

| Actions            | Arguments           | Description                                                 |
|:-------------------|:--------------------|:------------------------------------------------------------|
| captureToClipboard | {seconds} {no_copy} | 执行 OCR 捕获到系统剪贴板或触发 dbus 信号                      |
|                    |                     | seconds: 延迟执行单位为秒                                    |
|                    |                     | no_copy: 如果为 true 则仅触发 dbus 信号而不复制到系统剪贴板    |
| quitApp            | --                  | 退出应用                                                    |

### 信号

| Signals  | Arguments | Description                            |
|:---------|:----------|:---------------------------------------|
| captured | {text}    | OCR 识别结果文本会触发此信号             |
|          |           | text: 文本识别结果                      |

## 贡献

Pull requests are welcome.

For major changes, please open an issue first to discuss what you would
like to change.

## License

LGPL3
