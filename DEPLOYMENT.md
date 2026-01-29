# 部署说明

## 环境要求

- Nginx
- Python 3.8+
- Node.js 14+

## 部署步骤

### 1. 构建前端项目

在前端目录下执行以下命令：

```bash
cd frontend
npm install
npm run build
```

构建完成后，前端代码会生成在 `frontend/dist` 目录中。

### 2. 启动后端服务

在后端目录下执行以下命令：

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 3. 配置 Nginx

1. 复制 `nginx.conf` 文件到 Nginx 配置目录（例如 `/etc/nginx/conf.d/` 或 `C:\nginx\conf\`）。

2. 修改 `nginx.conf` 文件中的前端静态文件路径，确保指向正确的 `frontend/dist` 目录：

```nginx
location / {
    root d:\PycharmProjects\ScoutsLens\frontend\dist;
    index index.html;
    try_files $uri $uri/ /index.html;
}
```

3. 启动或重启 Nginx 服务：

```bash
# Linux
sudo systemctl restart nginx

# Windows
nginx -s reload
```

### 4. 访问应用

打开浏览器，访问 `http://localhost` 即可访问应用。

## 配置说明

### Nginx 配置

- 前端静态文件通过 `location /` 配置，指向 `frontend/dist` 目录。
- 后端 API 通过 `location /api/` 配置，反向代理到 `http://localhost:5000`。

### 前端 API 配置

前端 API 配置文件为 `frontend/src/config/api.js`，使用相对路径作为 API 基础 URL，这样当通过 Nginx 访问时，API 请求会自动路由到正确的后端服务。

### 后端配置

后端服务运行在 `127.0.0.1:5000`，关闭了 debug 模式，适合生产环境使用。

## 故障排除

1. **无法访问应用**：检查 Nginx 服务是否正常运行，端口是否被占用。
2. **API 请求失败**：检查后端服务是否正常运行，Nginx 配置中的反向代理设置是否正确。
3. **前端页面显示异常**：检查前端构建是否成功，Nginx 配置中的静态文件路径是否正确。
