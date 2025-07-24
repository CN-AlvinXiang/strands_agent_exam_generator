#!/bin/bash
# 统一停止脚本 - 停止AI考试生成器系统的各个组件

# 默认停止所有组件
STOP_BACKEND=true
STOP_FLASK=true
STOP_FRONTEND=true

# 处理命令行参数
if [ $# -gt 0 ]; then
    # 如果有参数，则默认不停止任何组件，只停止指定的组件
    STOP_BACKEND=false
    STOP_FLASK=false
    STOP_FRONTEND=false
    
    for arg in "$@"; do
        case $arg in
            all)
                STOP_BACKEND=true
                STOP_FLASK=true
                STOP_FRONTEND=true
                ;;
            backend)
                STOP_BACKEND=true
                ;;
            flask)
                STOP_FLASK=true
                ;;
            frontend)
                STOP_FRONTEND=true
                ;;
            *)
                echo "未知参数: $arg"
                echo "用法: ./stop.sh [all|backend|flask|frontend]"
                echo "示例: ./stop.sh all          # 停止所有组件"
                echo "      ./stop.sh backend flask # 只停止后端和Flask服务"
                echo "      ./stop.sh              # 默认停止所有组件"
                exit 1
                ;;
        esac
    done
fi

echo "停止AI考试生成器系统..."

# 停止后端服务
if [ "$STOP_BACKEND" = true ]; then
    echo "停止后端服务..."
    
    # 检查PID文件
    if [ -f "agent.pid" ]; then
        PID=$(cat agent.pid)
        if ps -p $PID > /dev/null; then
            kill $PID
            echo "已停止后端服务，PID: $PID"
        else
            echo "后端服务未运行（PID: $PID）"
        fi
        rm agent.pid
    else
        echo "未找到后端服务PID文件"
        
        # 尝试查找并杀死可能的进程
        PIDS=$(ps aux | grep "[p]ython -m exam_generator.server" | awk '{print $2}')
        if [ -n "$PIDS" ]; then
            echo "找到可能的后端服务进程，尝试停止..."
            for PID in $PIDS; do
                kill $PID
                echo "已停止进程，PID: $PID"
            done
        fi
    fi
    
    # 清理旧的日志文件
    if [ -f "agent_py310.log" ]; then
        echo "清理旧的日志文件: agent_py310.log"
        rm agent_py310.log
    fi
fi

# 停止Flask渲染服务
if [ "$STOP_FLASK" = true ]; then
    echo "停止Flask渲染服务..."
    
    # 检查PID文件
    if [ -f "flask-service/flask.pid" ]; then
        PID=$(cat flask-service/flask.pid)
        if ps -p $PID > /dev/null; then
            kill $PID
            echo "已停止Flask渲染服务，PID: $PID"
        else
            echo "Flask渲染服务未运行（PID: $PID）"
        fi
        rm flask-service/flask.pid
    else
        echo "未找到Flask渲染服务PID文件"
        
        # 尝试查找并杀死可能的进程
        PIDS=$(ps aux | grep "[p]ython.*flask-service/main.py" | awk '{print $2}')
        if [ -n "$PIDS" ]; then
            echo "找到可能的Flask服务进程，尝试停止..."
            for PID in $PIDS; do
                kill $PID
                echo "已停止进程，PID: $PID"
            done
        fi
    fi
fi

# 停止前端服务
if [ "$STOP_FRONTEND" = true ]; then
    echo "停止前端服务..."
    
    # 检查PID文件
    if [ -f "frontend/frontend.pid" ]; then
        PID=$(cat frontend/frontend.pid)
        if ps -p $PID > /dev/null; then
            kill $PID
            echo "已停止前端服务，PID: $PID"
        else
            echo "前端服务未运行（PID: $PID）"
        fi
        rm frontend/frontend.pid
    else
        # 尝试查找并杀死可能的Node.js进程
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            PIDS=$(ps aux | grep "[n]ode.*vite" | awk '{print $2}')
        else
            # Linux和其他系统
            PIDS=$(ps aux | grep "[n]ode.*vite" | awk '{print $2}')
        fi
        
        if [ -n "$PIDS" ]; then
            echo "找到前端服务进程，尝试停止..."
            for PID in $PIDS; do
                kill $PID
                echo "已停止进程，PID: $PID"
            done
        else
            echo "未找到前端服务进程"
            echo "如果前端服务在单独的终端中运行，请在该终端中按Ctrl+C停止"
        fi
    fi
    
    # 清理日志文件
    if [ -f "frontend/frontend.log" ]; then
        echo "清理前端日志文件"
        rm frontend/frontend.log
    fi
fi

echo "系统已停止"
