#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Windows平台GUI打包脚本
使用PyInstaller将k230_flash_gui打包为exe文件
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def setup_windows_build():
    """配置Windows构建环境"""
    print("=== 配置Windows构建环境 ===")
    
    # 确保当前在gui目录
    gui_dir = Path(__file__).parent
    os.chdir(gui_dir)
    
    # 检查必要文件
    required_files = [
        "k230_flash_gui.spec",
        "main.py",
        "config.ini",
        "libusb-1.0.dll"  # Windows USB驱动
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"错误: 缺少必要文件 {file}")
            return False
    
    # 检查assets目录
    if not Path("assets").exists():
        print("错误: 缺少assets目录")
        return False
    
    print("Windows构建环境检查完成")
    return True

def build_executable():
    """使用PyInstaller构建exe文件"""
    print("=== 开始构建Windows可执行文件 ===")
    
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

def create_installer():
    """创建Windows安装包"""
    print("=== 创建Windows安装包 ===")
    
    dist_dir = Path("dist/k230_flash_gui")
    if not dist_dir.exists():
        print("错误: 找不到构建输出目录")
        return False
    
    # 创建zip包
    output_dir = Path("../../upload")
    output_dir.mkdir(exist_ok=True)
    
    # 获取版本信息 - 优先使用环境变量，fallback到git
    version = os.environ.get('VERSION')
    if not version:
        try:
            import subprocess
            result = subprocess.run(
                ["git", "describe", "--tags", "--always"],
                capture_output=True, text=True, cwd="../.."
            )
            version = result.stdout.strip() if result.returncode == 0 else "dev"
        except:
            version = "dev"
    
    print(f"使用版本: {version}")
    
    # 创建zip文件
    zip_name = f"k230_flash_gui-windows-{version}"
    shutil.make_archive(
        str(output_dir / zip_name),
        'zip',
        str(dist_dir.parent),
        dist_dir.name
    )
    
    print(f"Windows安装包已创建: {zip_name}.zip")
    return True

def main():
    """主函数"""
    print("K230 Flash GUI - Windows构建脚本")
    print("=" * 50)
    
    if not setup_windows_build():
        sys.exit(1)
    
    if not build_executable():
        sys.exit(1)
    
    if not create_installer():
        sys.exit(1)
    
    print("\n=== Windows构建完成 ===")
    print("输出目录: dist/k230_flash_gui/")
    print("安装包: ../../upload/")

if __name__ == "__main__":
    main()