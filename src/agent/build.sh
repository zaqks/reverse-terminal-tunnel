#!/bin/bash
# python -m nuitka --onefile --mingw64 script.py

python -m nuitka main.py \
  --onefile \
  --lto=yes \
  --windows-disable-console \
  --include-data-files=.env=.env \
  --include-package=websockets \
  --include-package=tornado \
  --include-package=terminado \
  --include-package=requests

#   --enable-plugin=dotenv \