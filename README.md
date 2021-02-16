# FastOCR

![GitHub top language](https://img.shields.io/github/languages/top/BruceZhang1993/FastOCR?style=flat-square)
![GitHub](https://img.shields.io/github/license/BruceZhang1993/FastOCR?style=flat-square)

FastOCR is a desktop application for OCR API.

## Installation

### Arch Linux

[fastocr-git @ AUR](https://aur.archlinux.org/packages/fastocr-git/)

Build from AUR or install with your favorite AUR helper.

```shell
yay -S fastocr-git  # Using yay
pikaur -S fastocr-git  # Using pikaur
# ...
```

### PyPI

[fastocr @ PyPI](https://pypi.org/project/fastocr/)

```shell
pip install --user fastocr
# Then copy desktop file to ~/.local/share/applications
```

### Manually

Proudly use [DepHell](https://dephell.readthedocs.io/) to generate
setup.py file.

```shell
python setup.py install
# Then copy desktop file to ~/.local/share/applications
```

## Development

Proudly use [Poetry](https://python-poetry.org/docs/) for developing.

```shell
poetry install
```

## Usage

```shell
fastocr
```

## DBus

Service name: `io.github.brucezhang1993.FastOCR`

Object: `/io/github/brucezhang1993/FastOCR`

### Methods

| Actions            | Arguments           | Description                                                 |
|:-------------------|:--------------------|:------------------------------------------------------------|
| captureToClipboard | {seconds} {no_copy} | Capture and OCR to system clipboard or dbus signal          |
|                    |                     | seconds: Delay capture in seconds                           |
|                    |                     | no_copy: If true, the result will not be saved in clipboard |
| quitApp            | --                  | Quit app                                                    |

### Signal

| Signals  | Arguments | Description                            |
|:---------|:----------|:---------------------------------------|
| captured | {text}    | OCR result will be sent to this signal |
|          |           | text: OCR result in plain text         |

## Contributing

Pull requests are welcome.

For major changes, please open an issue first to discuss what you would
like to change.

## License

LGPL3
