import json
import os
import sys
from datetime import datetime

import paramiko


def load_config(config_file="config/remote_config.json"):
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


def execute_remote_command(hostname, username, password, command, port=22):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port, username, password)

        stdin, stdout, stderr = ssh.exec_command(command)

        stdout_output = stdout.read().decode("utf-8")
        stderr_output = stderr.read().decode("utf-8")
        exit_status = stdout.channel.recv_exit_status()

        ssh.close()

        return exit_status, stdout_output, stderr_output
    except Exception as e:
        print(f"✗ 执行命令失败: {e}")
        return -1, "", str(e)


def backup_database_before_start(
    hostname, username, password, port, remote_project_dir
):
    print("\n" + "=" * 60)
    print("部署前数据库备份")
    print("=" * 60)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"{remote_project_dir}/backups"
    remote_db = f"{remote_project_dir}/database/scoutslens.db"
    backup_file = f"{backup_dir}/scoutslens_backup_{timestamp}.db"

    exit_status, _, _ = execute_remote_command(
        hostname, username, password, f"mkdir -p {backup_dir}", port
    )

    if exit_status != 0:
        print("⚠ 创建备份目录失败")
        return False

    exit_status, _, _ = execute_remote_command(
        hostname, username, password, f"cp {remote_db} {backup_file}", port
    )

    if exit_status == 0:
        print(f"✓ 数据库备份成功: {backup_file}")
        return True
    else:
        print("⚠ 数据库备份失败")
        return False


def check_fastapi_health(hostname, username, password, port, remote_project_dir):
    print("\n检查FastAPI应用健康状态...")

    health_check_url = "http://127.0.0.1:8000/docs"
    exit_status, stdout, stderr = execute_remote_command(
        hostname,
        username,
        password,
        f"curl -s -o /dev/null -w '%{{http_code}}' {health_check_url}",
        port,
    )

    if exit_status == 0 and "200" in stdout:
        print("✓ FastAPI应用健康检查通过")
        return True
    else:
        print("⚠ FastAPI应用健康检查失败")
        return False


def start_service():
    config = load_config()
    if not config:
        print("✗ 加载配置文件失败")
        return False

    hostname = config.get("hostname")
    username = config.get("username")
    password = config.get("password")
    port = config.get("port", 22)
    remote_project_dir = config.get("remote_project_dir", "/var/www/scoutslens")

    if not all([hostname, username, password]):
        print("✗ 配置文件缺少必要信息")
        return False

    print("=" * 60)
    print("启动 ScoutsLens FastAPI 服务")
    print("=" * 60)
    print(f"服务器: {hostname}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    backup_success = backup_database_before_start(
        hostname, username, password, port, remote_project_dir
    )
    if not backup_success:
        print("⚠ 数据库备份失败，但继续启动服务...")

    commands = [
        ("启动 FastAPI 应用服务", "systemctl start scoutslens"),
        ("启动 Nginx", "systemctl start nginx"),
        ("等待服务启动", "sleep 3"),
        ("检查 FastAPI 服务状态", "systemctl status scoutslens --no-pager"),
        ("检查 Nginx 状态", "systemctl status nginx --no-pager"),
    ]

    all_success = True
    for desc, cmd in commands:
        print(f"\n{desc}...")
        exit_status, stdout, stderr = execute_remote_command(
            hostname, username, password, cmd, port
        )

        if exit_status == 0:
            print(f"✓ {desc} 成功")
            if stdout and "status" in desc:
                print(stdout[:300])
        else:
            print(f"✗ {desc} 失败")
            if stderr:
                print(stderr)
            all_success = False

    health_ok = check_fastapi_health(
        hostname, username, password, port, remote_project_dir
    )
    if not health_ok:
        print("⚠ FastAPI健康检查失败，请检查服务日志")
        all_success = False

    print("\n" + "=" * 60)
    if all_success:
        print("✓ FastAPI服务启动成功！")
        print("✓ 访问地址: http://{}:8000".format(config.get("public_ip", hostname)))
        print(
            "✓ API文档: http://{}:8000/docs".format(config.get("public_ip", hostname))
        )
    else:
        print("✗ 部分服务启动失败！")
        print("提示: 请检查日志文件: {}backend/logs/app.log".format(remote_project_dir))
    print("=" * 60)

    return all_success


def main():
    success = start_service()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
