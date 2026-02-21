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


def main():
    print("=" * 60)
    print("ScoutsLens 自动清理并重新部署")
    print("=" * 60)

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

    print(f"服务器: {hostname}")
    print("清理目录: /var/www/")
    print(f"项目目录: {remote_project_dir}")

    print("\n开始执行完全清理并重新部署...")

    print("\n1. 备份数据库...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"/tmp/scoutslens_backup_{timestamp}"

    exit_status, _, _ = execute_remote_command(
        hostname, username, password, f"mkdir -p {backup_dir}", port
    )

    if exit_status == 0:
        exit_status, _, _ = execute_remote_command(
            hostname,
            username,
            password,
            f"cp {remote_project_dir}/database/scoutslens.db {backup_dir}/scoutslens.db",
            port,
        )
        if exit_status == 0:
            print("✓ 数据库备份完成")
        else:
            print("⚠ 数据库备份失败，继续操作...")
    else:
        print("⚠ 创建备份目录失败，继续操作...")

    print("\n2. 停止服务...")
    execute_remote_command(
        hostname, username, password, "systemctl stop scoutslens", port
    )
    execute_remote_command(hostname, username, password, "systemctl stop nginx", port)
    print("✓ 服务已停止")

    print("\n3. 删除整个 /var/www/ 目录...")
    exit_status, _, _ = execute_remote_command(
        hostname, username, password, "rm -rf /var/www/*", port
    )
    if exit_status == 0:
        print("✓ /var/www/ 目录已完全清理")
    else:
        print("⚠ /var/www/ 目录清理可能存在问题")

    print("\n4. 重新创建目录结构...")
    commands = [
        f"mkdir -p {remote_project_dir}/backend",
        f"mkdir -p {remote_project_dir}/frontend/dist",
        f"mkdir -p {remote_project_dir}/database",
        f"mkdir -p {remote_project_dir}/logs",
        f"mkdir -p {remote_project_dir}/backups",
    ]

    for cmd in commands:
        exit_status, _, _ = execute_remote_command(
            hostname, username, password, cmd, port
        )

    print("✓ 目录结构已创建")

    print("\n5. 恢复数据库...")
    exit_status, _, _ = execute_remote_command(
        hostname,
        username,
        password,
        f"cp {backup_dir}/scoutslens.db {remote_project_dir}/database/scoutslens.db",
        port,
    )
    if exit_status == 0:
        print("✓ 数据库已恢复")
    else:
        print("⚠ 数据库恢复失败")

    print("\n" + "=" * 60)
    print("✓ 完全清理完成!")
    print("=" * 60)
    print("\n接下来请执行以下步骤:")
    print("1. 运行: python deploy/build.py")
    print("2. 运行: python deploy/update.py")
    print("3. 运行: python deploy/start.py")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
