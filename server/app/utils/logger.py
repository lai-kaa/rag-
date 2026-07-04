"""日志配置模块，将日志写入 logs/ 目录。"""

import logging
import os
from logging.handlers import TimedRotatingFileHandler

from app.config import settings

# 日志格式
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_initialized = False


def setup_logging() -> None:
    """初始化日志系统，创建 logs/ 目录并配置文件轮转。"""
    global _initialized
    if _initialized:
        return

    os.makedirs(settings.LOG_DIR, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 应用运行日志（按天轮转）
    app_handler = TimedRotatingFileHandler(
        os.path.join(settings.LOG_DIR, "app.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)
    root_logger.addHandler(app_handler)

    # 错误日志（按天轮转）
    error_handler = TimedRotatingFileHandler(
        os.path.join(settings.LOG_DIR, "error.log"),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的 logger 实例。"""
    setup_logging()
    return logging.getLogger(name)
