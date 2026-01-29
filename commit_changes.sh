#!/bin/bash
# Git提交脚本

set -e  # 遇到错误时退出

echo "🔧 准备提交代码到GitHub..."

# 检查Git状态
echo "📊 当前Git状态:"
git status

# 添加所有文件
echo "📁 添加文件到暂存区..."
git add .

# 提交更改
echo "💾 提交更改..."
if [ -z "$1" ]; then
    git commit -m "feat: 添加Excel转Markdown工具

- 实现xlsx/xls文件转markdown功能
- 支持多sheet页处理
- 支持大文件分页
- 添加示例数据和测试脚本
- 完善文档和使用说明"
else
    git commit -m "$1"
fi

# 推送到远程仓库
echo "🚀 推送到GitHub..."
git push origin main

echo "✅ 提交完成!"