# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['born-dig-accessioner.py'],
             pathex=['/Users/aliciadetelich/Dropbox/git/born-digital-accessioner'],
             binaries=[],
             datas=[('assets', 'assets'), ('assets/custom.css', 'assets'), ('assets/fonts', 'assets/fonts'),
                    ('assets/header.css', 'assets'), ('assets/Yale_typeface', 'assets/Yale_typeface')],
             hiddenimports=['jinja2.ext', 'pyodbc'],
             hookspath=['hooks'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='born-dig-accessioner',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
app = BUNDLE(exe,
             name='born-dig-accessioner.app',
             icon='/Users/aliciadetelich/Dropbox/git/born-digital-accessioner/files/dig_icon.icns',
             bundle_identifier=None)
