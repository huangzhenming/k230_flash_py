# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os
from pathlib import Path
import PySide6

spec_dir = Path.cwd()
block_cipher = None

# 收集 PySide6 的所有资源文件
datas = collect_data_files("PySide6")

# 修复 macOS 上 QtWebEngine 的 Helpers 目录问题
qt_helpers = os.path.join(
    os.path.dirname(PySide6.__file__),
    "Qt", "lib", "QtWebEngineCore.framework", "Helpers"
)
if os.path.exists(qt_helpers):
    datas += [(qt_helpers, "PySide6/Qt/lib/QtWebEngineCore.framework/Helpers")]

qt_platforms = os.path.join(os.path.dirname(PySide6.__file__), "Qt", "plugins", "platforms")
if os.path.exists(qt_platforms):
    datas += [(qt_platforms, "PySide6/Qt/plugins/platforms")]

a = Analysis(
    ["main.py"],
    pathex=[str(spec_dir), str(spec_dir.parent)],
    binaries=[],
    datas=datas + [
        ("config.ini", "."),
        ("k230_flash_gui.pdf", "."),
        ("libusb-1.0.dll", "."),   # Windows 用，macOS 下会忽略
        ("english.qm", "."),
        ("assets/*", "assets/"),
        (str(spec_dir.parent / "k230_flash" / "loaders"), "k230_flash/loaders"),
    ],
    hiddenimports=collect_submodules("PySide6") + [
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
    exclude_binaries=True,  # 生成 onedir
    name="k230_flash_gui",
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon="assets/k230_flash_gui_logo.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="k230_flash_gui"
)
