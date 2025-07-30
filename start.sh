#!/bin/bash
# 统一启动脚本 - 启动AI考试生成器系统的各个组件

# 默认启动所有组件
START_BACKEND=true
START_FLASK=true
START_FRONTEND=true

# 处理命令行参数
if [ $# -gt 0 ]; then
    # 如果有参数，则默认不启动任何组件，只启动指定的组件
    START_BACKEND=false
    START_FLASK=false
    START_FRONTEND=false
    
    for arg in "$@"; do
        case $arg in
            all)
                START_BACKEND=true
                START_FLASK=true
                START_FRONTEND=true
                ;;
            backend)
                START_BACKEND=true
                ;;
            flask)
                START_FLASK=true
                ;;
            frontend)
                START_FRONTEND=true
                ;;
            *)
                echo "未知参数: $arg"
                echo "用法: ./start.sh [all|backend|flask|frontend]"
                echo "示例: ./start.sh all          # 启动所有组件"
                echo "      ./start.sh backend flask # 只启动后端和Flask服务"
                echo "      ./start.sh              # 默认启动所有组件"
                exit 1
                ;;
        esac
    done
fi

echo "启动AI考试生成器系统..."

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "错误: 未找到虚拟环境，请先运行 './setup.sh'"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查Python版本
PYTHON_VERSION=$(python --version)
echo "使用Python版本: $PYTHON_VERSION"

# 启动Flask渲染服务
if [ "$START_FLASK" = true ]; then
    if [ -d "flask-service" ] && [ -f "flask-service/main.py" ]; then
        echo "启动Flask渲染服务..."
        
        # 确保data目录存在
        mkdir -p flask-service/data
        
        # 进入Flask目录
        cd flask-service
        
        # 安装依赖（确保依赖已安装）
        pip install -r requirements.txt > /dev/null 2>&1
        
        # 启动Flask服务
        nohup python main.py > flask.log 2>&1 &
        
        # 保存PID
        echo $! > flask.pid
        
        cd ..
        
        echo "Flask渲染服务已启动，PID: $(cat flask-service/flask.pid)"
        echo "您可以通过 http://*:5006 访问Flask服务"
        echo "日志文件: flask-service/flask.log"
        
        # 等待Flask服务启动
        echo "等待Flask服务启动..."
        sleep 3
    else
        echo "警告: 未找到Flask渲染服务或主程序"
    fi
fi

# 启动后端服务
if [ "$START_BACKEND" = true ]; then
    echo "启动后端服务..."
    nohup python -m exam_generator.server > agent.log 2>&1 &
    
    # 保存PID
    echo $! > agent.pid
    
    echo "后端服务已启动，PID: $(cat agent.pid)"
    echo "您可以通过 http://*:5001 访问后端服务"
    echo "日志文件: agent.log"
    
    # 等待后端服务启动
    echo "等待后端服务启动..."
    sleep 3
    
    # 检查后端服务是否正常运行
    if command -v curl &> /dev/null; then
        if ! curl -s http://*:5001/health > /dev/null; then
            echo "警告: 后端服务可能未正常启动，请检查日志文件"
        else
            echo "后端服务健康检查通过"
        fi
    fi
fi

# 启动前端服务
if [ "$START_FRONTEND" = true ]; then
    echo "启动前端服务..."
    
    # 检查前端目录
    if [ ! -d "frontend" ]; then
        echo "错误: 未找到前端目录"
        exit 1
    fi
    
    # 检查Node.js和npm
    if ! command -v node &> /dev/null; then
        echo "错误: 未找到Node.js，请安装Node.js"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo "错误: 未找到npm，请安装npm"
        exit 1
    fi
    
    # 在新的终端窗口中启动前端服务
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - 直接在后台运行前端服务
        cd frontend
        nohup npm run dev -- --host 0.0.0.0 > frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > frontend.pid
        cd ..
        echo "前端服务已启动，PID: $(cat frontend/frontend.pid)"
        echo "日志文件: frontend/frontend.log"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal -- bash -c "cd '$(pwd)/frontend' && npm run dev; exec bash"
        elif command -v xterm &> /dev/null; then
            xterm -e "cd '$(pwd)/frontend' && npm run dev" &
        else
            echo "无法打开新终端窗口，请在另一个终端中运行:"
            echo "cd '$(pwd)/frontend' && npm run dev"
        fi
    else
        # 其他系统
        echo "无法自动启动前端，请在另一个终端中运行:"
        echo "cd '$(pwd)/frontend' && npm run dev"
    fi
    
    echo "前端服务启动中..."
    echo "前端界面通常可通过 http://*:5173 访问"
fi

echo "系统启动完成！"
if [ "$START_BACKEND" = true ]; then
    echo "- 后端API: http://*:5001"
fi
if [ "$START_FLASK" = true ]; then
    echo "- Flask服务: http://*:5006"
fi
if [ "$START_FRONTEND" = true ]; then
    echo "- 前端界面: http://*:5173"
fi
echo "使用 './stop.sh' 停止系统"
