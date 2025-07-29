# 快速部署命令

## 一键部署脚本

将以下命令复制粘贴到终端中执行：

```bash
# 1. 停止所有服务
./stop.sh

# 2. 清理临时文件
rm -rf cache/* flask-service/data/* *.log *.pid flask-service/*.log flask-service/*.pid frontend/*.log frontend/*.pid
cd frontend && rm -rf node_modules/.vite && cd ..

# 3. 检查 Git 状态
git status

# 4. 添加远程仓库（如果尚未添加）
git remote add origin https://github.com/ray9919/strands_agent_exam_generator.git

# 5. 添加所有文件
git add .

# 6. 提交更改
git commit -m "Initial commit: AI Exam Generator with Strands Agent Framework

- Complete exam generation system with backend, frontend, and Flask service
- AWS Bedrock integration for Claude AI models  
- Multi-language support (Chinese/English)
- Multiple question types: single choice, multiple choice, fill-in-blank
- Reference material processing and caching system
- Security best practices for AWS credentials
- Comprehensive documentation and setup scripts"

# 7. 推送到 GitHub
git push -u origin main
```

## 如果遇到问题

### 远程仓库已存在内容
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

### 认证问题
```bash
# 使用个人访问令牌
git remote set-url origin https://[username]:[token]@github.com/ray9919/strands_agent_exam_generator.git
```

### 检查远程仓库配置
```bash
git remote -v
```

## 验证部署成功
访问: https://github.com/ray9919/strands_agent_exam_generator