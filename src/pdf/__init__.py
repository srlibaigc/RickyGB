"""
PDF处理模块
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导出主要功能
try:
    # 基础版本
    from .pdf_chapter_splitter_v1 import main as splitter_v1_main
    
    # OCR版本
    from .pdf_chapter_splitter_v2 import main as splitter_v2_main
    
    # 最终版本
    from .pdf_chapter_splitter_final import main as splitter_final_main
    
    # OCR模块
    from .pdf_ocr_module import PDFOCR
    from .pdf_ocr_processor import PDFOCRProcessor
    
    # 章节检测器
    from .pdf_chapter_detector import ChapterDetector as PDFChapterDetector
    
    # 批量处理器
    from .pdf_batch_processor import main as batch_processor_main
    
    __all__ = [
        'splitter_v1_main',
        'splitter_v2_main', 
        'splitter_final_main',
        'PDFOCR',
        'PDFOCRProcessor',
        'PDFChapterDetector',
        'batch_processor_main'
    ]
except ImportError as e:
    print(f"导入PDF模块时出错: {e}")
    __all__ = []