"""
Excel处理模块
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导出主要功能
try:
    from .xlsx2md import ExcelToMarkdownConverter as OriginalConverter
    from .xlsx2md_improved import ExcelToMarkdownConverter as ImprovedConverter
    from .create_sample_data import create_sample_excel
    
    __all__ = ['OriginalConverter', 'ImprovedConverter', 'create_sample_excel']
except ImportError as e:
    print(f"导入Excel模块时出错: {e}")
    __all__ = []