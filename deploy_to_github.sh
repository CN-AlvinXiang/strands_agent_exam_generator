#!/bin/bash

# AI 考试生成器 GitHub 部署脚本
# 目标仓库: https://github.com/ray9919/strands_agent_exam_generator.git

set -e  # 遇到错误时退出

echo "🚀 开始部署 AI 考试生成器到 GitHub..."
echo "目标仓库: https://github.com/ray9919/strands_agent_exam_generator.git"
echo ""

# 1. 停止服务
echo "📋 步骤 1: 停止所有服务..."
if [ -f "./stop.sh" ]; then
    ./stop.sh
    echo "✅ 服务已停止"
else
    echo "⚠️  stop.sh 文件不存在，跳过停止服务"
fi
echo ""

# 2. 清理临时文件
echo "🧹 步骤 2: 清理临时文件和缓存..."
rm -rf cache/* 2>/dev/null || true
rm -rf flask-service/data/* 2>/dev/null || true
rm -f *.log *.pid 2>/dev/null || true
rm -f flask-service/*.log flask-service/*.pid 2>/dev/null || true
rm -f frontend/*.log frontend/*.pid 2>/dev/null || true

# 清理前端缓存
if [ -d "frontend/node_modules/.vite" ]; then
    rm -rf frontend/node_modules/.vite
    echo "✅ 前端缓存已清理"
fi
echo "✅ 临时文件清理完成"
echo ""

# 3. 检查 Git 状态
echo "📊 步骤 3: 检查 Git 状态..."
git status
echo ""

# 4. 更新远程仓库地址
echo "🔗 步骤 4: 更新远程仓库地址..."
current_remote=$(git remote get-url origin 2>/dev/null || echo "无远程仓库")
echo "当前远程仓库: $current_remote"

git remote set-url origin https://github.com/ray9919/strands_agent_exam_generator.git
echo "✅ 远程仓库地址已更新"

# 验证远程仓库
echo "验证远程仓库配置:"
git remote -v
echo ""

# 5. 添加文件到 Git
echo "📁 步骤 5: 添加文件到 Git..."
git add .
echo "✅ 文件已添加到暂存区"

# 显示将要提交的文件
echo "将要提交的文件:"
git status --short
echo ""

# 6. 提交更改
echo "💾 步骤 6: 提交更改..."
commit_message="Initial commit: AI Exam Generator with Strands Agent Framework

Features:
- Complete exam generation system with backend, frontend, and Flask service
- AWS Bedrock integration for Claude AI models
- Multi-language support (Chinese/English)
- Multiple question types: single choice, multiple choice, fill-in-blank
- Reference material processing and caching system
- Security best practices for AWS credentials management
- Comprehensive documentation and setup scripts
- Added .gitignore for security and clean repository

Technical Stack:
- Backend: Python + Strands Agent Framework + Flask
- Frontend: React + TypeScript + Material-UI
- AI: AWS Bedrock (Claude models)
- Infrastructure: AWS services with proper credential management"

git commit -m "$commit_message"
echo "✅ 更改已提交"
echo ""

# 7. 推送到 GitHub
echo "🚀 步骤 7: 推送到 GitHub..."
echo "正在推送到: https://github.com/ray9919/strands_agent_exam_generator.git"

# 尝试推送
if git push -u origin main; then
    echo "✅ 推送成功！"
else
    echo "⚠️  推送失败，可能需要处理冲突..."
    echo "尝试先拉取远程更改..."
    
    if git pull origin main --allow-unrelated-histories; then
        echo "✅ 远程更改已合并"
        echo "重新推送..."
        git push origin main
        echo "✅ 推送成功！"
    else
        echo "❌ 自动合并失败，需要手动处理"
        echo "请检查冲突并手动解决"
        exit 1
    fi
fi
echo ""

# 8. 验证部署
echo "🔍 步骤 8: 验证部署..."
echo "检查远程分支:"
git branch -r

echo ""
echo "最新提交:"
git log --oneline -3
echo ""

# 完成
echo "🎉 部署完成！"
echo ""
echo "📋 部署摘要:"
echo "- 目标仓库: https://github.com/ray9919/strands_agent_exam_generator.git"
echo "- 分支: main"
echo "- 状态: 成功"
echo ""
echo "🌐 请访问以下链接查看部署结果:"
echo "https://github.com/ray9919/strands_agent_exam_generator"
echo ""
echo "📚 后续步骤:"
echo "1. 在 GitHub 上检查文件是否正确上传"
echo "2. 更新 README.md 文件（如需要）"
echo "3. 设置仓库描述和标签"
echo "4. 配置 GitHub Pages（如需要）"
echo ""
echo "✨ 部署脚本执行完成！"