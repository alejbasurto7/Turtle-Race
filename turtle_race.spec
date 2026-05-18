# Note: %APPDATA%/TurtleRace/leaderboard.json is generated at runtime by
# leaderboard.py — it is NOT a bundled resource and does NOT belong in datas=.

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/lawn.jpg', 'assets'), ('assets/*.mid', 'assets'), ('assets/midi/*.mid', 'assets/midi'), ('assets/snakes/*.png', 'assets/snakes'), ('assets/tracks/*.png', 'assets/tracks'), ('assets/turtles/*.jpg', 'assets/turtles')],
    hiddenimports=['turtle'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TurtleRace',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,
)
