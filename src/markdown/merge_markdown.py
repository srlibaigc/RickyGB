#!/usr/bin/env python3
"""
Markdown文件合并工具
将目录下的所有.md文件合并为一个带目录的.md文件
"""

import sys
import argparse
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from utils.logging_utils import setup_logging, get_logger


logger = get_logger(__name__)

class MarkdownMerger:
    """Markdown文件合并器"""
    
    def __init__(self):
        self.file_count = 0
        self.total_lines = 0
        
    def find_markdown_files(self, directory: Path, recursive: bool = True) -> List[Path]:
        """
        查找目录中的所有Markdown文件
        
        Args:
            directory: 目录路径
            recursive: 是否递归查找子目录
            
        Returns:
            Markdown文件路径列表
        """
        md_files = []
        
        if recursive:
            # 递归查找所有.md文件
            for md_file in directory.rglob("*.md"):
                if md_file.is_file():
                    md_files.append(md_file)
        else:
            # 只查找当前目录
            for md_file in directory.glob("*.md"):
                if md_file.is_file():
                    md_files.append(md_file)
        
        # 按文件名排序（自然排序）
        md_files.sort(key=lambda x: x.name.lower())
        
        return md_files
    
    def extract_title_from_file(self, file_path: Path) -> Tuple[str, str]:
        """
        从Markdown文件中提取标题
        
        Args:
            file_path: 文件路径
            
        Returns:
            (标题, 提取方法)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 方法1: 查找第一个一级标题
            match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if match:
                return match.group(1).strip(), "一级标题"
            
            # 方法2: 查找第一个二级标题
            match = re.search(r'^##\s+(.+)$', content, re.MULTILINE)
            if match:
                return match.group(1).strip(), "二级标题"
            
            # 方法3: 使用第一行非空行
            lines = content.strip().split('\n')
            for line in lines:
                if line.strip():
                    # 移除Markdown标记
                    clean_line = re.sub(r'^#+\s*', '', line.strip())
                    if clean_line:
                        return clean_line[:100], "第一行"
            
            # 方法4: 使用文件名
            return file_path.stem.replace('_', ' ').replace('-', ' ').title(), "文件名"
            
        except Exception as e:
            logger.warning(
                "提取标题失败，使用文件名兜底 | file=%s | reason=%s",
                file_path,
                e,
            )
            return file_path.stem, "文件名（错误）"
    
    def generate_table_of_contents(self, files: List[Path], base_dir: Path) -> str:
        """
        生成目录
        
        Args:
            files: 文件列表
            base_dir: 基础目录（用于计算相对路径）
            
        Returns:
            目录Markdown文本
        """
        if not files:
            return "## 目录\n\n（无Markdown文件）\n\n"
        
        toc_lines = ["## 📚 目录\n\n"]
        
        for i, file_path in enumerate(files, 1):
            # 计算相对路径
            rel_path = file_path.relative_to(base_dir) if file_path.is_relative_to(base_dir) else file_path
            
            # 提取标题
            title, method = self.extract_title_from_file(file_path)
            
            # 创建目录项
            toc_lines.append(f"{i}. **[{title}](#{self.slugify(title)})**  \n")
            toc_lines.append(f"   `{rel_path}`  \n")
        
        toc_lines.append("\n---\n\n")
        return ''.join(toc_lines)
    
    def slugify(self, text: str) -> str:
        """
        将文本转换为URL友好的slug
        
        Args:
            text: 原始文本
            
        Returns:
            slug字符串
        """
        # 转换为小写，替换空格为连字符，移除特殊字符
        slug = text.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # 移除特殊字符
        slug = re.sub(r'[\s_-]+', '-', slug)  # 替换空格和连字符
        slug = slug.strip('-')  # 移除首尾连字符
        return slug
    
    def merge_files(self, input_dir: Path, output_file: Path, 
                   recursive: bool = True, 
                   include_toc: bool = True,
                   add_separators: bool = True) -> Dict:
        """
        合并Markdown文件
        
        Args:
            input_dir: 输入目录
            output_file: 输出文件
            recursive: 是否递归查找
            include_toc: 是否包含目录
            add_separators: 是否添加文件分隔符
            
        Returns:
            合并统计信息
        """
        # 验证输入目录
        if not input_dir.exists():
            raise FileNotFoundError(f"输入目录不存在: {input_dir}")
        
        if not input_dir.is_dir():
            raise ValueError(f"输入路径不是目录: {input_dir}")
        
        # 查找Markdown文件
        md_files = self.find_markdown_files(input_dir, recursive)
        
        if not md_files:
            logger.warning("目录中没有找到Markdown文件 | input_dir=%s", input_dir)
            return {'success': False, 'error': '没有找到.md文件'}

        logger.info("发现Markdown文件 | count=%s | input_dir=%s", len(md_files), input_dir)
        
        # 准备输出
        output_content = []
        stats = {
            'input_dir': str(input_dir),
            'output_file': str(output_file),
            'file_count': len(md_files),
            'files_processed': [],
            'start_time': datetime.now().isoformat(),
            'total_lines': 0,
            'total_size': 0
        }
        
        # 添加文件头
        output_content.append(f"# 📄 合并Markdown文档\n\n")
        output_content.append(f"**来源目录**: `{input_dir}`  \n")
        output_content.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        output_content.append(f"**文件数量**: {len(md_files)}  \n\n")
        output_content.append("---\n\n")
        
        # 添加目录
        if include_toc:
            toc = self.generate_table_of_contents(md_files, input_dir)
            output_content.append(toc)
        
        # 合并文件内容
        for i, file_path in enumerate(md_files, 1):
            file_start_time = datetime.now()
            
            try:
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 计算文件信息
                file_size = file_path.stat().st_size
                file_lines = content.count('\n') + 1
                
                # 提取标题
                title, method = self.extract_title_from_file(file_path)
                
                # 计算相对路径
                rel_path = file_path.relative_to(input_dir) if file_path.is_relative_to(input_dir) else file_path
                
                # 添加文件分隔符
                if add_separators and i > 1:
                    output_content.append("\n" + "=" * 80 + "\n\n")
                
                # 添加文件标题和元信息
                output_content.append(f"## 📝 {title}\n\n")
                output_content.append(f"**文件**: `{rel_path}`  \n")
                output_content.append(f"**大小**: {file_size:,} 字节  \n")
                output_content.append(f"**行数**: {file_lines} 行  \n")
                output_content.append(f"**标题来源**: {method}  \n")
                output_content.append(f"**合并顺序**: 第 {i} 个文件  \n\n")
                output_content.append("---\n\n")
                
                # 添加文件内容
                output_content.append(content)
                
                # 确保内容以换行结束
                if not content.endswith('\n'):
                    output_content.append('\n')
                
                # 更新统计
                self.file_count += 1
                self.total_lines += file_lines
                
                # 记录文件处理信息
                file_stats = {
                    'file': str(file_path),
                    'relative_path': str(rel_path),
                    'title': title,
                    'title_source': method,
                    'size': file_size,
                    'lines': file_lines,
                    'order': i,
                    'processing_time': (datetime.now() - file_start_time).total_seconds()
                }
                stats['files_processed'].append(file_stats)
                stats['total_lines'] += file_lines
                stats['total_size'] += file_size

                logger.info(
                    "文件处理完成 | order=%s/%s | relative_path=%s | title=%s | title_source=%s | size_bytes=%s | lines=%s | elapsed_seconds=%.3f",
                    i,
                    len(md_files),
                    rel_path,
                    title,
                    method,
                    file_size,
                    file_lines,
                    file_stats['processing_time'],
                )

            except Exception as e:
                logger.error(
                    "文件处理失败 | file=%s | order=%s/%s | elapsed_seconds=%.3f | reason=%s",
                    file_path,
                    i,
                    len(md_files),
                    (datetime.now() - file_start_time).total_seconds(),
                    e,
                )
                
                # 添加错误信息到输出
                output_content.append(f"## ❌ 文件处理失败: {file_path.name}\n\n")
                output_content.append(f"错误: {e}\n\n")
                output_content.append("---\n\n")
        
        # 添加文件尾
        output_content.append("\n" + "=" * 80 + "\n\n")
        output_content.append("## 📊 合并统计\n\n")
        output_content.append(f"**总文件数**: {len(md_files)}  \n")
        output_content.append(f"**总行数**: {stats['total_lines']:,}  \n")
        output_content.append(f"**总大小**: {stats['total_size']:,} 字节  \n")
        output_content.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        output_content.append(f"**处理耗时**: {(datetime.now() - datetime.fromisoformat(stats['start_time'])).total_seconds():.1f} 秒  \n\n")
        
        # 写入输出文件
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(''.join(output_content))

            output_size = output_file.stat().st_size
            logger.info(
                "合并输出写入完成 | output_file=%s | output_size_bytes=%s | file_count=%s | total_lines=%s",
                output_file,
                output_size,
                len(md_files),
                stats['total_lines'],
            )
            
            stats['success'] = True
            stats['output_size'] = output_size
            stats['end_time'] = datetime.now().isoformat()
            stats['processing_time'] = (datetime.fromisoformat(stats['end_time']) - 
                                       datetime.fromisoformat(stats['start_time'])).total_seconds()
            
            return stats

        except Exception as e:
            logger.error(
                "写入输出文件失败 | output_file=%s | reason=%s",
                output_file,
                e,
            )
            return {'success': False, 'error': str(e)}

def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(
        description='合并目录中的Markdown文件为一个带目录的文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 合并当前目录的所有.md文件
  python merge_markdown.py --dir . --output merged.md
  
  # 递归合并子目录
  python merge_markdown.py --dir docs --output combined.md --recursive
  
  # 不生成目录
  python merge_markdown.py --dir . --output simple.md --no-toc
  
  # 输出最终摘要（默认关闭）
  python merge_markdown.py --dir docs --output combined.md --print-summary

  # 生成示例Markdown文件
  python generate_sample_markdown.py --output-dir sample_markdown --count 3
        """
    )
    
    # 主要参数
    parser.add_argument('--dir', '-d', type=str, default='.',
                       help='输入目录路径 (默认: 当前目录)')
    parser.add_argument('--output', '-o', type=str, default='merged_document.md',
                       help='输出文件路径 (默认: merged_document.md)')
    
    # 选项参数
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='递归查找子目录中的.md文件')
    parser.add_argument('--no-toc', action='store_true',
                       help='不生成目录')
    parser.add_argument('--no-separators', action='store_true',
                       help='不添加文件分隔符')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help='日志级别 (默认: INFO)')
    parser.add_argument('--log-file', type=str, default=None,
                       help='可选日志文件路径')
    parser.add_argument('--print-summary', action='store_true',
                       help='输出CLI最终摘要')

    args = parser.parse_args()

    setup_logging(level=args.log_level, log_file=args.log_file)

    merger = MarkdownMerger()

    # 正常合并模式
    input_dir = Path(args.dir)
    output_file = Path(args.output)

    logger.info(
        "开始合并Markdown文件 | input_dir=%s | output_file=%s | recursive=%s | include_toc=%s | add_separators=%s",
        input_dir,
        output_file,
        args.recursive,
        not args.no_toc,
        not args.no_separators,
    )
    
    try:
        result = merger.merge_files(
            input_dir,
            output_file,
            recursive=args.recursive,
            include_toc=not args.no_toc,
            add_separators=not args.no_separators
        )

        if result.get('success', False):
            logger.info(
                "Markdown合并执行成功 | output_file=%s | file_count=%s | total_lines=%s | processing_time_seconds=%.3f",
                output_file,
                result['file_count'],
                result['total_lines'],
                result['processing_time'],
            )
            if args.print_summary:
                print(f"✅ 合并完成: {output_file}")
                print(
                    f"文件数={result['file_count']} | 总行数={result['total_lines']:,} | "
                    f"处理时间={result['processing_time']:.1f}s"
                )
            return 0
        else:
            logger.error(
                "Markdown合并执行失败 | input_dir=%s | output_file=%s | reason=%s",
                input_dir,
                output_file,
                result.get('error', '未知错误'),
            )
            if args.print_summary:
                print(f"❌ 合并失败: {result.get('error', '未知错误')}")
            return 1

    except Exception as e:
        logger.exception(
            "合并过程中发生未捕获异常 | input_dir=%s | output_file=%s | reason=%s",
            input_dir,
            output_file,
            e,
        )
        if args.print_summary:
            print(f"💥 合并过程中发生错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
