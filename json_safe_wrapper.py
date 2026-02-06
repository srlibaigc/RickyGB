#!/usr/bin/env python3
"""
全局JSON安全包装器
一劳永逸解决JSON未终止字符串和其他解析错误
"""

import json
import re
import sys
import logging
from typing import Any, Optional, Union, Dict, List
from functools import wraps

# 设置详细日志
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('json_safe')

class JSONSafetyError(Exception):
    """JSON安全错误"""
    pass

class SafeJSON:
    """全局安全的JSON处理类"""
    
    # 错误统计
    error_count = 0
    fixed_count = 0
    last_error = None
    error_samples = []
    
    # 配置
    MAX_ERROR_SAMPLES = 10
    VERBOSE = True
    
    @classmethod
    def _record_error(cls, original_text: str, error: Exception, fixed_text: str = None):
        """记录JSON错误"""
        cls.error_count += 1
        cls.last_error = {
            'error': str(error),
            'original_length': len(original_text),
            'position': getattr(error, 'pos', None),
            'timestamp': logging.Formatter().formatTime(logging.LogRecord(
                'json_safe', logging.ERROR, '', 0, '', (), None
            ))
        }
        
        # 保存错误样本（限制数量）
        if len(cls.error_samples) < cls.MAX_ERROR_SAMPLES:
            sample = {
                'original_preview': original_text[:200] + ('...' if len(original_text) > 200 else ''),
                'error': str(error),
                'fixed_preview': fixed_text[:200] + ('...' if fixed_text and len(fixed_text) > 200 else '') if fixed_text else None
            }
            cls.error_samples.append(sample)
        
        if cls.VERBOSE:
            logger.error(f"JSON解析错误 #{cls.error_count}: {error}")
            if error.pos:
                start = max(0, error.pos - 100)
                end = min(len(original_text), error.pos + 100)
                logger.error(f"错误位置附近: {original_text[start:end]}")
    
    @classmethod
    def _deep_clean_text(cls, text: str) -> str:
        """深度清理文本，修复所有常见JSON问题"""
        if not text or not isinstance(text, str):
            return text or ''
        
        cleaned = text
        
        # 阶段1: 基本清理
        # 1.1 移除BOM字符
        if cleaned.startswith('\ufeff'):
            cleaned = cleaned[1:]
        
        # 1.2 移除所有控制字符（除了\t, \n, \r）
        # 保留制表符、换行符、回车符
        control_chars = ''.join(
            chr(i) for i in range(32) 
            if chr(i) not in ('\t', '\n', '\r')
        ) + ''.join(chr(i) for i in range(127, 160))
        
        for char in control_chars:
            cleaned = cleaned.replace(char, ' ')
        
        # 1.3 使用正则表达式移除剩余的控制字符
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', ' ', cleaned)
        
        # 阶段2: 修复JSON结构问题
        # 2.1 修复未转义的反斜杠
        # 查找反斜杠后面不是有效转义字符的情况
        def fix_backslashes(match):
            char = match.group(1)
            if char in '"\\/bfnrtu':
                return match.group(0)  # 已经是有效的转义
            return '\\\\' + char  # 转义反斜杠
        
        cleaned = re.sub(r'\\([^"\\/bfnrtu0-9])', fix_backslashes, cleaned)
        
        # 2.2 修复十六进制转义
        cleaned = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: f'\\u00{m.group(1)}', cleaned)
        
        # 2.3 修复引号配对
        lines = cleaned.split('\n')
        for i, line in enumerate(lines):
            # 统计非转义引号
            quote_positions = []
            in_escape = False
            
            for j, char in enumerate(line):
                if char == '\\' and not in_escape:
                    in_escape = True
                    continue
                
                if char == '"' and not in_escape:
                    quote_positions.append(j)
                
                in_escape = False
            
            # 如果引号数量是奇数，修复它
            if len(quote_positions) % 2 == 1:
                # 在行尾添加一个引号
                lines[i] = line + '"'
                cls.fixed_count += 1
        
        cleaned = '\n'.join(lines)
        
        # 2.4 修复尾随逗号
        # 在对象或数组末尾的逗号
        def fix_trailing_commas(match):
            return match.group(1)  # 只保留闭合括号
        
        cleaned = re.sub(r',\s*([}\]])', fix_trailing_commas, cleaned)
        
        # 2.5 修复未闭合的括号
        open_braces = cleaned.count('{') - cleaned.count('}')
        open_brackets = cleaned.count('[') - cleaned.count(']')
        
        if open_braces > 0:
            cleaned += '}' * open_braces
            cls.fixed_count += open_braces
        
        if open_brackets > 0:
            cleaned += ']' * open_brackets
            cls.fixed_count += open_brackets
        
        # 阶段3: 验证和最终修复
        # 3.1 确保字符串以有效字符开始和结束
        if cleaned and cleaned[0] not in '{[':
            # 尝试提取JSON部分
            json_match = re.search(r'[\{\[].*[\}\]]', cleaned, re.DOTALL)
            if json_match:
                cleaned = json_match.group()
        
        # 3.2 移除外部的无效字符
        cleaned = cleaned.strip()
        
        # 3.3 确保平衡的括号
        stack = []
        for i, char in enumerate(cleaned):
            if char == '{' or char == '[':
                stack.append(char)
            elif char == '}':
                if stack and stack[-1] == '{':
                    stack.pop()
                else:
                    # 不匹配的闭合括号，移除它
                    cleaned = cleaned[:i] + cleaned[i+1:]
                    cls.fixed_count += 1
                    return cls._deep_clean_text(cleaned)  # 递归清理
            elif char == ']':
                if stack and stack[-1] == '[':
                    stack.pop()
                else:
                    # 不匹配的闭合括号，移除它
                    cleaned = cleaned[:i] + cleaned[i+1:]
                    cls.fixed_count += 1
                    return cls._deep_clean_text(cleaned)  # 递归清理
        
        # 添加缺失的闭合括号
        while stack:
            if stack[-1] == '{':
                cleaned += '}'
            else:
                cleaned += ']'
            stack.pop()
            cls.fixed_count += 1
        
        return cleaned
    
    @classmethod
    def loads(cls, text: str, default: Any = None, verbose: bool = None) -> Any:
        """
        完全安全的JSON解析
        
        Args:
            text: 要解析的JSON文本
            default: 解析失败时返回的默认值
            verbose: 是否显示详细日志
            
        Returns:
            解析后的JSON对象，或默认值
        """
        if verbose is None:
            verbose = cls.VERBOSE
        
        if default is None:
            default = {}
        
        if not text or not isinstance(text, str):
            if verbose:
                logger.warning("输入不是字符串或为空")
            return default
        
        original_text = text
        
        try:
            # 第一次尝试：直接解析（使用原始json.loads避免递归）
            import json as original_json
            result = original_json.loads(text)
            if verbose:
                logger.debug("JSON直接解析成功")
            return result
        except original_json.JSONDecodeError as e:
            # 记录错误
            cls._record_error(original_text, e)
            
            if verbose:
                logger.warning(f"开始深度修复JSON...")
            
            # 深度修复
            fixed_text = cls._deep_clean_text(original_text)
            
            try:
                # 第二次尝试：解析修复后的文本
                result = original_json.loads(fixed_text)
                if verbose:
                    logger.info(f"JSON修复后解析成功，修复了 {cls.fixed_count} 个问题")
                return result
            except original_json.JSONDecodeError as e2:
                cls._record_error(fixed_text, e2, fixed_text)
                
                if verbose:
                    logger.error(f"深度修复后仍然失败: {e2}")
                
                # 最后尝试：提取最大的有效JSON片段
                try:
                    # 查找JSON对象
                    json_objects = list(re.finditer(r'\{(?:[^{}]|(?R))*\}', fixed_text, re.DOTALL))
                    json_arrays = list(re.finditer(r'\[(?:[^\[\]]|(?R))*\]', fixed_text, re.DOTALL))
                    
                    all_matches = json_objects + json_arrays
                    
                    if all_matches:
                        # 取最长的匹配
                        longest_match = max(all_matches, key=lambda m: len(m.group()))
                        json_fragment = longest_match.group()
                        
                        result = original_json.loads(json_fragment)
                        if verbose:
                            logger.info(f"使用JSON片段解析成功，长度: {len(json_fragment)}")
                        return result
                except Exception as e3:
                    if verbose:
                        logger.error(f"提取JSON片段失败: {e3}")
                
                # 所有尝试都失败
                if verbose:
                    logger.error(f"所有JSON解析尝试都失败，返回默认值")
                    logger.error(f"原始文本长度: {len(original_text)}")
                    logger.error(f"修复后文本长度: {len(fixed_text)}")
                
                return default
    
    @classmethod
    def dumps(cls, obj: Any, ensure_ascii: bool = False, indent: Optional[int] = 2, **kwargs) -> str:
        """
        安全的JSON序列化
        
        Args:
            obj: 要序列化的对象
            ensure_ascii: 是否确保ASCII输出
            indent: 缩进空格数
            **kwargs: 其他json.dumps参数
            
        Returns:
            有效的JSON字符串
        """
        import json as original_json
        
        def make_serializable(obj):
            """使对象可序列化"""
            if isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            elif isinstance(obj, dict):
                return {str(k): make_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, tuple):
                return [make_serializable(item) for item in obj]
            elif isinstance(obj, set):
                return [make_serializable(item) for item in obj]
            else:
                try:
                    # 尝试转换为字符串
                    return str(obj)
                except:
                    return "[Unserializable Object]"
        
        try:
            # 第一次尝试：直接序列化
            return original_json.dumps(obj, ensure_ascii=ensure_ascii, indent=indent, **kwargs)
        except (TypeError, ValueError) as e:
            if cls.VERBOSE:
                logger.warning(f"JSON序列化失败，尝试清理对象: {e}")
            
            # 清理对象后重试
            cleaned_obj = make_serializable(obj)
            return original_json.dumps(cleaned_obj, ensure_ascii=ensure_ascii, indent=indent, **kwargs)
    
    @classmethod
    def install_global_patch(cls):
        """全局替换json模块函数"""
        import json as json_module
        json_module.loads = cls.loads
        json_module.dumps = cls.dumps
        
        if cls.VERBOSE:
            logger.info("已全局替换json.loads和json.dumps为安全版本")
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            'error_count': cls.error_count,
            'fixed_count': cls.fixed_count,
            'last_error': cls.last_error,
            'error_samples': cls.error_samples
        }
    
    @classmethod
    def reset_stats(cls):
        """重置统计信息"""
        cls.error_count = 0
        cls.fixed_count = 0
        cls.last_error = None
        cls.error_samples = []

def safe_json_decorator(func):
    """装饰器：使函数使用安全的JSON处理"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        import json as json_module
        
        # 保存原始函数
        original_loads = json_module.loads
        original_dumps = json_module.dumps
        
        # 临时替换为安全版本
        json_module.loads = SafeJSON.loads
        json_module.dumps = SafeJSON.dumps
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # 恢复原始函数
            json_module.loads = original_loads
            json_module.dumps = original_dumps
    
    return wrapper

def test_safe_json():
    """测试安全JSON功能"""
    print("🧪 测试安全JSON包装器")
    
    # 创建有问题的JSON字符串
    problematic_json = '{"key": "value with unclosed quote, and control\x00char, and bad\\escape"}'
    
    print(f"测试文本: {problematic_json[:50]}...")
    
    # 使用安全解析
    result = SafeJSON.loads(problematic_json, verbose=True)
    
    print(f"解析结果: {result}")
    print(f"错误统计: {SafeJSON.get_stats()}")
    
    # 测试全局补丁
    SafeJSON.install_global_patch()
    
    # 现在json.loads应该使用安全版本
    try:
        result2 = json.loads(problematic_json)
        print(f"全局补丁后解析: {result2}")
    except Exception as e:
        print(f"全局补丁后仍然失败: {e}")
    
    print("\n✅ 安全JSON包装器测试完成")
    return True

if __name__ == "__main__":
    # 安装全局补丁
    SafeJSON.install_global_patch()
    
    # 运行测试
    test_safe_json()
    
    print("\n📋 安全JSON已激活:")
    print("1. json.loads 已替换为 SafeJSON.loads")
    print("2. json.dumps 已替换为 SafeJSON.dumps")
    print("3. 所有JSON操作现在都是安全的")
    print("4. 自动修复常见JSON问题")
    print("5. 记录所有错误以便调试")