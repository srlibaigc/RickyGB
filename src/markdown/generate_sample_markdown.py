#!/usr/bin/env python3
"""生成用于演示/测试的Markdown样例文件。"""

import argparse
from datetime import datetime
from pathlib import Path
import sys
from typing import List

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from utils.logging_utils import get_logger, setup_logging

logger = get_logger(__name__)


def create_sample_files(output_dir: Path, count: int = 5) -> List[Path]:
    """创建示例Markdown文件。"""
    output_dir.mkdir(parents=True, exist_ok=True)

    sample_files: List[Path] = []
    topics = [
        "Python基础", "数据结构", "算法", "Web开发", "数据库",
        "机器学习", "DevOps", "测试", "部署", "文档",
    ]

    for i in range(min(count, len(topics))):
        file_name = f"document_{i + 1:02d}_{topics[i].replace(' ', '_')}.md"
        file_path = output_dir / file_name

        content = f"""# {topics[i]}

## 概述

这是关于{topics[i]}的示例文档。

## 主要内容

1. 基本概念
2. 核心原理
3. 实际应用
4. 最佳实践

## 示例代码

```python
def example_function():
    \"\"\"示例函数\"\"\"
    print("Hello, {topics[i]}!")
    return True
```

## 总结

{topics[i]}是一个重要的技术领域，值得深入学习。

---
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        file_path.write_text(content, encoding='utf-8')
        sample_files.append(file_path)
        logger.info("示例文件已创建 | file=%s", file_path)

    return sample_files


def main() -> int:
    parser = argparse.ArgumentParser(description='生成Markdown示例文件')
    parser.add_argument('--output-dir', type=str, default='sample_markdown', help='输出目录')
    parser.add_argument('--count', type=int, default=5, help='创建文件数量')
    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    args = parser.parse_args()

    setup_logging(level=args.log_level)
    created = create_sample_files(Path(args.output_dir), args.count)
    logger.info("样例生成完成 | output_dir=%s | created_count=%s", args.output_dir, len(created))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
