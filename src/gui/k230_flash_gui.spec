# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os
import platform
import glob
from pathlib import Path
import PySide6

spec_dir = Path.cwd()
block_cipher = None
system = platform.system().lower()

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

# Windows特定配置
if system == "windows":
    # 添加libusb-1.0.dll
    libusb_dll = os.path.join(spec_dir, "libusb-1.0.dll")
    if os.path.exists(libusb_dll):
        binaries += [(libusb_dll, ".")]
        print(f"Adding Windows USB library: {libusb_dll}")
    
    # Windows系统库
    try:
        import usb.backend.libusb1
        backend_path = os.path.dirname(usb.backend.libusb1.__file__)
        for dll in glob.glob(os.path.join(backend_path, "*.dll")):
            binaries += [(dll, "usb/backend")]
    except:
        pass

# macOS特定配置
elif system == "darwin":
    # macOS USB库配置
    try:
        # 查找libusb库
        import subprocess
        result = subprocess.run(["brew", "--prefix", "libusb"], capture_output=True, text=True)
        if result.returncode == 0:
            libusb_path = result.stdout.strip()
            libusb_lib = os.path.join(libusb_path, "lib", "libusb-1.0.dylib")
            if os.path.exists(libusb_lib):
                binaries += [(libusb_lib, ".")]
                print(f"Adding macOS USB library: {libusb_lib}")
    except:
        # 备用路径
        for path in ["/usr/local/lib/libusb-1.0.dylib", "/opt/homebrew/lib/libusb-1.0.dylib"]:
            if os.path.exists(path):
                binaries += [(path, ".")]
                break

# Linux特定配置
elif system == "linux":
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
            
        print(f"Found gdk-pixbuf path: {gdk_pixbuf_path}")
        print(f"Number of loaders: {len([f for f in glob.glob(os.path.join(gdk_pixbuf_path, 'loaders', '*.so'))])}")
    else:
        print("Warning: gdk-pixbuf path not found, may cause image loading issues")


a = Analysis(
    ["main.py"],
    pathex=[str(spec_dir), str(spec_dir.parent)],
    binaries=binaries,
    datas=datas + [
        ("config.ini", "."),
        ("k230_flash_gui.pdf", "."),
        ("english.qm", "."),
        ("assets/*", "assets/"),
        (str(spec_dir.parent / "k230_flash" / "loaders"), "k230_flash/loaders"),
    ] + (["libusb-1.0.dll", "."] if system == "windows" and os.path.exists("libusb-1.0.dll") else []),
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
    # Windows特定设置
    version="version_info.txt" if system == "windows" and os.path.exists("version_info.txt") else None,
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

# macOS .app bundle配置
if system == "darwin":
    app = BUNDLE(
        coll,
        name="K230FlashGUI.app",
        icon="assets/k230_flash_gui_logo.ico",
        bundle_identifier="com.kendryte.k230flashgui",
        version="1.0.0",
        info_plist={
            'CFBundleName': 'K230 Flash GUI',
            'CFBundleDisplayName': 'K230 Flash GUI',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'LSMinimumSystemVersion': '10.14.0',
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'LSUIElement': False,
            'NSHighResolutionCapable': True,
            'CFBundleDocumentTypes': [{
                'CFBundleTypeName': 'K230 Image Files',
                'CFBundleTypeExtensions': ['kdimg', 'img'],
                'CFBundleTypeRole': 'Editor'
            }]
        }
    )
