"""
文件操作工具模块
提供安全的文件读写和操作功能
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, Union, List
import logging

logger = logging.getLogger(__name__)


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
        
    Returns:
        Path对象
    """
    path_obj = Path(path).resolve()
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def safe_read_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """
    安全读取文件，自动处理编码问题
    
    Args:
        file_path: 文件路径
        encoding: 首选编码
        
    Returns:
        文件内容
        
    Raises:
        FileNotFoundError: 文件不存在
        UnicodeDecodeError: 编码问题
    """
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        raise FileNotFoundError(f"文件不存在: {file_path_obj}")
    
    if not file_path_obj.is_file():
        raise ValueError(f"路径不是文件: {file_path_obj}")
    
    # 尝试多种编码
    encodings = [encoding, 'utf-8-sig', 'latin-1', 'cp1252', 'gbk', 'gb2312']
    
    for enc in encodings:
        try:
            with open(file_path_obj, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    # 所有编码都失败，尝试二进制读取
    with open(file_path_obj, 'rb') as f:
        content = f.read()
    return content.decode('utf-8', errors='ignore')


def safe_write_file(
    file_path: Union[str, Path],
    content: str,
    encoding: str = 'utf-8',
    backup: bool = False
) -> Path:
    """
    安全写入文件，自动创建目录
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
        encoding: 文件编码
        backup: 是否备份原文件
        
    Returns:
        写入的文件Path对象
    """
    file_path_obj = Path(file_path).resolve()
    
    # 确保目录存在
    ensure_directory(file_path_obj.parent)
    
    # 备份原文件
    if backup and file_path_obj.exists():
        backup_path = file_path_obj.with_suffix(f"{file_path_obj.suffix}.backup")
        shutil.copy2(file_path_obj, backup_path)
        logger.debug(f"已备份原文件: {backup_path}")
    
    # 写入文件
    with open(file_path_obj, 'w', encoding=encoding) as f:
        f.write(content)
    
    return file_path_obj


def get_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256') -> str:
    """
    计算文件哈希值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法 (md5, sha1, sha256)
        
    Returns:
        文件哈希值
    """
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        raise FileNotFoundError(f"文件不存在: {file_path_obj}")
    
    hash_func = getattr(hashlib, algorithm, hashlib.sha256)
    
    with open(file_path_obj, 'rb') as f:
        file_hash = hash_func()
        # 分块读取大文件
        for chunk in iter(lambda: f.read(8192), b''):
            file_hash.update(chunk)
    
    return file_hash.hexdigest()


def find_files(
    directory: Union[str, Path],
    patterns: Union[str, List[str]],
    recursive: bool = True
) -> List[Path]:
    """
    查找匹配模式的文件
    
    Args:
        directory: 目录路径
        patterns: 文件模式或模式列表
        recursive: 是否递归查找
        
    Returns:
        匹配的文件路径列表
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        return []
    
    if isinstance(patterns, str):
        patterns = [patterns]
    
    found_files = []
    
    for pattern in patterns:
        if recursive:
            files = list(directory_path.rglob(pattern))
        else:
            files = list(directory_path.glob(pattern))
        
        # 过滤出文件（排除目录）
        files = [f for f in files if f.is_file()]
        found_files.extend(files)
    
    # 去重并排序
    found_files = list(set(found_files))
    found_files.sort()
    
    return found_files


def validate_file_type(file_path: Union[str, Path], expected_extensions: List[str]) -> bool:
    """
    验证文件类型
    
    Args:
        file_path: 文件路径
        expected_extensions: 期望的文件扩展名列表
        
    Returns:
        是否匹配期望的类型
    """
    file_path_obj = Path(file_path)
    extension = file_path_obj.suffix.lower()
    
    # 检查扩展名
    if extension in expected_extensions:
        return True
    
    # 如果没有扩展名或扩展名不匹配，检查文件内容
    try:
        with open(file_path_obj, 'rb') as f:
            header = f.read(4)
        
        # 常见文件类型的魔术数字
        magic_numbers = {
            b'%PDF': '.pdf',
            b'PK\x03\x04': '.epub',  # EPUB是ZIP格式
            b'\x50\x4B\x03\x04': '.zip',
            b'\xD0\xCF\x11\xE0': '.xls',  # OLE2格式
        }
        
        for magic, ext in magic_numbers.items():
            if header.startswith(magic):
                return ext in expected_extensions
        
        return False
    except:
        return False


def get_size_string(size_bytes: int) -> str:
    """
    将字节数转换为易读的字符串
    
    Args:
        size_bytes: 字节数
        
    Returns:
        易读的大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"