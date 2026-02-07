"""
日志工具模块
提供统一的日志配置
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_str: Optional[str] = None,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    设置日志配置
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_str: 日志格式字符串
        log_file: 日志文件路径
        
    Returns:
        配置好的root logger
    """
    # 设置日志级别
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    log_level = level_map.get(level.upper(), logging.INFO)
    
    # 设置格式
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_str)
    
    # 获取root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # 清除现有handler
    logger.handlers.clear()
    
    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件handler
    if log_file:
        from .file_utils import ensure_directory
        ensure_directory(log_file)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的logger
    
    Args:
        name: logger名称
        
    Returns:
        logging.Logger实例
    """
    return logging.getLogger(name)


class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self, total: int, description: str = "处理进度"):
        self.total = total
        self.description = description
        self.current = 0
        self.logger = get_logger(__name__)
    
    def update(self, increment: int = 1, log_interval: int = 10) -> None:
        """更新进度"""
        self.current += increment
        
        if self.total > 0 and self.current % log_interval == 0:
            percentage = (self.current / self.total) * 100
            self.logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)")
    
    def complete(self) -> None:
        """完成进度跟踪"""
        if self.total > 0:
            self.logger.info(f"{self.description} 完成: {self.current}/{self.total} (100%)")
        else:
            self.logger.info(f"{self.description} 完成: {self.current} 项")