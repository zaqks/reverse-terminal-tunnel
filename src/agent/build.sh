#!/bin/bash
# python -m nuitka --onefile --mingw64 script.py

rm build -r
mkdir build
cd build
cp ../components . -r
cp ../main.py .

python -m nuitka main.py \
  --onefile \
  --lto=yes \
  --windows-disable-console \
  --assume-yes-for-downloads \
  --enable-plugin=anti-bloat \
  --noinclude-pytest-mode=nofollow \
  --noinclude-setuptools-mode=nofollow \
  --include-package=certifi \
  --include-package=websockets \
  --include-package=tornado \
  --include-package=terminado \
  
  
