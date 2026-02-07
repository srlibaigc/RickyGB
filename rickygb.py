#!/usr/bin/env python3
"""
RickyGB - 统一入口脚本
提供所有工具的统一访问接口
"""

import sys
import os
import argparse
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))


def print_banner():
    """打印项目横幅"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                    RickyGB Toolbox                       ║
║                多功能文档处理工具箱 v1.0.0                ║
╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def show_available_tools():
    """显示可用工具"""
    print("📦 可用工具:")
    print("")
    
    tools = [
        ("excel", "Excel处理工具", [
            "xlsx2md - Excel转Markdown (原始版本)",
            "xlsx2md-improved - Excel转Markdown (改进版本)",
            "create-sample-data - 创建测试数据"
        ]),
        ("pdf", "PDF处理工具", [
            "pdf-splitter-v1 - PDF章节拆分 (基础版本)",
            "pdf-splitter-v2 - PDF章节拆分 (OCR版本)", 
            "pdf-splitter-final - PDF章节拆分 (最终版本)",
            "pdf-batch - PDF批量处理"
        ]),
        ("epub", "EPUB处理工具", [
            "epub2md - EPUB转Markdown"
        ]),
        ("markdown", "Markdown处理工具", [
            "merge-md - Markdown文件合并"
        ]),
        ("heartbeat", "心跳检测工具", [
            "heartbeat - Clawdbot网关心跳检测"
        ])
    ]
    
    for category, description, commands in tools:
        print(f"  📁 {category.upper()} - {description}")
        for cmd in commands:
            print(f"      • {cmd}")
        print("")


def run_excel_tool(tool_name, args):
    """运行Excel工具"""
    from excel import OriginalConverter, ImprovedConverter, create_sample_excel
    
    if tool_name == "xlsx2md":
        # 调用原始版本
        import excel.xlsx2md as xlsx2md_module
        sys.argv = ['xlsx2md.py'] + args
        xlsx2md_module.main()
    
    elif tool_name == "xlsx2md-improved":
        # 调用改进版本
        import excel.xlsx2md_improved as improved_module
        sys.argv = ['xlsx2md_improved.py'] + args
        improved_module.main()
    
    elif tool_name == "create-sample-data":
        # 创建测试数据
        create_sample_excel()
    
    else:
        print(f"未知的Excel工具: {tool_name}")
        return False
    
    return True


def run_pdf_tool(tool_name, args):
    """运行PDF工具"""
    if tool_name == "pdf-splitter-v1":
        from pdf import splitter_v1_main
        sys.argv = ['pdf_chapter_splitter_v1.py'] + args
        splitter_v1_main()
    
    elif tool_name == "pdf-splitter-v2":
        from pdf import splitter_v2_main
        sys.argv = ['pdf_chapter_splitter_v2.py'] + args
        splitter_v2_main()
    
    elif tool_name == "pdf-splitter-final":
        from pdf import splitter_final_main
        sys.argv = ['pdf_chapter_splitter_final.py'] + args
        splitter_final_main()
    
    elif tool_name == "pdf-batch":
        from pdf import batch_processor_main
        sys.argv = ['pdf_batch_processor.py'] + args
        batch_processor_main()
    
    else:
        print(f"未知的PDF工具: {tool_name}")
        return False
    
    return True


def run_epub_tool(tool_name, args):
    """运行EPUB工具"""
    if tool_name == "epub2md":
        from epub import epub_converter_main
        sys.argv = ['epub_to_markdown_v1.py'] + args
        epub_converter_main()
    
    else:
        print(f"未知的EPUB工具: {tool_name}")
        return False
    
    return True


def run_markdown_tool(tool_name, args):
    """运行Markdown工具"""
    if tool_name == "merge-md":
        from markdown import merge_markdown_main
        sys.argv = ['merge_markdown.py'] + args
        merge_markdown_main()
    
    else:
        print(f"未知的Markdown工具: {tool_name}")
        return False
    
    return True


def run_heartbeat_tool(tool_name, args):
    """运行心跳检测工具"""
    if tool_name == "heartbeat":
        from heartbeat import heartbeat_main
        sys.argv = ['gateway_heartbeat.py'] + args
        heartbeat_main()
    
    else:
        print(f"未知的心跳检测工具: {tool_name}")
        return False
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='RickyGB多功能文档处理工具箱',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 显示可用工具
  python rickygb.py --list
  
  # 使用Excel工具
  python rickygb.py excel xlsx2md --input data.xlsx --output data.md
  
  # 使用PDF工具
  python rickygb.py pdf pdf-splitter-final --input document.pdf --output chapters
  
  # 直接运行原始脚本 (向后兼容)
  python src/excel/xlsx2md.py --input data.xlsx --output data.md
        """
    )
    
    # 主要参数
    parser.add_argument('category', nargs='?', help='工具类别 (excel, pdf, epub, markdown, heartbeat)')
    parser.add_argument('tool', nargs='?', help='工具名称')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='工具参数')
    
    # 选项
    parser.add_argument('--list', '-l', action='store_true', help='列出所有可用工具')
    parser.add_argument('--version', '-v', action='store_true', help='显示版本信息')
    
    # 如果没有参数，显示帮助
    if len(sys.argv) == 1:
        print_banner()
        parser.print_help()
        show_available_tools()
        sys.exit(0)
    
    args = parser.parse_args()
    
    # 显示版本
    if args.version:
        print("RickyGB Toolbox v1.0.0")
        sys.exit(0)
    
    # 显示工具列表
    if args.list:
        print_banner()
        show_available_tools()
        sys.exit(0)
    
    # 运行工具
    if args.category and args.tool:
        print_banner()
        print(f"🚀 运行工具: {args.category}/{args.tool}")
        print("")
        
        success = False
        
        if args.category == "excel":
            success = run_excel_tool(args.tool, args.args)
        
        elif args.category == "pdf":
            success = run_pdf_tool(args.tool, args.args)
        
        elif args.category == "epub":
            success = run_epub_tool(args.tool, args.args)
        
        elif args.category == "markdown":
            success = run_markdown_tool(args.tool, args.args)
        
        elif args.category == "heartbeat":
            success = run_heartbeat_tool(args.tool, args.args)
        
        else:
            print(f"❌ 未知的工具类别: {args.category}")
            print("使用 --list 查看可用工具")
            sys.exit(1)
        
        if not success:
            sys.exit(1)
    
    else:
        print_banner()
        parser.print_help()
        show_available_tools()
        sys.exit(1)


if __name__ == '__main__':
    main()