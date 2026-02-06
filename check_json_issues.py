#!/usr/bin/env python3
"""
检查JSON问题
"""

import os
import sys
import json
from pathlib import Path
from json_utils import safe_json_loads, validate_json

def check_directory_for_json_issues(directory="."):
    """检查目录中的JSON文件问题"""
    directory = Path(directory)
    
    print(f"检查目录: {directory}")
    
    json_files = list(directory.rglob("*.json"))
    
    if not json_files:
        print("没有找到JSON文件")
        return True
    
    print(f"找到 {len(json_files)} 个JSON文件")
    
    issues_found = 0
    
    for json_file in json_files:
        try:
            content = json_file.read_text(encoding='utf-8')
            
            if not validate_json(content):
                print(f"❌ JSON文件无效: {json_file}")
                issues_found += 1
                
                # 尝试修复
                fixed = safe_json_loads(content, verbose=True)
                if fixed:
                    print(f"  可以修复，解析后得到: {type(fixed)}")
                else:
                    print(f"  无法修复")
            
            else:
                print(f"✅ JSON文件有效: {json_file}")
                
        except Exception as e:
            print(f"❌ 读取文件失败: {json_file} - {e}")
            issues_found += 1
    
    if issues_found == 0:
        print("\n✅ 所有JSON文件都有效")
        return True
    else:
        print(f"\n❌ 发现 {issues_found} 个JSON问题")
        return False

def test_problematic_json():
    """测试有问题的JSON"""
    print("\n🧪 测试有问题的JSON字符串")
    
    # 模拟可能的问题
    problematic_strings = [
        # 未终止的字符串
        '{"key": "value with unclosed quote}',
        # 包含控制字符
        '{"key": "value\x00with null"}',
        # 未转义的反斜杠
        r'{"path": "C:\Users\test"}',
        # 尾随逗号
        '{"a": 1, "b": 2,}',
        # 未闭合的对象
        '{"nested": {"inner": "value"',
        # 混合问题
        '{"name": "test\x01", "list": [1,2,], "nested": {}}',
    ]
    
    for i, json_str in enumerate(problematic_strings, 1):
        print(f"\n测试 {i}: {json_str[:50]}...")
        
        try:
            # 标准解析
            json.loads(json_str)
            print("  标准解析: ✅ 通过")
        except json.JSONDecodeError as e:
            print(f"  标准解析: ❌ 失败 - {e}")
        
        # 安全解析
        result = safe_json_loads(json_str, verbose=False)
        if result:
            print(f"  安全解析: ✅ 通过 - 得到: {type(result)}")
        else:
            print(f"  安全解析: ❌ 失败")

def main():
    """主函数"""
    print("🔍 JSON问题检查工具")
    
    # 检查当前目录
    check_directory_for_json_issues()
    
    # 测试有问题的JSON
    test_problematic_json()
    
    print("\n📋 建议:")
    print("1. 在所有JSON操作中使用 safe_json_loads()")
    print("2. 写入JSON前使用 safe_json_dumps()")
    print("3. 定期运行此检查工具")
    print("4. 清理输入数据中的控制字符")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())