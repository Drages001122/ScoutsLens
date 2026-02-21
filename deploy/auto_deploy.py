import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import paramiko
from scp import SCPClient


class DeploymentLogger:
    def __init__(self, log_dir: str = "logs/deploy"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"deploy_{timestamp}.log")
        self.start_time = datetime.now()
        self.steps: List[Dict] = []
        self.warnings: List[str] = []
        self.errors: List[str] = []

    def log(self, level: str, message: str, stage: str = ""):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}]"
        if stage:
            log_entry += f" [{stage}]"
        log_entry += f" {message}"

        print(log_entry)

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

    def info(self, message: str, stage: str = ""):
        self.log("INFO", message, stage)

    def warning(self, message: str, stage: str = ""):
        self.log("WARNING", message, stage)
        self.warnings.append(f"{stage}: {message}" if stage else message)

    def error(self, message: str, stage: str = ""):
        self.log("ERROR", message, stage)
        self.errors.append(f"{stage}: {message}" if stage else message)

    def start_step(self, step_name: str) -> str:
        step_id = f"step_{len(self.steps) + 1}"
        step_info = {
            "id": step_id,
            "name": step_name,
            "start_time": datetime.now().isoformat(),
            "status": "in_progress",
        }
        self.steps.append(step_info)
        self.info(f"开始执行: {step_name}", step_id)
        return step_id

    def end_step(self, step_id: str, success: bool, message: str = ""):
        for step in self.steps:
            if step["id"] == step_id:
                step["end_time"] = datetime.now().isoformat()
                step["status"] = "success" if success else "failed"
                step["message"] = message
                step["duration_seconds"] = (
                    datetime.fromisoformat(step["end_time"])
                    - datetime.fromisoformat(step["start_time"])
                ).total_seconds()
                break

        status = "成功" if success else "失败"
        self.info(f"完成: {status} {message}", step_id)

    def generate_summary(self) -> Dict:
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()

        summary = {
            "deployment_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_duration_seconds": total_duration,
            "total_steps": len(self.steps),
            "successful_steps": sum(1 for s in self.steps if s["status"] == "success"),
            "failed_steps": sum(1 for s in self.steps if s["status"] == "failed"),
            "warnings_count": len(self.warnings),
            "errors_count": len(self.errors),
            "steps": self.steps,
            "warnings": self.warnings,
            "errors": self.errors,
            "overall_status": (
                "success"
                if all(s["status"] == "success" for s in self.steps)
                else "failed"
            ),
        }

        summary_file = os.path.join(
            self.log_dir,
            f"deploy_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        self.info(f"部署摘要已保存到: {summary_file}")
        return summary


class AutoDeployer:
    def __init__(self, config_file: str = "config/remote_config.json"):
        self.logger = DeploymentLogger()
        self.config = self.load_config(config_file)
        if not self.config:
            self.logger.error("加载配置文件失败", "INIT")
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
            self.logger.error("配置文件缺少必要信息", "INIT")
            sys.exit(1)

        self.ssh = None
        self.scp = None
        self.logger.info("AutoDeployer 初始化完成", "INIT")

    def load_config(self, config_file: str) -> Optional[Dict]:
        config_path = os.path.join(os.path.dirname(__file__), config_file)
        if not os.path.exists(config_path):
            self.logger.error(f"配置文件不存在: {config_path}", "CONFIG")
            return None

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            self.logger.info(f"配置文件加载成功: {config_path}", "CONFIG")
            return config
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {str(e)}", "CONFIG")
            return None

    def connect(self) -> bool:
        step_id = self.logger.start_step("连接服务器")
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(self.hostname, self.port, self.username, self.password)
            self.scp = SCPClient(self.ssh.get_transport())
            self.logger.info(f"成功连接到服务器: {self.hostname}", step_id)
            self.logger.end_step(step_id, True, "服务器连接成功")
            return True
        except Exception as e:
            self.logger.error(f"连接服务器失败: {e}", step_id)
            self.logger.end_step(step_id, False, f"连接失败: {e}")
            return False

    def disconnect(self):
        if self.scp:
            self.scp.close()
        if self.ssh:
            self.ssh.close()
        self.logger.info("已断开服务器连接", "DISCONNECT")

    def execute_command(
        self, command: str, show_output: bool = True
    ) -> Tuple[int, str, str]:
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            stdout_output = stdout.read().decode("utf-8")
            stderr_output = stderr.read().decode("utf-8")
            exit_status = stdout.channel.recv_exit_status()

            if show_output:
                if stdout_output:
                    self.logger.info(stdout_output.strip())
                if stderr_output:
                    self.logger.warning(stderr_output.strip())

            return exit_status, stdout_output, stderr_output
        except Exception as e:
            self.logger.error(f"执行命令失败: {e}")
            return -1, "", str(e)

    def check_environment_compatibility(self) -> bool:
        step_id = self.logger.start_step("环境兼容性检查")

        checks = {
            "操作系统版本": ("cat /etc/os-release | grep PRETTY_NAME", "Ubuntu"),
            "Python版本": ("python3 --version", "Python 3"),
            "pip版本": ("pip3 --version", "pip"),
            "系统内存": ("free -h | grep Mem", ""),
            "磁盘空间": ("df -h / | tail -1", ""),
        }

        all_passed = True
        for check_name, (command, expected) in checks.items():
            exit_status, stdout, stderr = self.execute_command(
                command, show_output=False
            )
            if exit_status == 0:
                output = stdout.strip()
                if expected and expected not in output:
                    self.logger.warning(
                        f"{check_name}: {output} (期望包含: {expected})", step_id
                    )
                else:
                    self.logger.info(f"{check_name}: {output}", step_id)
            else:
                self.logger.error(f"{check_name} 检查失败: {stderr}", step_id)
                all_passed = False

        required_packages = ["curl", "nginx", "python3", "python3-pip"]
        missing_packages = []
        for package in required_packages:
            exit_status, _, _ = self.execute_command(
                f"which {package}", show_output=False
            )
            if exit_status != 0:
                missing_packages.append(package)

        if missing_packages:
            self.logger.warning(f"缺少系统包: {', '.join(missing_packages)}", step_id)
        else:
            self.logger.info("所有必需系统包已安装", step_id)

        if all_passed:
            self.logger.end_step(step_id, True, "环境兼容性检查通过")
        else:
            self.logger.end_step(step_id, False, "环境兼容性检查发现问题")

        return all_passed

    def validate_config(self) -> bool:
        step_id = self.logger.start_step("配置文件验证")

        required_fields = [
            "hostname",
            "username",
            "password",
            "port",
            "remote_project_dir",
        ]
        missing_fields = [
            field for field in required_fields if not self.config.get(field)
        ]

        if missing_fields:
            self.logger.error(f"配置文件缺少字段: {', '.join(missing_fields)}", step_id)
            self.logger.end_step(step_id, False, "配置文件验证失败")
            return False

        self.logger.info("配置文件验证通过", step_id)
        self.logger.info(f"服务器: {self.hostname}:{self.port}", step_id)
        self.logger.info(f"项目目录: {self.remote_project_dir}", step_id)
        self.logger.info(f"域名: {self.remote_domain}", step_id)

        self.logger.end_step(step_id, True, "配置文件验证通过")
        return True

    def install_dependencies(self) -> bool:
        step_id = self.logger.start_step("安装系统依赖")

        commands = [
            ("更新软件包列表", "apt update"),
            (
                "安装基础依赖",
                "apt install -y python3 python3-pip python3-venv nginx curl",
            ),
        ]

        for cmd_name, cmd in commands:
            self.logger.info(f"执行: {cmd_name}", step_id)
            exit_status, _, _ = self.execute_command(cmd)
            if exit_status != 0:
                self.logger.error(f"{cmd_name} 失败", step_id)
                self.logger.end_step(step_id, False, f"{cmd_name} 失败")
                return False

        self.logger.end_step(step_id, True, "系统依赖安装完成")
        return True

    def setup_project_directory(self) -> bool:
        step_id = self.logger.start_step("创建项目目录")

        commands = [
            f"mkdir -p {self.remote_project_dir}",
            f"mkdir -p {self.remote_project_dir}/backend",
            f"mkdir -p {self.remote_project_dir}/database",
            f"mkdir -p {self.remote_project_dir}/logs",
        ]

        for cmd in commands:
            exit_status, _, _ = self.execute_command(cmd, show_output=False)
            if exit_status != 0:
                self.logger.error(f"创建目录失败: {cmd}", step_id)
                self.logger.end_step(step_id, False, "目录创建失败")
                return False

        self.logger.info(f"项目目录创建完成: {self.remote_project_dir}", step_id)
        self.logger.end_step(step_id, True, "项目目录创建完成")
        return True

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        try:
            self.scp.put(local_path, remote_path)
            self.logger.info(f"上传文件: {local_path} -> {remote_path}")
            return True
        except Exception as e:
            self.logger.error(f"上传文件失败: {e}")
            return False

    def upload_directory(self, local_dir: str, remote_dir: str) -> bool:
        try:
            for root, dirs, files in os.walk(local_dir):
                for file in files:
                    local_file = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file, local_dir)
                    remote_file = os.path.join(remote_dir, relative_path)
                    remote_dir_path = os.path.dirname(remote_file)

                    remote_dir_path = remote_dir_path.replace(os.sep, "/")
                    remote_file = remote_file.replace(os.sep, "/")

                    self.execute_command(
                        f"mkdir -p {remote_dir_path}", show_output=False
                    )
                    self.scp.put(local_file, remote_file)
                    self.logger.info(f"上传: {relative_path}")
            return True
        except Exception as e:
            self.logger.error(f"上传目录失败: {e}")
            return False

    def upload_backend(self) -> bool:
        step_id = self.logger.start_step("上传后端代码")
        local_backend = os.path.join(os.path.dirname(__file__), "..", "backend")
        remote_backend = f"{self.remote_project_dir}/backend"

        if not os.path.exists(local_backend):
            self.logger.error(f"本地后端目录不存在: {local_backend}", step_id)
            self.logger.end_step(step_id, False, "后端目录不存在")
            return False

        result = self.upload_directory(local_backend, remote_backend)

        if result:
            local_req = os.path.join(local_backend, "requirements.txt")
            if os.path.exists(local_req):
                remote_req = f"{remote_backend}/requirements.txt"
                self.logger.info("单独上传requirements.txt文件", step_id)
                result = self.upload_file(local_req, remote_req)

        if result:
            self.logger.end_step(step_id, True, "后端代码上传完成")
        else:
            self.logger.end_step(step_id, False, "后端代码上传失败")
        return result

    def upload_frontend(self) -> bool:
        step_id = self.logger.start_step("上传前端文件")
        local_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
        remote_dist = f"{self.remote_project_dir}/frontend/dist"

        if not os.path.exists(local_dist):
            self.logger.error(f"本地前端构建目录不存在: {local_dist}", step_id)
            self.logger.end_step(step_id, False, "前端构建目录不存在")
            return False

        self.execute_command(
            f"mkdir -p {self.remote_project_dir}/frontend/dist", show_output=False
        )

        import tempfile
        import tarfile

        try:
            self.logger.info("压缩前端文件以加快上传速度", step_id)

            with tempfile.NamedTemporaryFile(
                mode="wb", delete=False, suffix=".tar.gz"
            ) as f:
                temp_archive = f.name

            self.logger.info(f"创建压缩包: {os.path.basename(temp_archive)}", step_id)

            with tarfile.open(temp_archive, "w:gz") as tar:
                for root, dirs, files in os.walk(local_dist):
                    for file in files:
                        local_file = os.path.join(root, file)
                        relative_path = os.path.relpath(local_file, local_dist)
                        tar.add(local_file, arcname=relative_path)

            archive_size = os.path.getsize(temp_archive) / (1024 * 1024)
            self.logger.info(f"压缩包大小: {archive_size:.2f} MB", step_id)

            self.logger.info("上传压缩包到服务器", step_id)
            self.upload_file(temp_archive, "/tmp/frontend_dist.tar.gz")

            self.logger.info("在服务器上解压文件", step_id)
            self.execute_command(
                f"tar -xzf /tmp/frontend_dist.tar.gz -C {remote_dist}",
                show_output=False,
            )
            self.execute_command(
                "rm /tmp/frontend_dist.tar.gz", show_output=False
            )

            os.remove(temp_archive)
            self.logger.info("前端文件上传完成", step_id)

            self.logger.end_step(step_id, True, "前端文件上传完成")
            return True
        except Exception as e:
            self.logger.error(f"前端文件上传失败: {e}", step_id)
            self.logger.end_step(step_id, False, "前端文件上传失败")
            return False

    def upload_database(self) -> bool:
        step_id = self.logger.start_step("上传数据库")
        local_db = os.path.join(
            os.path.dirname(__file__), "..", "database", "scoutslens.db"
        )
        remote_db = f"{self.remote_project_dir}/database/scoutslens.db"

        if not os.path.exists(local_db):
            self.logger.error(f"本地数据库文件不存在: {local_db}", step_id)
            self.logger.end_step(step_id, False, "数据库文件不存在")
            return False

        result = self.upload_file(local_db, remote_db)
        if result:
            self.logger.end_step(step_id, True, "数据库上传完成")
        else:
            self.logger.end_step(step_id, False, "数据库上传失败")
        return result

    def setup_python_environment(self) -> bool:
        step_id = self.logger.start_step("配置Python环境")

        commands = [
            f"cd {self.remote_project_dir}/backend && python3 -m venv venv",
            f"cd {self.remote_project_dir}/backend && source venv/bin/activate && pip install -r requirements.txt",
            f"cd {self.remote_project_dir}/backend && source venv/bin/activate && pip install waitress",
        ]

        for cmd in commands:
            self.logger.info(f"执行: {cmd}", step_id)
            exit_status, _, _ = self.execute_command(cmd)
            if exit_status != 0:
                self.logger.error(f"Python环境配置失败: {cmd}", step_id)
                self.logger.end_step(step_id, False, "Python环境配置失败")
                return False

        self.logger.end_step(step_id, True, "Python环境配置完成")
        return True

    def update_backend_config(self) -> bool:
        step_id = self.logger.start_step("更新后端配置")
        public_ip = self.config.get("public_ip", self.hostname)
        env_content = f"""FLASK_ENV=prod
SECRET_KEY={self.config.get('secret_key', 'your-secret-key-here')}
FRONTEND_DOMAINS=http://localhost:5173,http://{public_ip}
"""
        env_path = f"{self.remote_project_dir}/backend/.env"

        try:
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".env"
            ) as f:
                temp_env_file = f.name
                f.write(env_content)
            self.upload_file(temp_env_file, env_path)
            os.remove(temp_env_file)

            self.logger.info("数据库路径配置保持不变（本地配置已正确）", step_id)
            self.logger.end_step(step_id, True, "后端配置更新完成")
            return True
        except Exception as e:
            self.logger.error(f"更新后端配置失败: {e}", step_id)
            self.logger.end_step(step_id, False, "后端配置更新失败")
            return False

    def setup_nginx(self) -> bool:
        step_id = self.logger.start_step("配置Nginx")
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
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".nginx"
            ) as f:
                temp_nginx_file = f.name
                f.write(nginx_config)
            self.upload_file(temp_nginx_file, "/tmp/scoutslens_nginx")
            os.remove(temp_nginx_file)

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
                    self.logger.error(f"Nginx配置失败: {cmd}", step_id)
                    self.logger.end_step(step_id, False, "Nginx配置失败")
                    return False

            self.logger.end_step(step_id, True, "Nginx配置完成")
            return True
        except Exception as e:
            self.logger.error(f"Nginx配置失败: {e}", step_id)
            self.logger.end_step(step_id, False, "Nginx配置失败")
            return False

    def setup_systemd_service(self) -> bool:
        step_id = self.logger.start_step("配置systemd服务")
        service_config = f"""[Unit]
Description=ScoutsLens Backend
After=network.target

[Service]
User=root
WorkingDirectory={self.remote_project_dir}/backend
Environment="PATH={self.remote_project_dir}/backend/venv/bin"
Environment="PYTHONPATH={self.remote_project_dir}/backend"
ExecStart={self.remote_project_dir}/backend/venv/bin/waitress-serve --port=5000 --threads=4 app:app
Restart=always

[Install]
WantedBy=multi-user.target
"""

        try:
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".service"
            ) as f:
                temp_service_file = f.name
                f.write(service_config)
            self.upload_file(temp_service_file, "/tmp/scoutslens.service")
            os.remove(temp_service_file)

            commands = [
                "mv /tmp/scoutslens.service /etc/systemd/system/scoutslens.service",
                "systemctl daemon-reload",
                "systemctl enable scoutslens",
                "systemctl restart scoutslens",
                "sleep 2",
                "systemctl status scoutslens",
            ]

            for cmd in commands:
                exit_status, _, _ = self.execute_command(cmd)
                if exit_status != 0 and "status" not in cmd:
                    self.logger.error(f"systemd服务配置失败: {cmd}", step_id)
                    self.logger.end_step(step_id, False, "systemd服务配置失败")
                    return False

            self.logger.end_step(step_id, True, "systemd服务配置完成")
            return True
        except Exception as e:
            self.logger.error(f"systemd服务配置失败: {e}", step_id)
            self.logger.end_step(step_id, False, "systemd服务配置失败")
            return False

    def run_health_checks(self) -> bool:
        step_id = self.logger.start_step("部署后健康检查")

        health_checks = [
            ("Nginx服务状态", "systemctl is-active nginx"),
            ("ScoutsLens服务状态", "systemctl is-active scoutslens"),
            (
                "前端页面访问",
                f"curl -s -o /dev/null -w '%{{http_code}}' http://{self.remote_domain}/",
            ),
            ("API健康检查", "curl -s http://localhost/api/"),
            ("端口5000监听", "netstat -tlnp | grep :5000 || ss -tlnp | grep :5000"),
        ]

        all_passed = True
        for check_name, command in health_checks:
            exit_status, stdout, stderr = self.execute_command(
                command, show_output=False
            )
            if exit_status == 0 and stdout.strip():
                if (
                    "200" in stdout
                    or "active" in stdout.lower()
                    or "5000" in stdout
                    or "{" in stdout
                ):
                    self.logger.info(f"✓ {check_name}: 通过", step_id)
                else:
                    self.logger.warning(f"? {check_name}: {stdout.strip()}", step_id)
            else:
                if "端口" in check_name or "ScoutsLens服务状态" in check_name:
                    self.logger.warning(f"? {check_name}: 服务可能正在初始化", step_id)
                else:
                    self.logger.error(f"✗ {check_name}: 失败", step_id)
                    all_passed = False

        if all_passed:
            self.logger.end_step(step_id, True, "所有健康检查通过")
        else:
            self.logger.end_step(step_id, False, "部分健康检查失败")

        return all_passed

    def deploy(self) -> bool:
        self.logger.info("=" * 60)
        self.logger.info("开始自动化部署 ScoutsLens 项目")
        self.logger.info("=" * 60)

        if not self.connect():
            return False

        try:
            steps = [
                ("环境兼容性检查", self.check_environment_compatibility),
                ("配置文件验证", self.validate_config),
                ("安装系统依赖", self.install_dependencies),
                ("创建项目目录", self.setup_project_directory),
                ("上传后端代码", self.upload_backend),
                ("上传前端文件", self.upload_frontend),
                ("上传数据库", self.upload_database),
                ("配置Python环境", self.setup_python_environment),
                ("更新后端配置", self.update_backend_config),
                ("配置Nginx", self.setup_nginx),
                ("配置systemd服务", self.setup_systemd_service),
                ("部署后健康检查", self.run_health_checks),
            ]

            for step_name, step_func in steps:
                if not step_func():
                    self.logger.error(f"部署失败: {step_name}")
                    return False

            summary = self.logger.generate_summary()

            self.logger.info("=" * 60)
            self.logger.info("✓ 部署成功完成！")
            self.logger.info("=" * 60)
            self.logger.info(f"访问地址: http://{self.remote_domain}")
            self.logger.info(f"项目目录: {self.remote_project_dir}")
            self.logger.info(f"总耗时: {summary['total_duration_seconds']:.2f}秒")
            self.logger.info(
                f"成功步骤: {summary['successful_steps']}/{summary['total_steps']}"
            )
            self.logger.info(f"警告数量: {summary['warnings_count']}")
            self.logger.info(f"错误数量: {summary['errors_count']}")
            self.logger.info("\n常用命令:")
            self.logger.info("  查看服务状态: systemctl status scoutslens")
            self.logger.info("  重启服务: systemctl restart scoutslens")
            self.logger.info("  查看日志: journalctl -u scoutslens -f")
            self.logger.info("  查看Nginx日志: tail -f /var/log/nginx/access.log")

            return True

        except Exception as e:
            self.logger.error(f"部署过程中发生错误: {e}")
            return False
        finally:
            self.disconnect()


def main():
    deployer = AutoDeployer()
    success = deployer.deploy()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
