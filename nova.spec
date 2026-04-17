# nova.spec
# ─────────────────────────────────────────────────────────────
#  PyInstaller spec for NOVA — AI Voice Assistant
#  Run:  pyinstaller nova.spec
# ─────────────────────────────────────────────────────────────

block_cipher = None

a = Analysis(
    ['nova_ui.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include the core assistant engine alongside the UI
        ('nova_assistant_v9.py', '.'),
    ],
    hiddenimports=[
        # Speech Recognition
        'speech_recognition',
        'pyaudio',
        # TTS
        'pyttsx3',
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
        # GUI
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        # AI / networking
        'groq',
        'requests',
        'httpx',
        # Translator
        'deep_translator',
        'deep_translator.google_trans',
        # Utilities
        'pyautogui',
        'pywhatkit',
        'psutil',
        'openpyxl',
        'screen_brightness_control',
        # Standard lib helpers often missed
        'pkg_resources.py2_warn',
        'encodings.utf_8',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'scipy',
        'PIL', 'tkinter', 'wx',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Nova',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # No black terminal window — clean UI only
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='nova_icon.ico',  # Uncomment and add nova_icon.ico to use a custom icon
)
