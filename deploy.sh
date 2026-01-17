#!/bin/bash

# 服务器部署脚本 - ScoutsLens 项目
# 使用 venv 作为虚拟环境

set -e

# 配置变量
GITHUB_REPO="https://github.com/yourusername/ScoutsLens.git"  # 替换为实际的 GitHub 仓库地址
PROJECT_DIR="/opt/ScoutsLens"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
PORT="8501"
HEALTH_CHECK_URL="http://localhost:$PORT"

# 日志函数
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="$1"
    echo "[$timestamp] $message"
    echo "[$timestamp] $message" >> "$LOG_DIR/deploy.log"
}

# 错误处理函数
error_exit() {
    log "错误: $1"
    exit 1
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" > /dev/null 2>&1; then
        error_exit "命令 $1 不存在，请安装"
    fi
}

# 检查服务状态
check_service() {
    local max_attempts=30
    local attempt=0
    local delay=2
    
    log "检查服务状态..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$HEALTH_CHECK_URL" > /dev/null 2>&1; then
            log "服务已成功启动！"
            return 0
        fi
        
        attempt=$((attempt + 1))
        log "等待服务启动... ($attempt/$max_attempts)"
        sleep $delay
    done
    
    error_exit "服务启动失败，请检查日志"
}

# 健康检查
health_check() {
    log "执行健康检查..."
    
    # 检查进程是否存在
    if [ -f "$PROJECT_DIR/streamlit.pid" ]; then
        local pid=$(cat "$PROJECT_DIR/streamlit.pid")
        if ps -p $pid > /dev/null 2>&1; then
            log "进程状态: 运行中 (PID: $pid)"
        else
            log "警告: 进程不存在，但 pid 文件存在"
        fi
    else
        log "警告: pid 文件不存在"
    fi
    
    # 检查端口是否监听
    if netstat -tuln | grep -q ":$PORT "; then
        log "端口状态: $PORT 已监听"
    else
        log "警告: 端口 $PORT 未监听"
    fi
    
    # 检查日志文件
    if [ -f "$LOG_DIR/streamlit.log" ]; then
        local error_count=$(grep -i "error" "$LOG_DIR/streamlit.log" | wc -l)
        if [ $error_count -gt 0 ]; then
            log "警告: 日志中存在 $error_count 个错误"
            log "查看错误详情: tail -n 20 $LOG_DIR/streamlit.log"
        else
            log "日志状态: 无错误"
        fi
    else
        log "警告: 日志文件不存在"
    fi
}

# 主部署函数
deploy() {
    # 创建日志目录
    mkdir -p "$LOG_DIR"
    
    log "开始部署 ScoutsLens 项目..."
    
    # 1. 检查系统环境
    log "步骤 1: 检查系统环境"
    check_command "python3"
    check_command "git"
    
    # 2. 安装系统依赖
    log "步骤 2: 安装系统依赖"
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        log "检测到 Debian/Ubuntu 系统"
        apt-get update && apt-get install -y python3 python3-venv python3-pip git curl net-tools
    elif [ -f /etc/redhat-release ]; then
        # CentOS/RHEL
        log "检测到 CentOS/RHEL 系统"
        yum update -y && yum install -y python3 python3-venv python3-pip git curl net-tools
    else
        error_exit "不支持的操作系统"
    fi
    
    # 3. 创建项目目录
    log "步骤 3: 创建项目目录"
    mkdir -p "$PROJECT_DIR"
    
    # 4. 克隆 GitHub 仓库
    log "步骤 4: 克隆 GitHub 仓库"
    if [ -d "$PROJECT_DIR/.git" ]; then
        log "仓库已存在，执行 git pull 更新..."
        cd "$PROJECT_DIR"
        git pull
    else
        log "克隆新仓库..."
        git clone "$GITHUB_REPO" "$PROJECT_DIR"
    fi
    
    # 5. 创建虚拟环境
    log "步骤 5: 创建虚拟环境"
    if [ -d "$VENV_DIR" ]; then
        log "虚拟环境已存在，重新创建..."
        rm -rf "$VENV_DIR"
    fi
    python3 -m venv "$VENV_DIR"
    
    # 6. 激活虚拟环境并安装依赖
    log "步骤 6: 激活虚拟环境并安装依赖"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    log "安装项目依赖..."
    pip install -r "$PROJECT_DIR/requirements.txt"
    
    # 7. 检查是否存在数据文件
    log "步骤 7: 检查数据文件"
    if [ ! -f "$PROJECT_DIR/player_information.csv" ]; then
        log "警告: 数据文件 player_information.csv 不存在，请确保在运行前添加"
    else
        log "数据文件存在: player_information.csv"
    fi
    
    # 8. 创建启动脚本
    log "步骤 8: 创建启动脚本"
    cat > "$PROJECT_DIR/start.sh" << 'EOF'
#!/bin/bash

# 启动脚本
PROJECT_DIR="/opt/ScoutsLens"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
PORT="8501"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="$1"
    echo "[$timestamp] $message"
    echo "[$timestamp] $message" >> "$LOG_DIR/start.log"
}

# 停止已运行的服务
if [ -f "$PROJECT_DIR/streamlit.pid" ]; then
    local pid=$(cat "$PROJECT_DIR/streamlit.pid")
    if ps -p $pid > /dev/null 2>&1; then
        log "停止已运行的服务..."
        kill $pid
        sleep 2
    fi
    rm -f "$PROJECT_DIR/streamlit.pid"
fi

# 激活虚拟环境
log "激活虚拟环境..."
source "$VENV_DIR/bin/activate"

# 启动 Streamlit 服务
log "启动 Streamlit 服务..."
log "服务地址: http://0.0.0.0:$PORT"

# 启动服务
streamlit run "$PROJECT_DIR/app.py" \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    > "$LOG_DIR/streamlit.log" 2>&1 &

# 保存进程 ID
local pid=$!
echo $pid > "$PROJECT_DIR/streamlit.pid"
log "服务已启动，进程 ID: $pid"
log "日志文件: $LOG_DIR/streamlit.log"

# 等待服务启动
sleep 5

# 检查服务状态
if ps -p $pid > /dev/null 2>&1; then
    log "服务启动成功！"
else
    log "服务启动失败，请检查日志"
fi
EOF
    
    # 创建停止脚本
    cat > "$PROJECT_DIR/stop.sh" << 'EOF'
#!/bin/bash

# 停止脚本
PROJECT_DIR="/opt/ScoutsLens"
LOG_DIR="$PROJECT_DIR/logs"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="$1"
    echo "[$timestamp] $message"
    echo "[$timestamp] $message" >> "$LOG_DIR/stop.log"
}

if [ -f "$PROJECT_DIR/streamlit.pid" ]; then
    local pid=$(cat "$PROJECT_DIR/streamlit.pid")
    if ps -p $pid > /dev/null 2>&1; then
        log "停止 Streamlit 服务... (PID: $pid)"
        kill $pid
        sleep 2
        
        # 检查是否停止成功
        if ps -p $pid > /dev/null 2>&1; then
            log "警告: 服务未能正常停止，尝试强制停止..."
            kill -9 $pid
            sleep 1
        fi
        
        rm "$PROJECT_DIR/streamlit.pid"
        log "服务已停止"
    else
        log "服务未运行，清理 pid 文件"
        rm "$PROJECT_DIR/streamlit.pid"
    fi
else
    log "pid 文件不存在，服务可能未运行"
    
    # 尝试查找并停止进程
    local streamlit_pid=$(ps aux | grep "streamlit run" | grep -v grep | awk '{print $2}')
    if [ -n "$streamlit_pid" ]; then
        log "发现运行中的 Streamlit 进程: $streamlit_pid"
        log "尝试停止..."
        kill $streamlit_pid
        sleep 2
        log "服务已停止"
    fi
fi
EOF
    
    # 创建状态检查脚本
    cat > "$PROJECT_DIR/status.sh" << 'EOF'
#!/bin/bash

# 状态检查脚本
PROJECT_DIR="/opt/ScoutsLens"
LOG_DIR="$PROJECT_DIR/logs"
PORT="8501"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志函数
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="$1"
    echo "[$timestamp] $message"
    echo "[$timestamp] $message" >> "$LOG_DIR/status.log"
}

log "检查 ScoutsLens 服务状态..."

# 检查进程状态
if [ -f "$PROJECT_DIR/streamlit.pid" ]; then
    local pid=$(cat "$PROJECT_DIR/streamlit.pid")
    if ps -p $pid > /dev/null 2>&1; then
        log "进程状态: 运行中 (PID: $pid)"
    else
        log "进程状态: 已停止 (PID 文件存在)"
    fi
else
    log "进程状态: 未运行 (PID 文件不存在)"
fi

# 检查端口状态
if netstat -tuln | grep -q ":$PORT "; then
    log "端口状态: $PORT 已监听"
else
    log "端口状态: $PORT 未监听"
fi

# 检查服务响应
if curl -s "http://localhost:$PORT" > /dev/null 2>&1; then
    log "服务状态: 正常响应"
else
    log "服务状态: 无响应"
fi

# 检查日志文件
if [ -f "$LOG_DIR/streamlit.log" ]; then
    local error_count=$(grep -i "error" "$LOG_DIR/streamlit.log" | wc -l)
    if [ $error_count -gt 0 ]; then
        log "日志状态: 存在 $error_count 个错误"
        log "最近的错误:"
        grep -i "error" "$LOG_DIR/streamlit.log" | tail -n 5
    else
        log "日志状态: 无错误"
    fi
else
    log "日志状态: 日志文件不存在"
fi

log "状态检查完成"
EOF
    
    # 设置脚本权限
    chmod +x "$PROJECT_DIR/start.sh"
    chmod +x "$PROJECT_DIR/stop.sh"
    chmod +x "$PROJECT_DIR/status.sh"
    
    # 9. 启动服务
    log "步骤 9: 启动服务"
    cd "$PROJECT_DIR"
    bash "$PROJECT_DIR/start.sh"
    
    # 10. 检查服务状态
    log "步骤 10: 检查服务状态"
    check_service
    
    # 11. 执行健康检查
    log "步骤 11: 执行健康检查"
    health_check
    
    # 12. 显示部署结果
    log "部署完成！"
    log "项目位置: $PROJECT_DIR"
    log "虚拟环境: $VENV_DIR"
    log "日志目录: $LOG_DIR"
    log "服务地址: http://$(hostname -I | awk '{print $1}'):$PORT"
    log ""
    log "管理命令:"
    log "  启动服务: bash $PROJECT_DIR/start.sh"
    log "  停止服务: bash $PROJECT_DIR/stop.sh"
    log "  检查状态: bash $PROJECT_DIR/status.sh"
    log "  查看日志: tail -f $LOG_DIR/streamlit.log"
    log ""
    log "部署脚本执行成功！"
}

# 执行部署
deploy