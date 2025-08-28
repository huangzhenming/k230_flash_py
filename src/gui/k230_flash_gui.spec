# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import os
from pathlib import Path

spec_dir = Path.cwd()
datas = collect_data_files("PySide6")
block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[
        str(spec_dir),
        str(spec_dir.parent),
    ],
    binaries=[],
    datas=datas + [
        ("config.ini", "."),
        ("k230_flash_gui.pdf", "."),
        ("libusb-1.0.dll", "."),
        ("english.qm", "."),
        ("assets/*", "assets/"),
        (str(spec_dir.parent / "k230_flash" / "loaders"), "k230_flash/loaders"),
    ],
    hiddenimports=[
        "PySide6.QtWidgets",
        "PySide6.QtGui",
        "PySide6.QtCore",
        "PySide6.QtNetwork",
        "loguru",
        "usb",
        "usb.core",
        "usb.util",
        "usb.backend",
        "usb.backend.libusb1",
        "k230_flash",
        "k230_flash.api",
        "k230_flash.burners",
        "k230_flash.usb_utils",
        "k230_flash.kdimage",
        "k230_flash.file_utils",
        "k230_flash.progress",
        "k230_flash.constants",
        "k230_flash.arg_parser",
        "k230_flash.kdimg_utils",
        "k230_flash.main",
        "advanced_settings",
        "batch_flash",
        "common_widget_sytles",
        "log_file_monitor",
        "single_flash",
        "utils",
        "resources_rc",
    ],
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
    name="k230_flash_gui",
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon="assets/k230_flash_gui_logo.ico",
)

# macOS 下生成 .app 包
app = BUNDLE(
    exe,
    name="k230_flash_gui.app",
    icon="assets/k230_flash_gui_logo.icns",
    bundle_identifier="com.hzm.k230_flash_gui"
)
