# RickyGB 目录结构

## 🏗️ 项目结构概览

```
/workspaces/RickyGB/
├── .claude/                    # Claude Code 配置 (OpenSpec)
├── .deepseek/                  # DeepSeek Reasoner 配置 (OpenSpec)
├── .git/                       # Git 版本控制
├── .gitignore                  # Git 忽略文件
├── .npmrc                      # npm 配置
│
├── config/                     # 配置文件
├── docs/                       # 项目文档
├── examples/                   # 使用示例
├── memory/                     # 项目记忆文件
├── openspec/                   # OpenSpec 工作区
├── scripts/                    # 快捷脚本
├── src/                        # 源代码
├── tests/                      # 测试文件
├── venv/                       # Python 虚拟环境
│
├── CHANGELOG_2026-02-07.md     # 更新日志
├── CODE_OF_CONDUCT.md          # 行为准则
├── CONTRIBUTING.md             # 贡献指南
├── DEEPSEEK_OPENSEPC_CONFIG.md # DeepSeek 配置指南
├── DIRECTORY_STRUCTURE.md      # 本文件
├── LICENSE                     # 许可证
├── OPENSPEC_SETUP.md           # OpenSpec 配置指南
├── PROJECT_STRUCTURE.md        # 项目结构说明
├── README.md                   # 项目主文档
├── TESTING.md                  # 测试文档
├── TODO.md                     # 待办事项
└── rickygb.py                  # 统一入口脚本
```

## 📁 目录详细说明

### 1. 配置目录
- **`.claude/`** - Claude Code 的 OpenSpec 配置
  - `commands/opsx/` - OpenSpec 命令定义
  - `skills/openspec-*/` - OpenSpec 技能文件
- **`.deepseek/`** - DeepSeek Reasoner 的 OpenSpec 配置
  - 结构与 `.claude/` 相同，针对 DeepSeek 优化
- **`.git/`** - Git 版本控制数据
- **`.gitignore`** - Git 忽略规则
- **`.npmrc`** - npm 包管理器配置

### 2. 项目目录
- **`config/`** - 配置文件
  - `requirements_all.txt` - 所有依赖
  - `requirements_openspec.txt` - OpenSpec 相关依赖
- **`docs/`** - 项目文档
  - API 文档、使用指南等
- **`examples/`** - 使用示例
  - 各种功能的示例代码
- **`memory/`** - 项目记忆
  - 项目历史、决策记录等
- **`openspec/`** - OpenSpec 工作区
  - `changes/` - 变更目录
  - `specs/` - 规范目录
- **`scripts/`** - 快捷脚本
  - `xlsx2md` - Excel 转 Markdown
  - `pdf_splitter` - PDF 章节拆分
  - `epub2md` - EPUB 转 Markdown
  - `merge_md` - Markdown 文件合并
- **`src/`** - 源代码
  - `excel/` - Excel 处理模块
  - `pdf/` - PDF 处理模块
  - `epub/` - EPUB 处理模块
  - `markdown/` - Markdown 处理模块
  - `utils/` - 工具模块
  - `heartbeat/` - 心跳检测模块
- **`tests/`** - 测试文件
  - 单元测试、集成测试等
- **`venv/`** - Python 虚拟环境
  - 项目依赖隔离环境

### 3. 文档文件
- **`CHANGELOG_2026-02-07.md`** - 2026年2月7日更新日志
- **`CODE_OF_CONDUCT.md`** - 社区行为准则
- **`CONTRIBUTING.md`** - 贡献者指南
- **`DEEPSEEK_OPENSEPC_CONFIG.md`** - DeepSeek OpenSpec 配置指南
- **`DIRECTORY_STRUCTURE.md`** - 目录结构说明（本文件）
- **`LICENSE`** - MIT 许可证
- **`OPENSPEC_SETUP.md`** - OpenSpec 配置和使用指南
- **`PROJECT_STRUCTURE.md`** - 项目技术结构说明
- **`README.md`** - 项目主文档
- **`TESTING.md`** - 测试指南
- **`TODO.md`** - 待办事项和未来规划

### 4. 核心文件
- **`rickygb.py`** - 统一入口脚本
  - 所有工具的统一访问接口

## 🧹 目录清理原则

### 保留的目录
1. **必要配置** - `.claude/`, `.deepseek/`, `.git/`
2. **项目代码** - `src/`, `tests/`, `scripts/`
3. **文档资源** - `docs/`, `examples/`, `config/`
4. **工作区** - `openspec/`, `memory/`
5. **环境** - `venv/`

### 清理的目录
1. **其他 AI 工具配置** - 已清理 `.agent/`, `.amazonq/` 等 20+ 目录
2. **临时文件** - 已清理 `__pycache__/`
3. **旧版本文件** - 已清理 `README_OLD.md`

### 保持整洁的规则
1. **按功能组织** - 相关文件放在同一目录
2. **命名规范** - 使用有意义的名称
3. **定期清理** - 移除不必要的文件
4. **文档完整** - 每个目录都有说明
5. **版本控制** - 重要文件纳入 Git

## 🔧 维护指南

### 添加新文件
1. **选择合适目录** - 根据文件类型选择目录
2. **遵循命名规范** - 使用 kebab-case 或 snake_case
3. **更新文档** - 更新相关说明文件
4. **提交更改** - 及时提交到版本控制

### 清理旧文件
1. **定期检查** - 每月检查一次目录结构
2. **备份重要文件** - 清理前备份
3. **更新忽略规则** - 更新 `.gitignore`
4. **记录变更** - 在 CHANGELOG 中记录

### 目录扩展
当项目需要新功能时：
1. **创建新目录** - 如 `api/`, `web/`, `cli/`
2. **更新结构文档** - 更新本文件
3. **添加示例** - 在 `examples/` 中添加示例
4. **编写文档** - 添加使用说明

## 🎯 最佳实践

### 文件组织
1. **单一职责** - 每个文件/目录有明确职责
2. **层次清晰** - 不超过 3 层嵌套
3. **易于查找** - 文件位置直观
4. **便于维护** - 结构支持长期维护

### 命名规范
1. **Python 代码** - `snake_case.py`
2. **配置文件** - `kebab-case.ext`
3. **文档文件** - `UPPER_CASE_WITH_UNDERSCORES.md`
4. **目录名称** - `lowercase-with-dashes/`

### 版本控制
1. **代码文件** - 全部纳入版本控制
2. **配置文件** - 模板纳入，敏感数据排除
3. **生成文件** - 不纳入版本控制
4. **大文件** - 使用 Git LFS 或排除

## 📊 目录统计

### 当前状态
- **总目录数**: 15 个
- **配置文件**: 2 个 (`.claude/`, `.deepseek/`)
- **代码目录**: 4 个 (`src/`, `tests/`, `scripts/`, `venv/`)
- **文档目录**: 4 个 (`docs/`, `examples/`, `config/`, `memory/`)
- **工作区**: 1 个 (`openspec/`)
- **文档文件**: 11 个
- **代码文件**: 1 个 (`rickygb.py`)

### 清理效果
- **已清理目录**: 20+ 个不必要的 AI 工具配置
- **已清理文件**: 2 个临时/旧文件
- **结构简化**: 从混乱到清晰
- **维护性提升**: 易于理解和维护

## 🚀 使用建议

### 新开发者
1. **阅读 README** - 了解项目概况
2. **查看本文件** - 理解目录结构
3. **探索 examples** - 查看使用示例
4. **运行测试** - 验证环境配置

### 贡献者
1. **遵循结构** - 按现有模式组织代码
2. **更新文档** - 添加或更新相关文档
3. **保持整洁** - 不添加不必要的文件
4. **提交规范** - 清晰的提交信息

### 维护者
1. **定期审查** - 检查目录结构
2. **清理优化** - 移除过时内容
3. **结构演进** - 根据需求调整结构
4. **文档同步** - 确保文档与实际一致

---

## 🎉 总结

RickyGB 项目现在具有清晰、整洁的目录结构：

1. **组织合理** - 按功能清晰划分
2. **文档完整** - 每个部分都有说明
3. **易于维护** - 结构支持长期开发
4. **扩展性强** - 便于添加新功能
5. **AI 增强** - 集成 OpenSpec 支持

**保持目录整洁是项目可维护性的关键！** 🧹

---

*最后更新: 2026年2月7日*
*维护状态: 良好*