#!/bin/bash
# stop_flask.sh - 停止Flask服务

if [ -f flask.pid ]; then
    PID=$(cat flask.pid)
    if ps -p $PID > /dev/null; then
        echo "停止Flask服务 (PID: $PID)..."
        kill $PID
        rm flask.pid
        echo "服务已停止。"
    else
        echo "服务未运行。"
        rm flask.pid
    fi
else
    echo "PID文件不存在。"
fi
