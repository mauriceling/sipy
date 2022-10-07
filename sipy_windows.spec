# -*- mode: python ; coding: utf-8 -*-
"""!
SiPy: Statistics in Python - PyInstaller Spec File

Date created: 7th October 2022

License: GNU General Public License version 3 for academic or 
not-for-profit use only

SiPy package is free software: you can redistribute it and/or 
modify it under the terms of the GNU General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

block_cipher = None

sipy = Analysis(['sipy.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
sipy_pyz = PYZ(sipy.pure, sipy.zipped_data,
             cipher=block_cipher)
sipy_exe = EXE(sipy_pyz,
          sipy.scripts, 
          [],
          icon='images/sipy_icon.ico',
          exclude_binaries=True,
          name='sipy',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

sipyCLI = Analysis(['sipy_CLI.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
sipyCLI_pyz = PYZ(sipyCLI.pure, sipyCLI.zipped_data,
             cipher=block_cipher)
sipyCLI_exe = EXE(sipyCLI_pyz,
          sipyCLI.scripts, 
          [],
          icon='images/sipy_icon.ico',
          exclude_binaries=True,
          name='sipy_CLI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )

coll = COLLECT(sipy_exe,
               sipy.binaries,
               sipy.zipfiles,
               sipy.datas, 
               sipyCLI_exe,
               sipyCLI.binaries,
               sipyCLI.zipfiles,
               sipyCLI.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='sipy')
