#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
macOS平台GUI打包脚本
使用PyInstaller将k230_flash_gui打包为.app，然后创建dmg文件
"""

import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path


def setup_macos_build():
    """配置macOS构建环境"""
    print("=== 配置macOS构建环境 ===")
    
    # 确保当前在gui目录
    gui_dir = Path(__file__).parent
    os.chdir(gui_dir)
    
    # 检查必要文件
    required_files = [
        "k230_flash_gui.spec",
        "main.py",
        "config.ini"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"错误: 缺少必要文件 {file}")
            return False
    
    # 检查assets目录
    if not Path("assets").exists():
        print("错误: 缺少assets目录")
        return False
    
    # 检查是否在macOS上
    if sys.platform != "darwin":
        print("警告: 当前不在macOS平台，某些功能可能不可用")
    
    print("macOS构建环境检查完成")
    return True

def build_app():
    """使用PyInstaller构建.app文件"""
    print("=== 开始构建macOS应用程序 ===")
    
    try:
        # 清理之前的构建
        if Path("build").exists():
            shutil.rmtree("build")
        if Path("dist").exists():
            shutil.rmtree("dist")
        
        # 运行PyInstaller
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean", "-y",
            "k230_flash_gui.spec"
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"PyInstaller构建失败:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
        
        print("PyInstaller构建成功")
        return True
        
    except Exception as e:
        print(f"构建过程中发生错误: {e}")
        return False

def create_app_bundle():
    """创建标准的macOS .app bundle"""
    print("=== 创建macOS应用程序Bundle ===")
    
    dist_dir = Path("dist/k230_flash_gui")
    app_dir = Path("dist/K230FlashGUI.app")
    
    if not dist_dir.exists():
        print("错误: 找不到PyInstaller输出目录")
        return False
    
    # 如果已经是.app bundle，跳过
    if app_dir.exists():
        print("应用程序Bundle已存在")
        return True
    
    try:
        # 创建.app目录结构
        app_dir.mkdir(exist_ok=True)
        contents_dir = app_dir / "Contents"
        contents_dir.mkdir(exist_ok=True)
        macos_dir = contents_dir / "MacOS"
        macos_dir.mkdir(exist_ok=True)
        resources_dir = contents_dir / "Resources"
        resources_dir.mkdir(exist_ok=True)
        
        # 复制可执行文件和资源
        if (dist_dir / "k230_flash_gui").exists():
            shutil.copy2(dist_dir / "k230_flash_gui", macos_dir / "K230FlashGUI")
        else:
            # 复制整个目录内容
            for item in dist_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, macos_dir)
                else:
                    shutil.copytree(item, macos_dir / item.name, dirs_exist_ok=True)
        
        # 复制图标文件
        icon_src = Path("assets/k230_flash_gui_logo.ico")
        if icon_src.exists():
            icon_dst = resources_dir / "icon.ico"
            shutil.copy2(icon_src, icon_dst)
        
        # 创建Info.plist文件
        info_plist = {
            'CFBundleName': 'K230 Flash GUI',
            'CFBundleDisplayName': 'K230 Flash GUI',
            'CFBundleIdentifier': 'com.kendryte.k230flashgui',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleExecutable': 'K230FlashGUI',
            'CFBundleIconFile': 'icon.ico',
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': '????',
            'LSMinimumSystemVersion': '10.14.0',
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'LSUIElement': False,
            'CFBundleInfoDictionaryVersion': '6.0'
        }
        
        with open(contents_dir / "Info.plist", 'wb') as f:
            plistlib.dump(info_plist, f)
        
        print("macOS应用程序Bundle创建完成")
        return True
        
    except Exception as e:
        print(f"创建App Bundle时发生错误: {e}")
        return False

def create_dmg():
    """创建DMG安装包"""
    print("=== 创建DMG安装包 ===")
    
    app_path = Path("dist/K230FlashGUI.app")
    if not app_path.exists():
        print("错误: 找不到应用程序Bundle")
        return False
    
    # 获取版本信息
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--always"],
            capture_output=True, text=True, cwd="../.."
        )
        version = result.stdout.strip() if result.returncode == 0 else "dev"
    except:
        version = "dev"
    
    # 创建输出目录
    output_dir = Path("../../upload")
    output_dir.mkdir(exist_ok=True)
    
    dmg_name = f"k230_flash_gui-macos-{version}.dmg"
    dmg_path = output_dir / dmg_name
    
    # 删除已存在的dmg文件
    if dmg_path.exists():
        dmg_path.unlink()
    
    try:
        # 创建临时DMG目录
        temp_dmg_dir = Path("temp_dmg")
        if temp_dmg_dir.exists():
            shutil.rmtree(temp_dmg_dir)
        temp_dmg_dir.mkdir()
        
        # 复制应用程序到临时目录
        shutil.copytree(app_path, temp_dmg_dir / "K230FlashGUI.app")
        
        # 创建Applications符号链接
        applications_link = temp_dmg_dir / "Applications"
        if not applications_link.exists():
            os.symlink("/Applications", applications_link)
        
        # 使用hdiutil创建DMG
        cmd = [
            "hdiutil", "create",
            "-volname", "K230 Flash GUI",
            "-srcfolder", str(temp_dmg_dir),
            "-ov", "-format", "UDZO",
            str(dmg_path)
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"创建DMG失败:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
        
        # 清理临时目录
        shutil.rmtree(temp_dmg_dir)
        
        print(f"DMG安装包已创建: {dmg_name}")
        return True
        
    except Exception as e:
        print(f"创建DMG时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("K230 Flash GUI - macOS构建脚本")
    print("=" * 50)
    
    if not setup_macos_build():
        sys.exit(1)
    
    if not build_app():
        sys.exit(1)
    
    if not create_app_bundle():
        sys.exit(1)
    
    if not create_dmg():
        sys.exit(1)
    
    print("\n=== macOS构建完成 ===")
    print("输出目录: dist/K230FlashGUI.app")
    print("安装包: ../../upload/")

if __name__ == "__main__":
    main()