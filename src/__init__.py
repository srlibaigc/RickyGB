"""
RickyGB - Python多功能文档处理工具箱
"""

__version__ = "1.0.0"
__author__ = "RickyGB Team"

# 导出各个模块
from . import excel
from . import pdf
from . import epub
from . import markdown
from . import utils
from . import heartbeat

__all__ = ['excel', 'pdf', 'epub', 'markdown', 'utils', 'heartbeat']