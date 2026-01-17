# ScoutsLens 项目部署文档

## 项目概述

ScoutsLens 是一个基于 Streamlit 构建的篮球球员阵容管理和评分系统，用于帮助用户管理球员阵容、分析比赛数据并计算球员评分。

### 主要功能
- 球员筛选和排序
- 阵容管理（首发和替补）
- 薪资上限检查
- 阵容导出
- 比赛数据查询和分析
- 球员评分计算

## 部署前准备

### 服务器要求
- 操作系统：Ubuntu 20.04+ 或 CentOS 7+
- Python 3.7+
- Git
- 网络连接（用于克隆 GitHub 仓库和安装依赖）
- 端口 8501 开放（用于 Streamlit 服务）

### GitHub 仓库准备
1. 将项目代码推送到 GitHub 仓库
2. 确保仓库可公开访问或配置了适当的访问权限

### 服务器环境准备
1. 更新系统包
   ```bash
   # Ubuntu/Debian
   sudo apt-get update && sudo apt-get upgrade -y
   
   # CentOS/RHEL
   sudo yum update -y
   ```

2. 安装基础依赖
   ```bash
   # Ubuntu/Debian
   sudo apt-get install -y python3 python3-venv python3-pip git curl net-tools
   
   # CentOS/RHEL
   sudo yum install -y python3 python3-venv python3-pip git curl net-tools
   ```

## 部署步骤

### 方法一：使用部署脚本（推荐）

1. **下载部署脚本**
   ```bash
   wget -O deploy.sh https://raw.githubusercontent.com/yourusername/ScoutsLens/main/deploy.sh
   chmod +x deploy.sh
   ```

2. **配置部署脚本**
   编辑 `deploy.sh` 文件，修改以下配置：
   ```bash
   GITHUB_REPO="https://github.com/yourusername/ScoutsLens.git"  # 替换为实际的 GitHub 仓库地址
   ```

3. **执行部署脚本**
   ```bash
   sudo ./deploy.sh
   ```

   部署脚本会自动完成以下操作：
   - 安装系统依赖
   - 克隆 GitHub 仓库
   - 创建虚拟环境
   - 安装项目依赖
   - 创建启动、停止和状态检查脚本
   - 启动 Streamlit 服务
   - 检查服务状态
   - 执行健康检查

### 方法二：手动部署

1. **克隆 GitHub 仓库**
   ```bash
   sudo mkdir -p /opt/ScoutsLens
   sudo git clone https://github.com/yourusername/ScoutsLens.git /opt/ScoutsLens
   ```

2. **创建虚拟环境**
   ```bash
   cd /opt/ScoutsLens
   sudo python3 -m venv venv
   ```

3. **激活虚拟环境并安装依赖**
   ```bash
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **创建启动脚本**
   ```bash
   sudo cat > start.sh << 'EOF'
   #!/bin/bash
   
   # 启动脚本
   PROJECT_DIR="/opt/ScoutsLens"
   VENV_DIR="$PROJECT_DIR/venv"
   LOG_DIR="$PROJECT_DIR/logs"
   PORT="8501"
   
   # 创建日志目录
   mkdir -p "$LOG_DIR"
   
   # 激活虚拟环境
   source "$VENV_DIR/bin/activate"
   
   # 启动 Streamlit 服务
   streamlit run "$PROJECT_DIR/app.py" \
       --server.port=$PORT \
       --server.address=0.0.0.0 \
       > "$LOG_DIR/streamlit.log" 2>&1 &
   
   # 保存进程 ID
   echo $! > "$PROJECT_DIR/streamlit.pid"
   echo "服务已启动，进程 ID: $!"
   EOF
   
   sudo chmod +x start.sh
   ```

5. **创建停止脚本**
   ```bash
   sudo cat > stop.sh << 'EOF'
   #!/bin/bash
   
   # 停止脚本
   PROJECT_DIR="/opt/ScoutsLens"
   
   if [ -f "$PROJECT_DIR/streamlit.pid" ]; then
       PID=$(cat "$PROJECT_DIR/streamlit.pid")
       if ps -p $PID > /dev/null 2>&1; then
           echo "停止 Streamlit 服务... (PID: $PID)"
           kill $PID
           rm "$PROJECT_DIR/streamlit.pid"
           echo "服务已停止"
       else
           echo "服务未运行，清理 pid 文件"
           rm "$PROJECT_DIR/streamlit.pid"
       fi
   else
       echo "pid 文件不存在，服务可能未运行"
   fi
   EOF
   
   sudo chmod +x stop.sh
   ```

6. **启动服务**
   ```bash
   sudo ./start.sh
   ```

## 服务管理

### 启动服务
```bash
sudo bash /opt/ScoutsLens/start.sh
```

### 停止服务
```bash
sudo bash /opt/ScoutsLens/stop.sh
```

### 检查服务状态
```bash
sudo bash /opt/ScoutsLens/status.sh
```

### 查看日志
```bash
# 查看 Streamlit 服务日志
tail -f /opt/ScoutsLens/logs/streamlit.log

# 查看部署日志
tail -f /opt/ScoutsLens/logs/deploy.log

# 查看启动日志
tail -f /opt/ScoutsLens/logs/start.log

# 查看停止日志
tail -f /opt/ScoutsLens/logs/stop.log

# 查看状态检查日志
tail -f /opt/ScoutsLens/logs/status.log
```

## 访问服务

部署完成后，您可以通过以下地址访问 ScoutsLens 服务：

```
http://服务器IP:8501
```

### 示例
- 本地访问：`http://localhost:8501`
- 网络访问：`http://192.168.1.100:8501`（替换为实际的服务器 IP）

## 故障排查

### 1. 服务无法启动

**症状**：执行启动脚本后，服务未运行

**排查步骤**：
1. 检查日志文件：`tail -n 50 /opt/ScoutsLens/logs/streamlit.log`
2. 检查端口是否被占用：`netstat -tuln | grep 8501`
3. 检查虚拟环境是否正常：`source /opt/ScoutsLens/venv/bin/activate && python --version`
4. 检查依赖是否安装完整：`pip list | grep -E "streamlit|pandas|numpy"`

### 2. 服务启动后无响应

**症状**：服务进程存在，但访问页面无响应

**排查步骤**：
1. 检查服务日志：`tail -n 50 /opt/ScoutsLens/logs/streamlit.log`
2. 检查网络连接：`curl -v http://localhost:8501`
3. 检查防火墙设置：`sudo ufw status`（Ubuntu）或 `sudo firewall-cmd --list-ports`（CentOS）
4. 重启服务：`sudo bash /opt/ScoutsLens/stop.sh && sudo bash /opt/ScoutsLens/start.sh`

### 3. 数据文件不存在

**症状**：服务启动成功，但无法加载球员数据

**排查步骤**：
1. 检查数据文件是否存在：`ls -la /opt/ScoutsLens/player_information.csv`
2. 如果文件不存在，需要添加球员数据文件

### 4. 依赖安装失败

**症状**：部署脚本执行过程中依赖安装失败

**排查步骤**：
1. 检查网络连接是否正常
2. 检查 Python 版本是否满足要求（3.7+）
3. 尝试手动安装依赖：`source /opt/ScoutsLens/venv/bin/activate && pip install -r requirements.txt`

## 常见问题

### Q1: 如何更新项目代码？

**A1**: 可以通过以下步骤更新项目代码：
```bash
cd /opt/ScoutsLens
git pull
source venv/bin/activate
pip install -r requirements.txt
bash stop.sh
bash start.sh
```

### Q2: 如何修改服务端口？

**A2**: 修改 `deploy.sh` 文件中的 `PORT` 变量，然后重新执行部署脚本，或修改 `start.sh` 文件中的端口配置并重启服务。

### Q3: 如何设置服务开机自启动？

**A3**: 创建系统服务文件：

```bash
sudo cat > /etc/systemd/system/scoutslens.service << 'EOF'
[Unit]
Description=ScoutsLens Streamlit Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ScoutsLens
ExecStart=/bin/bash /opt/ScoutsLens/start.sh
ExecStop=/bin/bash /opt/ScoutsLens/stop.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable scoutslens.service
sudo systemctl start scoutslens.service
```

### Q4: 如何查看服务运行状态？

**A4**: 使用系统服务命令：
```bash
sudo systemctl status scoutslens.service
```
或使用状态检查脚本：
```bash
bash /opt/ScoutsLens/status.sh
```

### Q5: 遇到内存不足问题怎么办？

**A5**: 增加服务器内存或优化 Streamlit 配置，在 `start.sh` 文件中添加以下参数：
```bash
streamlit run "$PROJECT_DIR/app.py" \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.maxUploadSize=10 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    > "$LOG_DIR/streamlit.log" 2>&1 &
```

## 部署架构

```
┌─────────────────────────────────────────────────────────┐
│                     服务器                               │
├─────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────┐  │
│  │                /opt/ScoutsLens                   │  │
│  ├───────────────────────────────────────────────────┤  │
│  │  ┌─────────────────┐  ┌─────────────────┐        │  │
│  │  │   项目代码      │  │   venv 虚拟环境 │        │  │
│  │  └─────────────────┘  └─────────────────┘        │  │
│  │  ┌─────────────────┐  ┌─────────────────┐        │  │
│  │  │   启动脚本      │  │   停止脚本      │        │  │
│  │  └─────────────────┘  └─────────────────┘        │  │
│  │  ┌─────────────────┐  ┌─────────────────┐        │  │
│  │  │  状态检查脚本   │  │   日志目录      │        │  │
│  │  └─────────────────┘  └─────────────────┘        │  │
│  └───────────────────────────────────────────────────┘  │
│                  ▲                                     │
│                  │                                     │
│                  ▼                                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Streamlit 服务                      │  │
│  └───────────────────────────────────────────────────┘  │
│                  ▲                                     │
│                  │                                     │
│                  ▼                                     │
│  ┌───────────────────────────────────────────────────┐  │
│  │                  8501 端口                        │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 技术栈

- **前端框架**: Streamlit
- **后端**: Python 3.7+
- **数据处理**: Pandas, NumPy
- **API**: nba_api, basketball_reference_scraper
- **虚拟环境**: venv
- **版本控制**: Git

## 总结

本部署文档提供了详细的步骤，帮助您在服务器上通过 GitHub 部署 ScoutsLens 项目，使用 venv 作为虚拟环境。如果您遇到任何问题，请参考故障排查部分或联系技术支持。

---

**部署完成后，您可以通过 http://服务器IP:8501 访问 ScoutsLens 系统，开始管理和分析篮球球员阵容。**
