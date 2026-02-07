# 测试指南

## 环境准备

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 创建示例数据：
```bash
python create_sample_data.py
```

## 功能测试

### 测试1：转换单个文件
```bash
# 转换小型文件
python xlsx2md.py -i sample_data/sample_small.xlsx -o test_small.md

# 转换多sheet文件
python xlsx2md.py -i sample_data/sample_medium.xlsx -o test_medium.md

# 转换带文本的文件
python xlsx2md.py -i sample_data/sample_text.xlsx -o test_text.md

# 转换旧格式文件
python xlsx2md.py -i sample_data/sample_old_format.xls -o test_old.md
```

### 测试2：转换目录下所有文件
```bash
# 转换sample_data目录下所有Excel文件
python xlsx2md.py -d sample_data -od test_output
```

### 测试3：大型文件分页测试
```bash
# 测试分页功能（每页1000行）
python xlsx2md.py -i sample_data/sample_large.xlsx -o test_large.md -m 1000

# 测试更小的分页（每页500行）
python xlsx2md.py -i sample_data/sample_large.xlsx -o test_large_500.md -m 500
```

## 验证输出

检查生成的Markdown文件：
1. 文件结构是否完整
2. 表格格式是否正确
3. 多sheet页是否都包含
4. 分页功能是否正常工作
5. 特殊字符是否正确处理

## 性能测试

```bash
# 测试大型文件处理性能
time python xlsx2md.py -i sample_data/sample_large.xlsx -o perf_test.md

# 测试内存使用
/usr/bin/time -v python xlsx2md.py -i sample_data/sample_large.xlsx -o mem_test.md
```

## 边界测试

1. 空Excel文件
2. 只有一个单元格的文件
3. 包含特殊字符的文件名
4. 非常大的列数测试
5. 混合数据类型的测试