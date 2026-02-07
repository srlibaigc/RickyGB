"""
Markdown处理模块
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导出主要功能
try:
    from .merge_markdown import MarkdownMerger
    from .merge_markdown import main as merge_markdown_main
    
    __all__ = ['MarkdownMerger', 'merge_markdown_main']
except ImportError as e:
    print(f"导入Markdown模块时出错: {e}")
    __all__ = []