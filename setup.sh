#!/bin/bash
# 设置脚本 - 安装AI考试生成器系统的所有依赖

echo "设置AI考试生成器系统..."

# 检查Python版本
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
if [ -z "$python_version" ]; then
    echo "错误: 未找到Python 3，请先安装Python 3.8+"
    exit 1
fi

echo "检测到Python版本: $python_version"

# 检查Python版本是否满足要求
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "错误: Python版本过低，需要Python 3.8+，当前版本: $python_version"
    exit 1
fi

# 创建虚拟环境
echo "创建Python虚拟环境..."
if [ -d "venv" ]; then
    echo "虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "错误: 创建虚拟环境失败"
        exit 1
    fi
    echo "虚拟环境创建成功"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装Python依赖
echo "安装Python依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 安装Python依赖失败"
        exit 1
    fi
    echo "Python依赖安装成功"
else
    echo "警告: 未找到requirements.txt文件"
fi

# 检查Node.js和npm
echo "检查Node.js和npm..."
if ! command -v node &> /dev/null; then
    echo "警告: 未找到Node.js，前端功能将不可用"
    echo "请安装Node.js 16+: https://nodejs.org/"
else
    node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$node_version" -lt 16 ]; then
        echo "警告: Node.js版本过低，需要16+，当前版本: $(node --version)"
    else
        echo "检测到Node.js版本: $(node --version)"
        
        # 安装前端依赖
        if [ -d "frontend" ]; then
            echo "安装前端依赖..."
            cd frontend
            npm install
            if [ $? -ne 0 ]; then
                echo "错误: 安装前端依赖失败"
                cd ..
                exit 1
            fi
            cd ..
            echo "前端依赖安装成功"
        else
            echo "警告: 未找到frontend目录"
        fi
    fi
fi

# 创建必要的目录
echo "创建必要的目录..."
mkdir -p cache
mkdir -p quicksight_data
mkdir -p flask-service/data
mkdir -p flask-service/markdown-quiz-files

# 设置脚本权限
echo "设置脚本权限..."
chmod +x start.sh
chmod +x stop.sh
if [ -f "test_api.sh" ]; then
    chmod +x test_api.sh
fi

echo ""
echo "✅ 设置完成！"
echo ""
echo "下一步："
echo "1. 配置AWS凭证以访问Bedrock服务"
echo "2. 运行 './start.sh' 启动系统"
echo "3. 在浏览器中访问前端界面（通常是 http://localhost:5173）"
echo ""
echo "注意: 请确保已正确配置AWS凭证，否则系统无法正常工作"