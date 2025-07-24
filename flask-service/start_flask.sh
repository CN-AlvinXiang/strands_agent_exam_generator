#!/bin/bash
# start_flask.sh - 启动Flask服务

# 安装依赖
pip install -r requirements.txt

# 启动Flask服务
# 使用Python 3.10虚拟环境
source "$HOME/ai_exam_venv_py310/bin/activate"
nohup python main.py > flask.log 2>&1 &

# 保存PID
echo $! > flask.pid

echo "Flask服务已启动，PID: $(cat flask.pid)"
echo "您可以通过 http://localhost:5006 访问Flask服务"
echo "日志文件: flask.log"
