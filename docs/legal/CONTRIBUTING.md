# 贡献指南

感谢您对RickyGB项目的关注！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 报告Bug
- ✨ 请求新功能
- 📖 改进文档
- 🔧 提交代码修复
- 🧪 添加测试用例

## 🚀 开始贡献

### 1. 设置开发环境

```bash
# 1. Fork项目
# 在GitHub上点击Fork按钮

# 2. 克隆你的Fork
git clone https://github.com/yourusername/RickyGB.git
cd RickyGB

# 3. 添加上游仓库
git remote add upstream https://github.com/originalowner/RickyGB.git

# 4. 创建虚拟环境
python -m venv venv

# 5. 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 6. 安装开发依赖
pip install -r config/requirements_all.txt
pip install -e .
```

### 2. 创建功能分支

```bash
# 从main分支创建新分支
git checkout -b feature/your-feature-name

# 或修复Bug
git checkout -b fix/issue-number-description
```

### 3. 开发流程

#### 代码规范
- 遵循PEP 8编码规范
- 使用有意义的变量名和函数名
- 添加必要的注释和文档字符串
- 保持函数简洁（建议不超过50行）

#### 类型注解
```python
def process_file(file_path: str, output_dir: Path) -> bool:
    """
    处理文件
    
    Args:
        file_path: 输入文件路径
        output_dir: 输出目录
        
    Returns:
        处理是否成功
    """
    # 实现代码
    return True
```

#### 测试要求
- 新功能必须包含测试用例
- 修复Bug时添加回归测试
- 测试覆盖率不应降低

### 4. 提交代码

#### 提交信息格式
```
类型(范围): 简短描述

详细描述（可选）

关联Issue: #123
```

**类型说明**:
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具

**示例**:
```
feat(excel): 添加Excel批量处理功能

- 支持目录递归处理
- 添加进度显示
- 优化内存使用

关联Issue: #45
```

### 5. 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定模块测试
python -m pytest tests/test_excel.py -v

# 检查代码风格
python -m flake8 src/ --max-line-length=100

# 类型检查
python -m mypy src/
```

### 6. 提交Pull Request

1. 确保所有测试通过
2. 更新相关文档
3. 提交到你的分支
4. 在GitHub上创建Pull Request
5. 填写PR模板，描述变更内容

## 📁 项目结构指南

### 添加新工具模块
1. 在`src/`下创建新目录（如`src/word/`）
2. 实现核心功能类
3. 创建`__init__.py`导出接口
4. 在`rickygb.py`中添加支持
5. 创建快捷脚本（可选）
6. 添加测试用例

### 修改现有模块
1. 保持向后兼容性
2. 使用`utils/`模块中的工具函数
3. 更新相关文档
4. 确保测试覆盖

### 工具模块使用
```python
# 推荐使用工具模块
from utils import (
    safe_read_file, safe_write_file,
    setup_logging, get_logger, ProgressTracker
)

# 设置日志
logger = get_logger(__name__)

# 使用工具函数
def process_data(input_path, output_path):
    content = safe_read_file(input_path)
    # 处理逻辑
    safe_write_file(output_path, processed_content)
```

## 🧪 测试指南

### 测试文件结构
```
tests/
├── test_basic.py          # 基础功能测试
├── test_excel.py         # Excel模块测试
├── test_pdf.py           # PDF模块测试
├── test_epub.py          # EPUB模块测试
├── test_markdown.py      # Markdown模块测试
├── test_utils.py         # 工具模块测试
└── conftest.py           # 测试配置
```

### 编写测试
```python
import pytest
from pathlib import Path
from src.excel import OriginalConverter

class TestExcelConverter:
    def test_basic_conversion(self, tmp_path):
        """测试基本转换功能"""
        # 准备测试数据
        input_file = tmp_path / "test.xlsx"
        output_file = tmp_path / "test.md"
        
        # 执行测试
        converter = OriginalConverter()
        result = converter.convert_single_file(str(input_file), str(output_file))
        
        # 验证结果
        assert result is True
        assert output_file.exists()
```

### 测试夹具
```python
# conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_excel_file(tmp_path):
    """创建示例Excel文件"""
    file_path = tmp_path / "sample.xlsx"
    # 创建测试文件
    return file_path
```

## 📖 文档指南

### 更新README
- 新功能添加到快速开始部分
- 更新项目结构图
- 添加使用示例

### 添加模块文档
每个模块应包含：
1. 模块级文档字符串
2. 类和方法文档字符串
3. 使用示例
4. API参考

### 创建教程
复杂功能应提供教程：
```
docs/tutorials/
├── excel-processing.md
├── pdf-splitting.md
└── epub-extraction.md
```

## 🔍 代码审查

### 审查要点
1. **功能正确性**: 代码是否按预期工作
2. **代码质量**: 是否遵循编码规范
3. **测试覆盖**: 是否有足够的测试
4. **文档更新**: 相关文档是否更新
5. **性能影响**: 是否影响现有功能性能

### 审查流程
1. 至少需要一名核心贡献者审查
2. 所有CI检查必须通过
3. 解决所有审查意见
4. 合并前确保分支是最新的

## 🐛 报告问题

### Bug报告模板
```
## 问题描述
清晰描述问题

## 重现步骤
1. 
2. 
3. 

## 预期行为
应该发生什么

## 实际行为
实际发生了什么

## 环境信息
- 操作系统:
- Python版本:
- 项目版本:
- 相关依赖版本:

## 附加信息
日志、截图等
```

### 功能请求模板
```
## 功能描述
清晰描述需要的功能

## 使用场景
为什么需要这个功能

## 建议实现
如果有实现想法

## 替代方案
考虑过的其他方案
```

## 🏆 贡献者奖励

- 贡献者名单会添加到README.md
- 重大贡献者会成为项目维护者
- 定期评选优秀贡献者

## 📞 沟通渠道

- **GitHub Issues**: 技术讨论和问题报告
- **GitHub Discussions**: 功能讨论和想法分享
- **邮件列表**: 项目公告和重要更新

## 📄 行为准则

请遵守我们的[行为准则](CODE_OF_CONDUCT.md)，确保友好、尊重的交流环境。

---

感谢您的贡献！您的每一份努力都让RickyGB变得更好。 🚀