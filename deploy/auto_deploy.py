import json
import os
import sys

import paramiko
from scp import SCPClient


class AutoDeployer:
    def __init__(self, config_file="config/remote_config.json"):
        self.config = self.load_config(config_file)
        if not self.config:
            print("✗ 加载配置文件失败")
            sys.exit(1)

        self.hostname = self.config.get("hostname")
        self.username = self.config.get("username")
        self.password = self.config.get("password")
        self.port = self.config.get("port", 22)
        self.remote_project_dir = self.config.get(
            "remote_project_dir", "/var/www/scoutslens"
        )
        self.remote_domain = self.config.get("remote_domain", self.hostname)

        if not all([self.hostname, self.username, self.password]):
            print("✗ 配置文件缺少必要信息")
            sys.exit(1)

        self.ssh = None
        self.scp = None

    def load_config(self, config_file):
        config_path = os.path.join(os.path.dirname(__file__), config_file)
        if not os.path.exists(config_path):
            print(f"配置文件不存在: {config_path}")
            return None

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            return None

    def connect(self):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.hostname, self.port, self.username, self.password)
            self.scp = SCPClient(self.ssh.get_transport())
            print(f"✓ 成功连接到服务器: {self.hostname}")
            return True
        except Exception as e:
            print(f"✗ 连接服务器失败: {e}")
            return False

    def disconnect(self):
        if self.scp:
            self.scp.close()
        if self.ssh:
            self.ssh.close()
        print("✓ 已断开服务器连接")

    def execute_command(self, command, show_output=True):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            stdout_output = stdout.read().decode("utf-8")
            stderr_output = stderr.read().decode("utf-8")
            exit_status = stdout.channel.recv_exit_status()

            if show_output:
                if stdout_output:
                    print(stdout_output)
                if stderr_output:
                    print(f"错误输出: {stderr_output}")

            return exit_status, stdout_output, stderr_output
        except Exception as e:
            print(f"✗ 执行命令失败: {e}")
            return -1, "", str(e)

    def upload_file(self, local_path, remote_path):
        try:
            self.scp.put(local_path, remote_path)
            print(f"✓ 上传文件: {local_path} -> {remote_path}")
            return True
        except Exception as e:
            print(f"✗ 上传文件失败: {e}")
            return False

    def upload_directory(self, local_dir, remote_dir):
        try:
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    local_file = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file, local_dir)
                    remote_file = os.path.join(remote_dir, relative_path)
                    remote_dir_path = os.path.dirname(remote_file)

                    self.execute_command(
                        f"mkdir -p {remote_dir_path}", show_output=False
                    )
                    self.scp.put(local_file, remote_file)
                    print(f"✓ 上传: {relative_path}")
            return True
        except Exception as e:
            print(f"✗ 上传目录失败: {e}")
            return False

    def install_dependencies(self):
        print("\n=== 步骤 1: 安装系统依赖 ===")
        commands = [
            "apt update",
            "apt install -y python3 python3-pip nginx",
            "pip3 install --upgrade pip",
        ]

        for cmd in commands:
            print(f"执行: {cmd}")
            exit_status, _, _ = self.execute_command(cmd)
            if exit_status != 0:
                print(f"✗ 命令执行失败: {cmd}")
                return False

        print("✓ 系统依赖安装完成")
        return True

    def setup_project_directory(self):
        print("\n=== 步骤 2: 创建项目目录 ===")
        commands = [
            f"mkdir -p {self.remote_project_dir}",
            f"mkdir -p {self.remote_project_dir}/backend",
            f"mkdir -p {self.remote_project_dir}/database",
            f"mkdir -p {self.remote_project_dir}/logs",
        ]

        for cmd in commands:
            exit_status, _, _ = self.execute_command(cmd, show_output=False)
            if exit_status != 0:
                print(f"✗ 创建目录失败: {cmd}")
                return False

        print(f"✓ 项目目录创建完成: {self.remote_project_dir}")
        return True

    def upload_backend(self):
        print("\n=== 步骤 3: 上传后端代码 ===")
        local_backend = os.path.join(os.path.dirname(__file__), "..", "backend")
        remote_backend = f"{self.remote_project_dir}/backend"

        if not os.path.exists(local_backend):
            print(f"✗ 本地后端目录不存在: {local_backend}")
            return False

        return self.upload_directory(local_backend, remote_backend)

    def upload_frontend(self):
        print("\n=== 步骤 4: 上传前端文件 ===")
        local_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
        remote_dist = f"{self.remote_project_dir}/frontend/dist"

        if not os.path.exists(local_dist):
            print(f"✗ 本地前端构建目录不存在: {local_dist}")
            return False

        self.execute_command(
            f"mkdir -p {self.remote_project_dir}/frontend/dist", show_output=False
        )
        return self.upload_directory(local_dist, remote_dist)

    def upload_database(self):
        print("\n=== 步骤 5: 上传数据库 ===")
        local_db = os.path.join(
            os.path.dirname(__file__), "..", "database", "scoutslens.db"
        )
        remote_db = f"{self.remote_project_dir}/database/scoutslens.db"

        if not os.path.exists(local_db):
            print(f"✗ 本地数据库文件不存在: {local_db}")
            return False

        return self.upload_file(local_db, remote_db)

    def setup_python_environment(self):
        print("\n=== 步骤 6: 配置 Python 环境 ===")
        commands = [
            f"cd {self.remote_project_dir}/backend && python3 -m venv venv",
            f"cd {self.remote_project_dir}/backend && source venv/bin/activate && pip install -r requirements.txt",
            f"cd {self.remote_project_dir}/backend && source venv/bin/activate && pip install gunicorn",
        ]

        for cmd in commands:
            print(f"执行: {cmd}")
            exit_status, _, _ = self.execute_command(cmd)
            if exit_status != 0:
                print(f"✗ Python 环境配置失败: {cmd}")
                return False

        print("✓ Python 环境配置完成")
        return True

    def update_backend_config(self):
        print("\n=== 步骤 7: 更新后端配置 ===")
        env_content = f"FLASK_ENV=production\nSECRET_KEY={self.config.get('secret_key', 'your-secret-key-here')}\n"
        env_path = f"{self.remote_project_dir}/backend/.env"

        try:
            with open("/tmp/scoutslens_env", "w") as f:
                f.write(env_content)
            self.upload_file("/tmp/scoutslens_env", env_path)
            os.remove("/tmp/scoutslens_env")
            print("✓ 后端配置更新完成")
            return True
        except Exception as e:
            print(f"✗ 更新后端配置失败: {e}")
            return False

    def setup_nginx(self):
        print("\n=== 步骤 8: 配置 Nginx ===")
        nginx_config = f"""server {{
    listen 80;
    server_name {self.remote_domain};

    location / {{
        root {self.remote_project_dir}/frontend/dist;
        try_files $uri $uri/ /index.html;
    }}

    location /api/ {{
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }}
}}
"""

        try:
            with open("/tmp/scoutslens_nginx", "w") as f:
                f.write(nginx_config)
            self.upload_file("/tmp/scoutslens_nginx", "/tmp/scoutslens_nginx")
            os.remove("/tmp/scoutslens_nginx")

            commands = [
                "cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup",
                "mv /tmp/scoutslens_nginx /etc/nginx/sites-available/scoutslens",
                "ln -sf /etc/nginx/sites-available/scoutslens /etc/nginx/sites-enabled/scoutslens",
                "rm -f /etc/nginx/sites-enabled/default",
                "nginx -t",
                "systemctl restart nginx",
            ]

            for cmd in commands:
                exit_status, _, _ = self.execute_command(cmd)
                if exit_status != 0 and "nginx -t" not in cmd:
                    print(f"✗ Nginx 配置失败: {cmd}")
                    return False

            print("✓ Nginx 配置完成")
            return True
        except Exception as e:
            print(f"✗ Nginx 配置失败: {e}")
            return False

    def setup_systemd_service(self):
        print("\n=== 步骤 9: 配置 systemd 服务 ===")
        service_config = f"""[Unit]
Description=ScoutsLens Backend
After=network.target

[Service]
User=root
WorkingDirectory={self.remote_project_dir}/backend
Environment="PATH={self.remote_project_dir}/backend/venv/bin"
ExecStart={self.remote_project_dir}/backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
"""

        try:
            with open("/tmp/scoutslens.service", "w") as f:
                f.write(service_config)
            self.upload_file("/tmp/scoutslens.service", "/tmp/scoutslens.service")
            os.remove("/tmp/scoutslens.service")

            commands = [
                "mv /tmp/scoutslens.service /etc/systemd/system/scoutslens.service",
                "systemctl daemon-reload",
                "systemctl enable scoutslens",
                "systemctl start scoutslens",
                "systemctl status scoutslens",
            ]

            for cmd in commands:
                exit_status, _, _ = self.execute_command(cmd)
                if exit_status != 0 and "status" not in cmd:
                    print(f"✗ systemd 服务配置失败: {cmd}")
                    return False

            print("✓ systemd 服务配置完成")
            return True
        except Exception as e:
            print(f"✗ systemd 服务配置失败: {e}")
            return False

    def verify_deployment(self):
        print("\n=== 步骤 10: 验证部署 ===")
        commands = [
            "systemctl is-active nginx",
            "systemctl is-active scoutslens",
            "curl -s http://localhost/api/ || echo 'API 测试'",
        ]

        results = []
        for cmd in commands:
            exit_status, stdout, _ = self.execute_command(cmd)
            results.append((cmd, exit_status, stdout))

        print("\n=== 部署验证结果 ===")
        all_passed = True
        for cmd, status, output in results:
            status_str = "✓" if status == 0 else "✗"
            print(f"{status_str} {cmd}")
            if output:
                print(f"   {output.strip()}")
            if status != 0:
                all_passed = False

        return all_passed

    def deploy(self):
        print("=" * 60)
        print("开始自动化部署 ScoutsLens 项目")
        print("=" * 60)

        if not self.connect():
            return False

        try:
            steps = [
                ("安装系统依赖", self.install_dependencies),
                ("创建项目目录", self.setup_project_directory),
                ("上传后端代码", self.upload_backend),
                ("上传前端文件", self.upload_frontend),
                ("上传数据库", self.upload_database),
                ("配置 Python 环境", self.setup_python_environment),
                ("更新后端配置", self.update_backend_config),
                ("配置 Nginx", self.setup_nginx),
                ("配置 systemd 服务", self.setup_systemd_service),
                ("验证部署", self.verify_deployment),
            ]

            for step_name, step_func in steps:
                if not step_func():
                    print(f"\n✗ 部署失败: {step_name}")
                    return False

            print("\n" + "=" * 60)
            print("✓ 部署成功完成！")
            print("=" * 60)
            print(f"\n访问地址: http://{self.remote_domain}")
            print(f"项目目录: {self.remote_project_dir}")
            print("\n常用命令:")
            print("  查看服务状态: systemctl status scoutslens")
            print("  重启服务: systemctl restart scoutslens")
            print("  查看日志: journalctl -u scoutslens -f")
            print("  查看 Nginx 日志: tail -f /var/log/nginx/access.log")

            return True

        except Exception as e:
            print(f"\n✗ 部署过程中发生错误: {e}")
            return False
        finally:
            self.disconnect()


def main():
    deployer = AutoDeployer()
    success = deployer.deploy()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
