#!/bin/bash
# python -m nuitka --onefile --mingw64 script.py

rm build -r
mkdir build
cd build
cp ../components . -r
cp ../main.py .
cp ../.env .

python -m nuitka main.py \
  --onefile \
  --lto=yes \
  --windows-disable-console \
  --include-data-files=.env=.env \
  --follow-imports \
  --assume-yes-for-downloads \
  --enable-plugin=anti-bloat \
  --include-package=websockets \
  --include-package=certifi \
  