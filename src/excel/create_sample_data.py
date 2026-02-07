#!/usr/bin/env python3
"""
创建示例Excel文件用于测试
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os

def create_sample_excel():
    """创建示例Excel文件"""
    
    # 创建示例数据目录
    data_dir = Path("sample_data")
    data_dir.mkdir(exist_ok=True)
    
    print("创建示例Excel文件...")
    
    # 示例1：小型数据表
    small_data = {
        '姓名': ['张三', '李四', '王五', '赵六'],
        '年龄': [25, 30, 35, 28],
        '城市': ['北京', '上海', '广州', '深圳'],
        '工资': [50000, 60000, 55000, 48000],
        '入职日期': ['2020-01-15', '2019-03-20', '2021-06-10', '2022-02-28']
    }
    df_small = pd.DataFrame(small_data)
    
    # 示例2：中型数据表（多个sheet）
    medium_data1 = {
        f'列_{i}': np.random.randn(100) for i in range(10)
    }
    df_medium1 = pd.DataFrame(medium_data1)
    
    medium_data2 = {
        '产品ID': [f'P{1000+i}' for i in range(50)],
        '产品名称': [f'产品{i}' for i in range(50)],
        '类别': np.random.choice(['电子', '服装', '食品', '家居'], 50),
        '价格': np.random.uniform(10, 1000, 50),
        '库存': np.random.randint(0, 1000, 50)
    }
    df_medium2 = pd.DataFrame(medium_data2)
    
    # 示例3：带有多行文本的数据
    text_data = {
        '标题': ['项目报告', '会议纪要', '技术文档'],
        '内容': [
            '这是项目报告的详细内容，包含多个段落和要点。\n第一段：项目概述\n第二段：技术实现\n第三段：风险评估',
            '会议时间：2024-01-15\n参会人员：张三、李四、王五\n会议议题：季度规划',
            '技术文档包含：\n1. 系统架构\n2. 接口设计\n3. 部署方案\n4. 测试用例'
        ],
        '状态': ['进行中', '已完成', '待审核'],
        '负责人': ['张三', '李四', '王五']
    }
    df_text = pd.DataFrame(text_data)
    
    # 创建Excel文件
    with pd.ExcelWriter(data_dir / 'sample_small.xlsx', engine='openpyxl') as writer:
        df_small.to_excel(writer, sheet_name='员工信息', index=False)
        print("✓ 创建 sample_small.xlsx")
    
    with pd.ExcelWriter(data_dir / 'sample_medium.xlsx', engine='openpyxl') as writer:
        df_medium1.to_excel(writer, sheet_name='随机数据', index=False)
        df_medium2.to_excel(writer, sheet_name='产品信息', index=False)
        print("✓ 创建 sample_medium.xlsx (2个sheet页)")
    
    with pd.ExcelWriter(data_dir / 'sample_text.xlsx', engine='openpyxl') as writer:
        df_text.to_excel(writer, sheet_name='文档记录', index=False)
        # 添加第二个sheet
        summary_data = {
            '统计项': ['总文档数', '进行中', '已完成', '待审核'],
            '数量': [3, 1, 1, 1],
            '百分比': ['100%', '33.3%', '33.3%', '33.3%']
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='统计摘要', index=False)
        print("✓ 创建 sample_text.xlsx (带多行文本)")
    
    # 创建.xls格式文件（旧格式）- 使用openpyxl兼容模式
    try:
        with pd.ExcelWriter(data_dir / 'sample_old_format.xls', engine='openpyxl') as writer:
            df_small.to_excel(writer, sheet_name='旧格式数据', index=False)
            print("✓ 创建 sample_old_format.xls (.xls格式，使用openpyxl)")
    except Exception as e:
        print(f"⚠️  创建.xls文件失败: {e}")
        print("  创建.xlsx替代文件")
        with pd.ExcelWriter(data_dir / 'sample_compatibility.xlsx', engine='openpyxl') as writer:
            df_small.to_excel(writer, sheet_name='兼容格式数据', index=False)
            print("✓ 创建 sample_compatibility.xlsx (兼容格式)")
    
    print(f"\n所有示例文件已创建到: {data_dir.absolute()}")
    print("\n文件列表:")
    for file in data_dir.glob("*.xls*"):
        print(f"  - {file.name}")
    
    return data_dir

def create_large_sample():
    """创建大型示例文件（用于测试分页功能）"""
    data_dir = Path("sample_data")
    
    print("\n创建大型示例文件...")
    
    # 创建大型数据集
    large_data = {
        f'字段_{i:03d}': np.random.randn(5000) for i in range(20)
    }
    
    # 添加一些文本字段
    large_data['ID'] = [f'ID_{i:06d}' for i in range(5000)]
    large_data['描述'] = [f'这是第{i}条记录的描述信息，包含一些详细内容。' for i in range(5000)]
    large_data['状态'] = np.random.choice(['正常', '警告', '错误', '待处理'], 5000)
    large_data['数值'] = np.random.uniform(0, 1000, 5000)
    
    df_large = pd.DataFrame(large_data)
    
    # 保存为Excel文件
    output_file = data_dir / 'sample_large.xlsx'
    df_large.to_excel(output_file, sheet_name='大数据集', index=False)
    
    print(f"✓ 创建大型文件: {output_file.name}")
    print(f"  数据规模: {len(df_large)} 行 × {len(df_large.columns)} 列")
    
    return output_file

if __name__ == "__main__":
    print("=" * 50)
    print("创建示例Excel数据")
    print("=" * 50)
    
    # 创建示例数据目录
    data_dir = create_sample_excel()
    
    # 创建大型示例文件
    large_file = create_large_sample()
    
    print("\n" + "=" * 50)
    print("示例数据创建完成！")
    print("=" * 50)
    print("\n使用方法:")
    print("1. 测试小型文件:")
    print("   python xlsx2md.py -i sample_data/sample_small.xlsx -o test_small.md")
    print("\n2. 测试多sheet文件:")
    print("   python xlsx2md.py -i sample_data/sample_medium.xlsx -o test_medium.md")
    print("\n3. 测试目录下所有文件:")
    print("   python xlsx2md.py -d sample_data -od markdown_output")
    print("\n4. 测试大型文件分页:")
    print("   python xlsx2md.py -i sample_data/sample_large.xlsx -o test_large.md -m 1000")