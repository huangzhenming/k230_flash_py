import configparser
import shutil
import sys
from datetime import datetime
from platformdirs import user_config_dir
from pathlib import Path

import setuptools_scm
from loguru import logger


CONFIG_FILE = "config.ini"
HELP_FILE = "flash-python-gui.pdf"
APP_NAME = "k230_flash_gui"


# -------------------------
# 路径管理
# -------------------------

def get_app_config_dir() -> Path:
    """
    获取跨平台的用户配置目录
    - Linux: ~/.config/k230_flash_gui
    - Windows: %APPDATA%\k230_flash_gui
    - macOS: ~/Library/Application Support/k230_flash_gui
    """
    config_dir = Path(user_config_dir(APP_NAME))
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_exe_dir() -> Path:
    """获取 exe 所在目录（只读）"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path.cwd() / "src" / "gui"


def get_resource_path(filename: str) -> Path:
    """获取只读资源文件路径"""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / filename
    return Path.cwd() / filename

LOG_FILE_NAME = "k230_flash.log"
FULL_LOG_FILE_PATH = get_app_config_dir() / LOG_FILE_NAME

# -------------------------
# 配置文件管理
# -------------------------

def load_config():
    """从用户配置目录加载 config.ini"""
    config_path = get_app_config_dir() / CONFIG_FILE
    logger.debug(f"加载配置文件: {config_path}")

    config = configparser.ConfigParser()
    if config_path.exists():
        config.read(config_path, encoding="utf-8")
    else:
        logger.warning("未找到 config.ini，创建默认配置")
        save_config(config)

    return config


def save_config(config):
    """保存 ConfigParser 对象到用户配置目录"""
    config_path = get_app_config_dir() / CONFIG_FILE
    with open(config_path, "w", encoding="utf-8") as configfile:
        config.write(configfile)
    logger.debug(f"配置已保存到 {config_path}")


# -------------------------
# 日志管理
# -------------------------

def update_log_level(log_level):
    """动态更新日志级别"""
    try:
        logger.remove()
        if sys.stdout is not None:
            logger.add(sys.stdout, level=log_level.upper(),
                       format="{time:HH:mm:ss.SSS} | {level:<8} | {message}")

        if FULL_LOG_FILE_PATH:
            log_path = get_app_config_dir() / "k230_flash.log"
            logger.add(
                log_path,
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


# -------------------------
# 资源文件提取
# -------------------------

def extract_resource(filename: str):
    """
    从资源中复制文件到用户配置目录（仅第一次）
    例如帮助文档、默认模板等
    """
    target_path = get_app_config_dir() / filename
    if not target_path.exists():
        try:
            shutil.copy(get_resource_path(filename), target_path)
            logger.info(f"提取 {filename} 到 {target_path}")
        except Exception as e:
            logger.error(f"提取 {filename} 失败: {e}")


# -------------------------
# 版本号管理
# -------------------------

def get_version_from_git():
    return f"v{setuptools_scm.get_version()}"


def gen_version_file():
    version = get_version_from_git()
    version_file = get_app_config_dir() / "version.txt"
    with open(version_file, "w") as f:
        f.write(version)


def get_version_from_file(name="version.txt"):
    version_path = get_app_config_dir() / name
    try:
        with open(version_path, "r") as f:
            version = f.read()
    except FileNotFoundError:
        version = "v0.0"
    return version


def get_version():
    if getattr(sys, "frozen", False):
        return get_version_from_file()
    return get_version_from_git()


# -------------------------
# 入口
# -------------------------

if __name__ == "__main__":
    gen_version_file()
    print(get_version())

    load_config()
