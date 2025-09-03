# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os
import platform
import glob
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

binaries = []
if platform.system().lower() == "linux":
    # 尝试多个可能的gdk-pixbuf路径（适配不同Linux发行版）
    gdk_pixbuf_paths = [
        "/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0",
        "/usr/lib64/gdk-pixbuf-2.0/2.10.0",
        "/usr/lib/gdk-pixbuf-2.0/2.10.0"
    ]
    
    gdk_pixbuf_path = None
    for path in gdk_pixbuf_paths:
        if os.path.exists(path):
            gdk_pixbuf_path = path
            break
    
    if gdk_pixbuf_path:
        # 复制所有gdk-pixbuf加载器
        binaries += [
            (f, "gdk-pixbuf/loaders")
            for f in glob.glob(os.path.join(gdk_pixbuf_path, "loaders", "*.so"))
        ]
        
        # 如果存在loaders.cache，复制它；否则将在运行时生成
        cache_file = os.path.join(gdk_pixbuf_path, "loaders.cache")
        if os.path.exists(cache_file):
            datas += [(cache_file, "gdk-pixbuf/")]
            
        print(f"找到gdk-pixbuf路径: {gdk_pixbuf_path}")
        print(f"加载器数量: {len([f for f in glob.glob(os.path.join(gdk_pixbuf_path, 'loaders', '*.so'))])}")
    else:
        print("警告: 未找到gdk-pixbuf路径，可能会导致图像加载问题")


a = Analysis(
    ["main.py"],
    pathex=[str(spec_dir), str(spec_dir.parent)],
    binaries=binaries,
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
