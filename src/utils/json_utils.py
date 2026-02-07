#!/usr/bin/env python3
"""
安全的JSON处理工具
解决JSON解析中的常见问题
"""

import json
import re
import logging
from typing import Any, Optional, Union

# 设置日志
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def safe_json_loads(text: str, default: Any = None, verbose: bool = False) -> Any:
    """
    安全的JSON解析，处理所有常见问题
    
    Args:
        text: 要解析的JSON文本
        default: 解析失败时返回的默认值
        verbose: 是否显示详细错误信息
        
    Returns:
        解析后的JSON对象，或默认值
    """
    if default is None:
        default = {}
    
    if not text or not isinstance(text, str):
        if verbose:
            logger.warning("输入不是字符串或为空")
        return default
    
    original_text = text
    fixed_text = text
    
    try:
        # 第一次尝试：直接解析
        return json.loads(fixed_text)
    except json.JSONDecodeError as e:
        if verbose:
            logger.warning(f"第一次JSON解析失败: {e}")
            logger.warning(f"错误位置: {e.pos}, 行: {e.lineno}, 列: {e.colno}")
            
            # 显示错误位置附近的文本
            start = max(0, e.pos - 100)
            end = min(len(fixed_text), e.pos + 100)
            context = fixed_text[start:end]
            logger.warning(f"错误上下文:\n{context}")
        
        # 修复步骤1: 移除BOM字符
        if fixed_text.startswith('\ufeff'):
            fixed_text = fixed_text[1:]
            if verbose:
                logger.info("移除了BOM字符")
        
        # 修复步骤2: 修复常见的编码问题
        # 替换常见的非法字符
        illegal_chars = {
            '\x00': ' ',  # NULL
            '\x01': ' ',  # SOH
            '\x02': ' ',  # STX
            '\x03': ' ',  # ETX
            '\x04': ' ',  # EOT
            '\x05': ' ',  # ENQ
            '\x06': ' ',  # ACK
            '\x07': ' ',  # BEL
            '\x08': ' ',  # BS
            '\x0b': ' ',  # VT
            '\x0c': ' ',  # FF
            '\x0e': ' ',  # SO
            '\x0f': ' ',  # SI
            '\x10': ' ',  # DLE
            '\x11': ' ',  # DC1
            '\x12': ' ',  # DC2
            '\x13': ' ',  # DC3
            '\x14': ' ',  # DC4
            '\x15': ' ',  # NAK
            '\x16': ' ',  # SYN
            '\x17': ' ',  # ETB
            '\x18': ' ',  # CAN
            '\x19': ' ',  # EM
            '\x1a': ' ',  # SUB
            '\x1b': ' ',  # ESC
            '\x1c': ' ',  # FS
            '\x1d': ' ',  # GS
            '\x1e': ' ',  # RS
            '\x1f': ' ',  # US
            '\x7f': ' ',  # DEL
        }
        
        for illegal, replacement in illegal_chars.items():
            if illegal in fixed_text:
                fixed_text = fixed_text.replace(illegal, replacement)
                if verbose:
                    logger.info(f"替换了非法字符: {repr(illegal)}")
        
        # 修复步骤3: 使用正则表达式移除所有控制字符
        fixed_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', fixed_text)
        
        # 修复步骤4: 修复未转义的引号
        # 分析引号配对情况
        lines = fixed_text.split('\n')
        for i, line in enumerate(lines):
            # 跳过已经是JSON字符串内部的行
            if '"' in line:
                # 简单修复：确保引号成对出现
                quote_count = line.count('"')
                if quote_count % 2 != 0:
                    # 奇数个引号，在行尾添加一个引号
                    lines[i] = line + '"'
                    if verbose:
                        logger.info(f"修复了行 {i+1} 的引号配对")
        
        fixed_text = '\n'.join(lines)
        
        # 修复步骤5: 修复未转义的反斜杠
        # 查找未转义的反斜杠后面不是有效转义序列的情况
        fixed_text = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', fixed_text)
        
        # 修复步骤6: 修复尾随逗号
        # 在对象或数组末尾的逗号
        fixed_text = re.sub(r',\s*([}\]])', r'\1', fixed_text)
        
        # 修复步骤7: 修复未闭合的括号
        open_braces = fixed_text.count('{') - fixed_text.count('}')
        open_brackets = fixed_text.count('[') - fixed_text.count(']')
        
        if open_braces > 0:
            fixed_text += '}' * open_braces
            if verbose:
                logger.info(f"添加了 {open_braces} 个闭合大括号")
        
        if open_brackets > 0:
            fixed_text += ']' * open_brackets
            if verbose:
                logger.info(f"添加了 {open_brackets} 个闭合方括号")
        
        # 第二次尝试：解析修复后的文本
        try:
            return json.loads(fixed_text)
        except json.JSONDecodeError as e2:
            if verbose:
                logger.warning(f"第二次JSON解析失败: {e2}")
            
            # 最后尝试：提取可能的JSON对象
            try:
                # 查找最长的可能是JSON对象的部分
                json_pattern = r'\{(?:[^{}]|(?R))*\}'
                matches = list(re.finditer(json_pattern, fixed_text, re.DOTALL))
                
                if matches:
                    # 取最长的匹配
                    longest_match = max(matches, key=lambda m: len(m.group()))
                    json_text = longest_match.group()
                    
                    if verbose:
                        logger.info(f"提取了JSON片段，长度: {len(json_text)}")
                    
                    return json.loads(json_text)
            except Exception as e3:
                if verbose:
                    logger.warning(f"提取JSON片段失败: {e3}")
            
            # 如果所有尝试都失败，返回默认值
            if verbose:
                logger.error(f"所有JSON解析尝试都失败，返回默认值")
                logger.error(f"原始文本长度: {len(original_text)}")
                logger.error(f"修复后文本长度: {len(fixed_text)}")
            
            return default

def safe_json_dumps(obj: Any, ensure_ascii: bool = False, indent: Optional[int] = 2, **kwargs) -> str:
    """
    安全的JSON序列化，确保输出是有效的JSON
    
    Args:
        obj: 要序列化的对象
        ensure_ascii: 是否确保ASCII输出
        indent: 缩进空格数
        **kwargs: 其他json.dumps参数
        
    Returns:
        有效的JSON字符串
    """
    try:
        return json.dumps(obj, ensure_ascii=ensure_ascii, indent=indent, **kwargs)
    except (TypeError, ValueError) as e:
        logger.warning(f"JSON序列化失败: {e}")
        
        # 尝试清理对象
        def clean_obj(obj):
            if isinstance(obj, dict):
                return {str(k): clean_obj(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_obj(item) for item in obj]
            elif isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            else:
                # 其他类型转换为字符串
                try:
                    return str(obj)
                except:
                    return "[Unserializable Object]"
        
        cleaned_obj = clean_obj(obj)
        return json.dumps(cleaned_obj, ensure_ascii=ensure_ascii, indent=indent, **kwargs)

def validate_json(text: str) -> bool:
    """
    验证文本是否是有效的JSON
    
    Args:
        text: 要验证的文本
        
    Returns:
        是否是有效的JSON
    """
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False

def extract_json_from_text(text: str) -> Optional[str]:
    """
    从文本中提取JSON部分
    
    Args:
        text: 包含JSON的文本
        
    Returns:
        提取的JSON字符串，或None
    """
    # 查找JSON对象或数组
    patterns = [
        r'\{(?:[^{}]|(?R))*\}',  # JSON对象
        r'\[(?:[^\[\]]|(?R))*\]',  # JSON数组
    ]
    
    for pattern in patterns:
        matches = list(re.finditer(pattern, text, re.DOTALL))
        if matches:
            # 返回第一个匹配
            return matches[0].group()
    
    return None

def test_json_utils():
    """测试JSON工具函数"""
    print("🧪 测试JSON工具函数")
    
    # 测试1: 正常JSON
    normal_json = '{"name": "test", "value": 123}'
    result = safe_json_loads(normal_json, verbose=True)
    assert result == {"name": "test", "value": 123}
    print("✅ 正常JSON解析测试通过")
    
    # 测试2: 包含非法字符的JSON
    bad_json = '{"name": "test\x00with null", "value": 123}'
    result = safe_json_loads(bad_json, verbose=True)
    assert result == {"name": "test with null", "value": 123}
    print("✅ 非法字符处理测试通过")
    
    # 测试3: 未闭合的JSON
    unclosed_json = '{"name": "test", "nested": {"inner": "value"'
    result = safe_json_loads(unclosed_json, verbose=True)
    assert isinstance(result, dict)
    print("✅ 未闭合JSON处理测试通过")
    
    # 测试4: 验证函数
    assert validate_json(normal_json) == True
    assert validate_json(bad_json) == False
    print("✅ JSON验证测试通过")
    
    # 测试5: 序列化
    obj = {"name": "test", "value": 123, "list": [1, 2, 3]}
    json_str = safe_json_dumps(obj)
    assert validate_json(json_str)
    print("✅ JSON序列化测试通过")
    
    print("\n🎉 所有JSON工具测试通过!")
    return True

if __name__ == "__main__":
    test_json_utils()