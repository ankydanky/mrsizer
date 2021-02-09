#! /bin/bash

rm -rf dist
rm -rf build

python -m PyInstaller \
--icon systray.icns \
--windowed \
--onedir \
--add-data "systray.png:." \
--name "MRSizer" \
MRSizer.py

rm -rf build
