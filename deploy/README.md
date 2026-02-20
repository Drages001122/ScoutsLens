# ScoutsLens 自动化部署系统

## 目录结构

```
deploy/
├── config/
│   └── remote_config.json          # 服务器配置文件
├── backups/                        # 数据库备份目录（自动创建）
├── auto_deploy.py                   # 自动部署脚本
├── build.py                        # 项目构建脚本
├── start.py                        # 启动服务脚本
├── stop.py                         # 停止服务脚本
├── restart.py                      # 重启服务脚本
├── status.py                       # 服务状态检查脚本
├── backup.py                       # 数据库备份脚本
├── update.py                       # 更新部署脚本
├── rollback.py                     # 回滚脚本
├── requirements.txt                # Python依赖
└── README.md                       # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置服务器信息

编辑 `config/remote_config.json` 文件：

```json
{
  "hostname": "your-server-ip",
  "username": "your-username",
  "password": "your-password",
  "port": 22,
  "remote_project_dir": "/var/www/scoutslens",
  "remote_domain": "your-domain-or-ip",
  "secret_key": "your-secret-key"
}
```

### 3. 首次部署

```bash
# 构建项目
python build.py

# 自动部署
python auto_deploy.py
```

## 脚本说明

### auto_deploy.py - 自动部署脚本

**功能**: 完整的自动化部署流程

**执行步骤**:
1. 安装系统依赖（Python3, pip3, Nginx）
2. 创建项目目录
3. 上传后端代码
4. 上传前端文件
5. 上传数据库
6. 配置 Python 环境
7. 更新后端配置
8. 配置 Nginx
9. 配置 systemd 服务
10. 验证部署

**使用方法**:
```bash
python auto_deploy.py
```

**适用场景**: 首次部署或完全重新部署

---

### build.py - 项目构建脚本

**功能**: 构建前端和检查后端依赖

**执行步骤**:
1. 安装前端依赖（npm install）
2. 构建前端（npm run build）
3. 检查后端依赖文件

**使用方法**:
```bash
python build.py
```

**适用场景**: 修改前端代码后需要重新构建

---

### start.py - 启动服务脚本

**功能**: 启动 ScoutsLens 服务

**执行步骤**:
1. 启动应用服务（scoutslens）
2. 启动 Nginx
3. 检查服务状态

**使用方法**:
```bash
python start.py
```

**适用场景**: 服务停止后需要启动

---

### stop.py - 停止服务脚本

**功能**: 停止 ScoutsLens 服务

**执行步骤**:
1. 停止应用服务（scoutslens）
2. 停止 Nginx
3. 检查服务状态

**使用方法**:
```bash
python stop.py
```

**适用场景**: 维护或更新前需要停止服务

---

### restart.py - 重启服务脚本

**功能**: 重启 ScoutsLens 服务

**执行步骤**:
1. 重启应用服务（scoutslens）
2. 重启 Nginx
3. 检查服务状态

**使用方法**:
```bash
python restart.py
```

**适用场景**: 配置更改或代码更新后需要重启

---

### status.py - 服务状态检查脚本

**功能**: 检查服务运行状态和系统资源

**检查项目**:
- 应用服务状态
- Nginx 状态
- 磁盘使用情况
- 内存使用情况
- CPU 使用情况
- 应用服务日志
- Nginx 访问日志
- Nginx 错误日志

**使用方法**:
```bash
python status.py
```

**适用场景**: 日常运维、故障排查

---

### backup.py - 数据库备份脚本

**功能**: 备份远程数据库到本地

**执行步骤**:
1. 从服务器下载数据库文件
2. 保存到 `backups/` 目录
3. 文件名包含时间戳

**使用方法**:
```bash
python backup.py
```

**适用场景**: 定期备份、重大更新前备份

**备份文件命名**: `scoutslens_YYYYMMDD_HHMMSS.db`

---

### update.py - 更新部署脚本

**功能**: 更新前端或后端代码

**执行步骤**:
1. 选择更新内容（前端/后端/全部）
2. 上传更新的文件
3. 重启相关服务

**使用方法**:
```bash
python update.py
```

**交互选项**:
```
请选择要更新的内容:
1. 仅更新前端
2. 仅更新后端
3. 同时更新前端和后端

请输入选项 (1/2/3):
```

**适用场景**: 代码更新、bug修复

**注意**: 更新前端前需要先运行 `python build.py`

---

### rollback.py - 回滚脚本

**功能**: 从备份恢复数据库

**执行步骤**:
1. 列出可用的备份文件
2. 选择要恢复的备份
3. 备份当前数据库
4. 上传并恢复备份数据库
5. 重启服务

**使用方法**:
```bash
python rollback.py
```

**适用场景**: 数据库损坏、更新失败需要回滚

**注意**: 回滚前会自动备份当前数据库

---

## 常见使用场景

### 场景 1: 首次部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置服务器信息
# 编辑 config/remote_config.json

# 3. 构建项目
python build.py

# 4. 自动部署
python auto_deploy.py
```

### 场景 2: 更新前端代码

```bash
# 1. 构建前端
python build.py

# 2. 更新前端
python update.py
# 选择: 1. 仅更新前端
```

### 场景 3: 更新后端代码

```bash
# 1. 更新后端
python update.py
# 选择: 2. 仅更新后端
```

### 场景 4: 更新前后端

```bash
# 1. 构建前端
python build.py

# 2. 更新全部
python update.py
# 选择: 3. 同时更新前端和后端
```

### 场景 5: 日常运维检查

```bash
# 检查服务状态
python status.py
```

### 场景 6: 定期备份

```bash
# 备份数据库
python backup.py
```

### 场景 7: 故障恢复

```bash
# 1. 停止服务
python stop.py

# 2. 回滚数据库
python rollback.py

# 3. 启动服务
python start.py

# 4. 检查状态
python status.py
```

## 配置参数说明

### remote_config.json 参数

| 参数 | 说明 | 示例 |
|------|------|------|
| hostname | 服务器IP地址或域名 | 8.153.167.209 |
| username | SSH登录用户名 | root |
| password | SSH登录密码 | your-password |
| port | SSH端口 | 22 |
| remote_project_dir | 服务器上项目目录 | /var/www/scoutslens |
| remote_domain | 服务器域名或IP | 8.153.167.209 |
| secret_key | Flask应用密钥 | your-secret-key |

## 故障排查

### 问题 1: 连接服务器失败

**检查项**:
- 服务器IP地址是否正确
- SSH密码是否正确
- 网络连接是否正常
- 服务器SSH服务是否运行

**解决方法**:
```bash
# 手动测试SSH连接
ssh username@hostname
```

### 问题 2: 部署失败

**检查项**:
- 前端是否已构建
- 数据库文件是否存在
- 服务器磁盘空间是否充足
- 服务器权限是否足够

**解决方法**:
```bash
# 检查服务器状态
python status.py

# 查看详细日志
journalctl -u scoutslens -n 50
```

### 问题 3: 服务无法启动

**检查项**:
- 配置文件是否正确
- 端口是否被占用
- 依赖是否安装完整

**解决方法**:
```bash
# 检查服务状态
systemctl status scoutslens

# 查看错误日志
journalctl -u scoutslens -f
```

### 问题 4: 前端无法访问

**检查项**:
- Nginx 是否运行
- 前端文件是否上传成功
- Nginx 配置是否正确

**解决方法**:
```bash
# 检查 Nginx 状态
systemctl status nginx

# 查看 Nginx 错误日志
tail -f /var/log/nginx/error.log

# 测试 Nginx 配置
nginx -t
```

## 安全建议

1. **定期备份**: 建议每天或每周执行一次数据库备份
2. **修改密码**: 定期修改 SSH 密码和 Flask 密钥
3. **配置防火墙**: 使用 ufw 配置防火墙规则
4. **启用 HTTPS**: 使用 Let's Encrypt 配置 SSL 证书
5. **限制访问**: 限制 SSH 访问来源IP

## 扩展功能

### 配置自动备份

使用 cron 定时任务自动备份：

```bash
# 编辑 crontab
crontab -e

# 添加每天凌晨2点备份
0 2 * * * cd /path/to/ScoutsLens/deploy && /usr/bin/python3 backup.py >> /var/log/scoutslens_backup.log 2>&1
```

### 配置 HTTPS

使用 Let's Encrypt 免费证书：

```bash
# 安装 certbot
apt install certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d your-domain.com

# 自动续期
certbot renew --dry-run
```

## 注意事项

1. **首次部署前**确保服务器网络正常
2. **确保SSH密码正确**且服务器允许密码登录
3. **确保前端已构建**（frontend/dist目录存在）
4. **确保数据库文件存在**（database/scoutslens.db）
5. **部署过程中不要中断**脚本执行
6. **部署完成后验证**所有功能正常
7. **定期备份数据库**以防数据丢失
8. **更新代码前先备份**数据库

## 技术支持

如遇到问题，请：
1. 检查服务器状态：`python status.py`
2. 查看日志文件
3. 参考故障排查章节
4. 检查配置文件是否正确

## 版本历史

### v1.0.0 (2026-02-20)
- 初始版本
- 完整的自动化部署流程
- 服务管理脚本
- 备份和回滚功能
