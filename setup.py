
# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = ''

setup(
    long_description=readme,
    name='fastocr',
    version='0.1.2',
    description='FastOCR is a desktop application for OCR API.',
    python_requires='<3.10,>=3.7',
    project_urls={"documentation": "https://github.com/BruceZhang1993/FastOCR", "homepage": "https://github.com/BruceZhang1993/FastOCR", "repository": "https://github.com/BruceZhang1993/FastOCR"},
    author='Bruce Zhang',
    author_email='zttt183525594@gmail.com',
    license='LGPL-3.0-only',
    keywords='ocr',
    entry_points={"console_scripts": ["fastocr = fastocr.__main__:main"]},
    packages=['fastocr'],
    package_dir={"": "."},
    package_data={"fastocr": ["data/*.desktop", "data/*.ini", "data/*.pro", "i18n/*.qm", "i18n/*.ts", "qml/*.qml", "resource/icon/*.svg"]},
    install_requires=['aiohttp==3.*,>=3.7.3', 'click==7.*,>=7.1.2', 'dbus-python==1.*,>=1.2.16', 'pyside2==5.*,>=5.15.2', 'qasync==0.*,>=0.13.0'],
    extras_require={"dev": ["dephell==0.*,>=0.8.3"]},
)
