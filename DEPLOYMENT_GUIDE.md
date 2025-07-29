# 代码部署指南

本文档提供将 AI 考试生成器项目提交到 GitHub 仓库的详细步骤和命令。

## 目标仓库
- **仓库地址**: https://github.com/ray9919/strands_agent_exam_generator.git
- **仓库名称**: strands_agent_exam_generator
- **所有者**: ray9919

## 前置条件

### 1. 确保 Git 已安装
```bash
git --version
```

### 2. 配置 Git 用户信息（如果尚未配置）
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. 确保有 GitHub 访问权限
- 确保你有该仓库的推送权限
- 配置 SSH 密钥或使用 HTTPS 认证

## 部署步骤

### 步骤 1: 检查当前 Git 状态
```bash
# 查看当前状态
git status

# 查看当前远程仓库配置
git remote -v
```

### 步骤 2: 添加或更新远程仓库
```bash
# 如果没有远程仓库，添加远程仓库
git remote add origin https://github.com/ray9919/strands_agent_exam_generator.git

# 如果已有远程仓库但地址不正确，更新远程仓库地址
git remote set-url origin https://github.com/ray9919/strands_agent_exam_generator.git
```

### 步骤 3: 清理和准备文件
```bash
# 停止所有运行中的服务
./stop.sh

# 清理临时文件和缓存
rm -rf cache/*
rm -rf flask-service/data/*
rm -f *.log
rm -f *.pid
rm -f flask-service/*.log
rm -f flask-service/*.pid
rm -f frontend/*.log
rm -f frontend/*.pid

# 清理 Node.js 构建缓存
cd frontend
rm -rf node_modules/.vite
cd ..
```

### 步骤 4: 添加文件到 Git
```bash
# 添加新创建的 .gitignore 文件
git add .gitignore

# 添加所有项目文件（.gitignore 会自动排除不需要的文件）
git add .

# 查看将要提交的文件
git status
```

### 步骤 5: 提交更改
```bash
# 提交更改，包含有意义的提交信息
git commit -m "Initial commit: AI Exam Generator with Strands Agent Framework

- Add complete exam generation system with backend, frontend, and Flask service
- Implement AWS Bedrock integration for Claude AI models
- Add multi-language support (Chinese/English)
- Include question types: single choice, multiple choice, fill-in-blank
- Add reference material processing and caching system
- Implement security best practices for AWS credentials
- Add comprehensive project documentation and setup scripts"
```

### 步骤 6: 推送到 GitHub
```bash
# 首次推送到远程仓库
git push -u origin main

# 如果遇到分支不匹配问题，可能需要先拉取
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## 可能遇到的问题和解决方案

### 问题 1: 认证失败
```bash
# 如果使用 HTTPS 遇到认证问题，可以使用个人访问令牌
# 在 GitHub 设置中生成个人访问令牌，然后使用以下格式：
git remote set-url origin https://[username]:[token]@github.com/ray9919/strands_agent_exam_generator.git
```

### 问题 2: 分支冲突
```bash
# 如果远程仓库已有内容，需要先合并
git pull origin main --allow-unrelated-histories
git push origin main
```

### 问题 3: 大文件问题
```bash
# 如果有大文件被意外添加，可以从暂存区移除
git reset HEAD [filename]

# 或者使用 git-lfs 处理大文件
git lfs track "*.pkl"
git lfs track "*.log"
```

## 验证部署

### 1. 检查远程仓库
访问 https://github.com/ray9919/strands_agent_exam_generator 确认文件已正确上传

### 2. 克隆测试
```bash
# 在另一个目录测试克隆
cd /tmp
git clone https://github.com/ray9919/strands_agent_exam_generator.git
cd strands_agent_exam_generator
ls -la
```

## 后续维护

### 日常提交流程
```bash
# 1. 检查状态
git status

# 2. 添加更改
git add .

# 3. 提交更改
git commit -m "描述你的更改"

# 4. 推送到远程
git push origin main
```

### 创建发布版本
```bash
# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签
git push origin v1.0.0
```

## 安全注意事项

1. **永远不要提交敏感信息**：
   - AWS 凭证
   - API 密钥
   - 密码
   - 个人信息

2. **定期检查 .gitignore**：
   - 确保所有敏感文件都被排除
   - 定期审查提交内容

3. **使用环境变量**：
   - 所有敏感配置都应通过环境变量管理
   - 在部署文档中说明需要设置的环境变量

## 团队协作

### 分支策略
```bash
# 创建功能分支
git checkout -b feature/new-feature

# 完成功能后合并到主分支
git checkout main
git merge feature/new-feature

# 删除功能分支
git branch -d feature/new-feature
```

### 代码审查
- 使用 Pull Request 进行代码审查
- 确保所有更改都经过审查后再合并到主分支

## 联系信息

如果在部署过程中遇到问题，请联系项目维护者或查看项目文档。

---

**最后更新**: $(date)
**文档版本**: 1.0