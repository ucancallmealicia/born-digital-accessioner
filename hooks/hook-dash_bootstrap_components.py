#/usr/bin/python3

from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('dash_bootstrap_components')