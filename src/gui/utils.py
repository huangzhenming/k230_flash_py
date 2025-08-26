import configparser
import shutil
import sys
from datetime import datetime
from pathlib import Path

import setuptools_scm

# import debugpy
from loguru import logger

from k230_flash.constants import FULL_LOG_FILE_PATH

CONFIG_FILE = "config.ini"
help_file = "flash-python-gui.pdf"

# debugpy.debug_this_thread()


def load_config():
    """从 exe 目录加载 config.ini"""
    config_path = get_exe_dir() / CONFIG_FILE  # 从 exe 目录加载
    logger.debug(f"加载配置文件: {config_path}")

    config = configparser.ConfigParser()
    if config_path.exists():
        config.read(config_path, encoding="utf-8")
    else:
        logger.warning("未找到 config.ini，创建默认配置")
        save_config(config)  # 如果配置文件不存在，则创建默认配置

    return config


def save_config(config):
    """保存 ConfigParser 对象到 config.ini"""
    config_path = get_exe_dir() / CONFIG_FILE  # 从 exe 目录加载
    with open(config_path, "w", encoding="utf-8") as configfile:
        config.write(configfile)
    logger.debug("配置已保存到 config.ini")


def update_log_level(log_level):
    """
    动态更新日志级别
    :param log_level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
    """
    try:
        # 移除现有处理器并重新配置
        logger.remove()

        # 重新添加控制台处理器（如果可用）
        if sys.stdout is not None:
            logger.add(sys.stdout, level=log_level.upper(), format="{time:HH:mm:ss.SSS} | {level:<8} | {message}")

        # 重新添加文件处理器
        if FULL_LOG_FILE_PATH:
            logger.add(
                FULL_LOG_FILE_PATH,
                format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level:<8} | {name} | {message}",
                rotation="10 MB",
                retention="10 days",
                level=log_level.upper(),
                enqueue=True,
                encoding="utf-8",
            )

        logger.debug(f"日志级别已更新为: {log_level.upper()}")

    except Exception as e:
        if sys.stdout is not None:
            print(f"Warning: 更新日志级别失败: {e}")


# 以下是一些辅助函数，用于处理资源文件， 用于检测 pyinstaller 打包后的环墋
def get_exe_dir():
    # 获取 exe 所在目录
    return Path(sys.executable).parent if getattr(sys, "frozen", False) else Path.cwd() / "src" / "gui"


def get_resource_path(filename):
    # 获取资源文件路径
    return Path(sys._MEIPASS) / filename if getattr(sys, "frozen", False) else Path.cwd() / filename


def extract_resource(filename):
    # 从资源中解压缩文件到 exe 目录
    exe_resource_path = get_exe_dir() / filename
    if not exe_resource_path.exists():
        logger.info(f"未找到 {exe_resource_path}，从资源中复制")
        try:
            if getattr(sys, "frozen", False):
                shutil.copy(get_resource_path(filename), exe_resource_path)
                logger.info(f"提取 {filename} 到 {exe_resource_path}")
        except Exception as e:
            logger.error(f"提取 {filename} 失败: {e}")


# 以下是一些辅助函数，用于处理版本号
def get_version_from_git():
    return f"v{setuptools_scm.get_version()}"


def gen_version_file():
    version = get_version_from_git()
    with open("version.txt", "w") as f:
        f.write(version)


def get_version_from_file(name="version.txt"):
    try:
        with open(name, "r") as f:
            version = f.read()
    except FileNotFoundError:
        version = "v0.0"
    finally:
        return version


def get_version():
    if getattr(sys, "frozen", False):  # 是否为 PyInstaller 打包的环境
        base_path = Path(sys._MEIPASS)  # PyInstaller 解压的临时目录
        return get_version_from_file(base_path / "version.txt")
    else:
        return get_version_from_git()


if __name__ == "__main__":
    gen_version_file()
    print(get_version())

    load_config()
    pass
