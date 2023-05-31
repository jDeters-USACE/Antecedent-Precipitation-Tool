# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

added_files = [
    ( 'C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool\\images\\folder.gif', 'images' ),
    ( 'C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool\\images\\RD_2_0.png', 'images' ),
    ( 'C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool\\images\\Graph.ico', 'images' ),
    ( 'C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool\\images\\Plus.gif', 'images' ),
    ( 'C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool\\images\\Minus.gif', 'images' ),
    ( 'C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool\\images\\Question.gif', 'images' ),
    ( 'C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool\\images\\Traverse_40%_503.gif', 'images' ),
    ( 'C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool\\images\\Traverse_80%_1920.png', 'images' ),
    ( 'C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool\\version', '.' ),
    ( 'C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool\\v\\main_ex', 'v' ),
    ( 'C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool\\proj.db', '.')
]

a = Analysis(['C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool\\main_ex.py'],
             pathex=['C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool'],
             binaries=[],
             datas=added_files,
             hiddenimports=[
				'cftime',
				'cftime._strptime',
				'matplotlib.backends.backend_pdf',
				'osgeo._gdal'
             ],
             hookspath=[],
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
          [],
          icon='C:\\Users\\Desktop\\Gutenson\\2023_WRAP_Streamflow_APT\\Repositories\\Antecedent-Precipitation-Tool\\images\\Graph.ico',
          exclude_binaries=True,
          name='main_ex',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
		  upx_dir='G:\\upx-4.0.2-win64',
          console=True)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
			   upx_dir='G:\\upx-4.0.2-win64',
               upx_exclude=[],
               name='main_ex')
