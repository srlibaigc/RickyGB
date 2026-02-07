#!/usr/bin/env python3
"""
XLSX to Markdown Converter - 改进版
使用统一的工具模块，代码更简洁，功能更强大
"""

import argparse
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import warnings
from tqdm import tqdm
from datetime import datetime

# 导入工具模块
try:
    from utils import (
        safe_json_loads, safe_json_dumps,
        ensure_directory, safe_write_file, get_file_hash,
        setup_logging, get_logger, ProgressTracker
    )
    TOOLS_AVAILABLE = True
except ImportError:
    TOOLS_AVAILABLE = False
    import json
    import hashlib
    import logging
    
    # 简单的回退实现
    def safe_json_loads(text, default=None):
        if default is None:
            default = {}
        try:
            return json.loads(text)
        except:
            return default
    
    def safe_json_dumps(obj, **kwargs):
        return json.dumps(obj, **kwargs)
    
    def ensure_directory(path):
        Path(path).mkdir(parents=True, exist_ok=True)
        return Path(path)
    
    def safe_write_file(file_path, content, encoding='utf-8', backup=False):
        path = Path(file_path)
        ensure_directory(path.parent)
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        return path
    
    def get_file_hash(file_path, algorithm='sha256'):
        path = Path(file_path)
        hash_func = getattr(hashlib, algorithm, hashlib.sha256)
        with open(path, 'rb') as f:
            return hash_func(f.read()).hexdigest()
    
    def setup_logging(level="INFO", **kwargs):
        logging.basicConfig(level=getattr(logging, level.upper()), 
                          format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        return logging.getLogger()
    
    def get_logger(name):
        return logging.getLogger(name)
    
    class ProgressTracker:
        def __init__(self, total, description="处理进度"):
            self.total = total
            self.description = description
            self.current = 0
        
        def update(self, increment=1):
            self.current += increment
        
        def complete(self):
            pass

warnings.filterwarnings('ignore')

# 设置日志
logger = get_logger(__name__)


class ExcelToMarkdownConverter:
    """Excel文件转Markdown转换器 - 改进版"""
    
    def __init__(self, chunk_size: int = 1000, max_rows_per_page: int = 500):
        """
        初始化转换器
        
        Args:
            chunk_size: 分块处理的行数
            max_rows_per_page: 每个Markdown页面的最大行数
        """
        self.chunk_size = chunk_size
        self.max_rows_per_page = max_rows_per_page
        logger.info(f"初始化转换器: chunk_size={chunk_size}, max_rows_per_page={max_rows_per_page}")
    
    def get_engine_for_file(self, file_path: str) -> str:
        """根据文件扩展名获取合适的引擎"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.xlsx':
            return 'openpyxl'
        elif ext == '.xls':
            try:
                import xlrd
                return 'xlrd'
            except ImportError:
                logger.warning("xlrd未安装，尝试使用openpyxl读取.xls文件")
                return 'openpyxl'
        else:
            return 'openpyxl'
    
    def read_excel_file(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """
        安全读取Excel文件
        
        Args:
            file_path: Excel文件路径
            
        Returns:
            包含sheet名和DataFrame的字典
        """
        file_name = Path(file_path).name
        logger.info(f"开始读取Excel文件: {file_name}")
        
        engines_to_try = []
        ext = Path(file_path).suffix.lower()
        
        if ext == '.xlsx':
            engines_to_try = ['openpyxl', 'xlrd']
        elif ext == '.xls':
            engines_to_try = ['xlrd', 'openpyxl']
        else:
            engines_to_try = ['openpyxl', 'xlrd']
        
        for engine in engines_to_try:
            try:
                logger.debug(f"尝试使用 {engine} 引擎")
                excel_file = pd.ExcelFile(file_path, engine=engine)
                sheets = {}
                
                for sheet_name in excel_file.sheet_names:
                    try:
                        df = pd.read_excel(
                            excel_file,
                            sheet_name=sheet_name,
                            dtype=str,
                            na_filter=False,
                            engine=engine
                        )
                        sheets[sheet_name] = df
                        logger.debug(f"读取sheet页: {sheet_name} ({len(df)}行×{len(df.columns)}列)")
                    except Exception as e:
                        logger.warning(f"读取sheet页 {sheet_name} 失败: {e}")
                        sheets[sheet_name] = pd.DataFrame()
                
                logger.info(f"成功读取文件: {file_name} (引擎: {engine}, sheet页: {len(sheets)})")
                return sheets
                
            except ImportError:
                logger.debug(f"引擎 {engine} 不可用")
                continue
            except Exception as e:
                logger.warning(f"使用引擎 {engine} 读取失败: {e}")
                continue
        
        raise ValueError(f"无法读取Excel文件: {file_name}")
    
    def should_skip_conversion(self, input_file: Path, output_file: Path) -> bool:
        """
        检查是否应该跳过转换（幂等检测）
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            
        Returns:
            是否应该跳过
        """
        if not output_file.exists():
            return False
        
        try:
            content = safe_write_file.__wrapped__.__globals__.get('safe_read_file', 
                lambda p: Path(p).read_text(encoding='utf-8'))(output_file)
            
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            
            if json_match:
                summary = safe_json_loads(json_match.group(1), default={})
                if summary.get('file_name') == input_file.name:
                    logger.info(f"检测到已转换文件: {input_file.name}")
                    return True
        except Exception as e:
            logger.debug(f"幂等检测失败: {e}")
        
        return False
    
    def convert_single_file(self, input_path: str, output_path: str, force: bool = False) -> bool:
        """
        转换单个Excel文件
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            force: 是否强制重新转换
            
        Returns:
            是否成功
        """
        input_file = Path(input_path)
        output_file = Path(output_path)
        
        if not input_file.exists():
            logger.error(f"输入文件不存在: {input_path}")
            return False
        
        # 幂等检测
        if not force and self.should_skip_conversion(input_file, output_file):
            print(f"✓ 跳过已转换文件: {input_file.name}")
            return True
        
        print(f"处理文件: {input_file.name}")
        
        try:
            # 读取Excel文件
            sheets = self.read_excel_file(input_path)
            
            if not sheets:
                logger.error(f"Excel文件没有可读取的数据: {input_path}")
                return False
            
            # 生成Markdown内容
            markdown_content = self._generate_markdown(input_file, sheets)
            
            # 写入文件
            safe_write_file(output_file, markdown_content, backup=True)
            
            print(f"✓ 转换完成: {output_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"转换文件 {input_path} 时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_markdown(self, input_file: Path, sheets: Dict[str, pd.DataFrame]) -> str:
        """
        生成Markdown内容
        
        Args:
            input_file: 输入文件路径
            sheets: Excel数据字典
            
        Returns:
            Markdown内容
        """
        lines = []
        
        # 文件头
        lines.append(f"# Excel转Markdown - {input_file.stem}")
        lines.append("")
        lines.append(f"**源文件**: `{input_file.name}`")
        lines.append(f"**转换时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**文件哈希**: {get_file_hash(input_file)}")
        lines.append("")
        
        # sheet页信息
        total_rows = sum(len(df) for df in sheets.values())
        total_columns = sum(len(df.columns) for df in sheets.values())
        
        lines.append(f"**总sheet页**: {len(sheets)}")
        lines.append(f"**总行数**: {total_rows:,}")
        lines.append(f"**总列数**: {total_columns:,}")
        lines.append("")
        
        # 每个sheet页的内容
        progress = ProgressTracker(len(sheets), "处理sheet页")
        
        for sheet_name, df in sheets.items():
            lines.append(f"## 📄 {sheet_name}")
            lines.append("")
            
            # sheet页统计
            lines.append(f"*行数*: {len(df):,} | *列数*: {len(df.columns):,}")
            lines.append("")
            
            # 列信息
            if len(df.columns) <= 20:
                lines.append("**列名**: " + ", ".join(f"`{col}`" for col in df.columns))
                lines.append("")
            
            # 数据表格
            if not df.empty:
                markdown_table = self._dataframe_to_markdown(df)
                lines.append(markdown_table)
            
            lines.append("")
            progress.update()
        
        progress.complete()
        
        # JSON摘要
        summary = self._create_summary(input_file, sheets)
        lines.append("---")
        lines.append("### 文件摘要")
        lines.append("```json")
        lines.append(safe_json_dumps(summary, indent=2, ensure_ascii=False))
        lines.append("```")
        
        return "\n".join(lines)
    
    def _dataframe_to_markdown(self, df: pd.DataFrame) -> str:
        """将DataFrame转换为Markdown表格"""
        if df.empty:
            return "*空表格*"
        
        # 处理大表格分页
        total_rows = len(df)
        if total_rows <= self.max_rows_per_page:
            return self._df_to_markdown_simple(df)
        else:
            result = []
            num_pages = (total_rows + self.max_rows_per_page - 1) // self.max_rows_per_page
            
            for page in range(num_pages):
                start_idx = page * self.max_rows_per_page
                end_idx = min((page + 1) * self.max_rows_per_page, total_rows)
                
                page_df = df.iloc[start_idx:end_idx]
                result.append(f"### 第 {page + 1} 页 ({start_idx + 1}-{end_idx} 行)")
                result.append("")
                result.append(self._df_to_markdown_simple(page_df))
                result.append("")
            
            return "\n".join(result)
    
    def _df_to_markdown_simple(self, df: pd.DataFrame) -> str:
        """简单的DataFrame转Markdown实现，不依赖tabulate"""
        if df.empty:
            return "*空表格*"
        
        # 获取列名
        columns = df.columns.tolist()
        
        # 构建Markdown表格
        lines = []
        
        # 表头
        header = "| " + " | ".join(str(col) for col in columns) + " |"
        lines.append(header)
        
        # 分隔线
        separator = "| " + " | ".join(["---"] * len(columns)) + " |"
        lines.append(separator)
        
        # 数据行
        for _, row in df.iterrows():
            # 处理每个单元格的值，避免None和NaN
            row_values = []
            for col in columns:
                value = row[col]
                if pd.isna(value):
                    row_values.append("")
                else:
                    # 转义管道符，避免破坏表格结构
                    row_values.append(str(value).replace("|", "\\|"))
            
            row_line = "| " + " | ".join(row_values) + " |"
            lines.append(row_line)
        
        return "\n".join(lines)
    
    def _create_summary(self, input_file: Path, sheets: Dict[str, pd.DataFrame]) -> Dict:
        """创建文件摘要"""
        total_rows = sum(len(df) for df in sheets.values())
        total_columns = sum(len(df.columns) for df in sheets.values())
        
        sheets_info = {}
        for sheet_name, df in sheets.items():
            sheets_info[sheet_name] = {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": df.columns.tolist()
            }
        
        return {
            "file_name": input_file.name,
            "file_path": str(input_file),
            "file_hash": get_file_hash(input_file),
            "conversion_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "total_sheets": len(sheets),
            "total_rows": total_rows,
            "total_columns": total_columns,
            "sheets_info": sheets_info
        }
    
    def convert_directory(self, input_dir: str, output_dir: str, force: bool = False) -> Dict[str, bool]:
        """
        转换目录下的所有Excel文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            force: 是否强制重新转换
            
        Returns:
            转换结果字典
        """
        results = {}
        
        # 创建输出目录
        ensure_directory(output_dir)
        
        # 查找所有Excel文件
        excel_extensions = ['.xlsx', '.xls', '.xlsm', '.xlsb']
        excel_files = []
        for ext in excel_extensions:
            excel_files.extend(Path(input_dir).glob(f"*{ext}"))
        
        if not excel_files:
            logger.warning(f"在目录 {input_dir} 中没有找到Excel文件")
            return results
        
        logger.info(f"找到 {len(excel_files)} 个Excel文件")
        
        # 处理每个文件
        for excel_file in tqdm(excel_files, desc="处理文件"):
            output_file = Path(output_dir) / f"{excel_file.stem}.md"
            success = self.convert_single_file(str(excel_file), str(output_file), force)
            results[excel_file.name] = success
        
        return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='将Excel文件转换为Markdown格式 - 改进版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转换单个文件
  python xlsx2md_improved.py -i data.xlsx -o data.md
  
  # 批量转换目录
  python xlsx2md_improved.py -d ./excel_files -od ./markdown_output
  
  # 强制重新转换
  python xlsx2md_improved.py -i data.xlsx -o data.md -f
        """
    )
    
    parser.add_argument('--input', '-i', type=str, help='输入Excel文件路径')
    parser.add_argument('--output', '-o', type=str, help='输出Markdown文件路径')
    parser.add_argument('--dir', '-d', type=str, help='输入目录路径（转换所有Excel文件）')
    parser.add_argument('--output_dir', '-od', type=str, default='./markdown_output',
                       help='输出目录路径（默认: ./markdown_output）')
    parser.add_argument('--chunk_size', '-c', type=int, default=1000,
                       help='分块处理的行数（默认: 1000）')
    parser.add_argument('--max_rows', '-m', type=int, default=500,
                       help='每个Markdown页面的最大行数（默认: 500）')
    parser.add_argument('--force', '-f', action='store_true',
                       help='强制重新转换，即使输出文件已存在')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='详细输出模式')
    
    args = parser.parse_args()
    
    # 设置日志级别
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(level=log_level)
    
    # 创建转换器
    converter = ExcelToMarkdownConverter(
        chunk_size=args.chunk_size,
        max_rows_per_page=args.max_rows
    )
    
    # 处理单个文件
    if args.input:
        if not args.output:
            # 自动生成输出文件名
            input_path = Path(args.input)
            args.output = f"{input_path.stem}.md"
        
        success = converter.convert_single_file(args.input, args.output, args.force)
        sys.exit(0 if success else 1)
    
    # 处理目录
    elif args.dir:
        results = converter.convert_directory(args.dir, args.output_dir, args.force)
        
        # 统计结果
        total = len(results)
        successful = sum(1 for success in results.values() if success)
        
        print(f"\n{'='*50}")
        print(f"转换完成!")
        print(f"总文件数: {total}")
        print(f"成功: {successful}")
        print(f"失败: {total - successful}")
        print(f"{'='*50}")
        
        sys.exit(0 if successful == total else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()