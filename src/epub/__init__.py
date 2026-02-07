"""
EPUB处理模块
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导出主要功能
try:
    from .epub_to_markdown_v1 import EPUBConverterV1
    from .epub_to_markdown_v1 import main as epub_converter_main
    
    __all__ = ['EPUBConverterV1', 'epub_converter_main']
except ImportError as e:
    print(f"导入EPUB模块时出错: {e}")
    __all__ = []