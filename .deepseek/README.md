# DeepSeek Reasoner OpenSpec 配置

此目录包含为 DeepSeek Reasoner 模型定制的 OpenSpec 配置。

## 配置说明

### 模型信息
- **模型名称**: deepseek-reasoner
- **模型提供商**: DeepSeek
- **模型类型**: 推理优化模型
- **适用场景**: 代码生成、技术设计、问题解决

### OpenSpec 集成

此配置基于 Claude Code 的 OpenSpec 配置进行适配，做了以下调整：

1. **提示词优化**: 针对 DeepSeek 模型的提示词风格进行优化
2. **工作流适配**: 确保 OpenSpec 工作流与 DeepSeek 模型兼容
3. **命令映射**: 将 OpenSpec 命令映射到 DeepSeek 环境

### 可用命令

在 Clawdbot 中使用以下命令（需要配置相应的命令映射）：

```
/opsx:new       # 开始新变更
/opsx:ff        # 快速生成规划文档
/opsx:apply     # 实施任务
/opsx:continue  # 继续当前变更
/opsx:archive   # 归档完成变更
/opsx:verify    # 验证变更
/opsx:explore   # 探索项目
```

### 配置方式

要让 Clawdbot 使用此配置，需要在 Clawdbot 配置中添加：

```yaml
# Clawdbot 配置示例
model: deepseek/deepseek-coder
openspec_config: .deepseek/
```

### 技能文件

所有技能文件已从 Claude Code 配置复制并进行了适当调整，确保与 DeepSeek 模型兼容。

### 注意事项

1. **模型特性**: DeepSeek 模型在代码生成和技术设计方面表现优秀
2. **上下文长度**: 注意模型的上下文长度限制
3. **推理能力**: 充分利用模型的推理能力进行复杂任务规划
4. **中文支持**: DeepSeek 对中文有良好的支持

### 测试验证

使用以下命令测试配置：
```bash
# 创建测试变更
openspec new change "test-deepseek-integration"

# 查看状态
openspec status --change "test-deepseek-integration"
```

### 问题排查

如果遇到问题：
1. 检查模型配置是否正确
2. 验证 OpenSpec 版本兼容性
3. 查看技能文件的兼容性
4. 确保命令映射正确

### 更新维护

当 OpenSpec 更新时，需要同步更新此配置：
1. 备份当前配置
2. 获取最新 OpenSpec 配置
3. 重新适配到 DeepSeek
4. 测试验证