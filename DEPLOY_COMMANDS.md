# 部署到新仓库的具体命令

## 当前状态
- 现有远程仓库: https://github.com/Anya2089/exam_generator_strands.git
- 目标仓库: https://github.com/ray9919/strands_agent_exam_generator.git

## 执行步骤

### 1. 停止服务并清理文件
```bash
# 停止所有运行中的服务
./stop.sh

# 清理临时文件和日志
rm -rf cache/*
rm -rf flask-service/data/*
rm -f *.log *.pid
rm -f flask-service/*.log flask-service/*.pid  
rm -f frontend/*.log frontend/*.pid

# 清理前端缓存
cd frontend
rm -rf node_modules/.vite
cd ..
```

### 2. 更新远程仓库地址
```bash
# 更改远程仓库地址到新的目标仓库
git remote set-url origin https://github.com/ray9919/strands_agent_exam_generator.git

# 验证远程仓库地址已更新
git remote -v
```

### 3. 准备提交
```bash
# 查看当前状态
git status

# 添加所有文件（.gitignore 会自动排除不需要的文件）
git add .

# 查看将要提交的文件
git status
```

### 4. 提交更改
```bash
git commit -m "Initial commit: AI Exam Generator with Strands Agent Framework

Features:
- Complete exam generation system with backend, frontend, and Flask service
- AWS Bedrock integration for Claude AI models
- Multi-language support (Chinese/English)  
- Multiple question types: single choice, multiple choice, fill-in-blank
- Reference material processing and caching system
- Security best practices for AWS credentials management
- Comprehensive documentation and setup scripts
- Added .gitignore for security and clean repository"
```

### 5. 推送到新仓库
```bash
# 推送到新的远程仓库
git push -u origin main
```

## 如果目标仓库不为空

如果目标仓库已经有内容，可能需要强制推送或合并：

### 选项 A: 强制推送（会覆盖远程内容）
```bash
git push -f origin main
```

### 选项 B: 先拉取再推送（保留远程内容）
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

## 验证部署

### 1. 检查远程仓库
访问 https://github.com/ray9919/strands_agent_exam_generator 确认文件已上传

### 2. 本地验证
```bash
# 检查远程分支
git branch -r

# 检查最新提交
git log --oneline -5
```

## 完整的一键执行脚本

```bash
#!/bin/bash
echo "开始部署到 GitHub 仓库..."

# 停止服务
echo "1. 停止服务..."
./stop.sh

# 清理文件
echo "2. 清理临时文件..."
rm -rf cache/* flask-service/data/* *.log *.pid flask-service/*.log flask-service/*.pid frontend/*.log frontend/*.pid
cd frontend && rm -rf node_modules/.vite && cd ..

# 更新远程仓库
echo "3. 更新远程仓库地址..."
git remote set-url origin https://github.com/ray9919/strands_agent_exam_generator.git

# 添加文件
echo "4. 添加文件到 Git..."
git add .

# 提交
echo "5. 提交更改..."
git commit -m "Initial commit: AI Exam Generator with Strands Agent Framework

Features:
- Complete exam generation system with backend, frontend, and Flask service
- AWS Bedrock integration for Claude AI models
- Multi-language support (Chinese/English)  
- Multiple question types: single choice, multiple choice, fill-in-blank
- Reference material processing and caching system
- Security best practices for AWS credentials management
- Comprehensive documentation and setup scripts
- Added .gitignore for security and clean repository"

# 推送
echo "6. 推送到 GitHub..."
git push -u origin main

echo "部署完成！"
echo "请访问 https://github.com/ray9919/strands_agent_exam_generator 查看结果"
```

## 注意事项

1. **确保有推送权限**: 确认你有目标仓库的写入权限
2. **备份重要数据**: 在执行前确保重要数据已备份
3. **检查敏感信息**: 确认没有敏感信息被提交
4. **网络连接**: 确保网络连接稳定

## 故障排除

### 认证失败
```bash
# 如果使用 HTTPS 认证失败，可以使用个人访问令牌
git remote set-url origin https://[username]:[personal_access_token]@github.com/ray9919/strands_agent_exam_generator.git
```

### 推送被拒绝
```bash
# 如果推送被拒绝，可能需要先拉取
git pull origin main --allow-unrelated-histories
git push origin main
```

### 查看详细错误
```bash
# 启用详细输出查看错误详情
git push -v origin main
```