import json
import os
import sys
from datetime import datetime

import paramiko
from scp import SCPClient


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


def download_file(hostname, username, password, remote_path, local_path, port=22):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port, username, password)

        scp = SCPClient(ssh.get_transport())
        scp.get(remote_path, local_path)
        scp.close()
        ssh.close()

        return True
    except Exception as e:
        print(f"✗ 下载文件失败: {e}")
        return False


def backup_database():
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
    print("备份 ScoutsLens 数据库")
    print("=" * 60)
    print(f"服务器: {hostname}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    remote_db = f"{remote_project_dir}/database/scoutslens.db"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_backup_dir = os.path.join(os.path.dirname(__file__), "backups")

    if not os.path.exists(local_backup_dir):
        os.makedirs(local_backup_dir)
        print(f"✓ 创建本地备份目录: {local_backup_dir}")

    local_backup = os.path.join(local_backup_dir, f"scoutslens_{timestamp}.db")

    print("\n正在下载数据库文件...")
    print(f"远程路径: {remote_db}")
    print(f"本地路径: {local_backup}")

    if download_file(hostname, username, password, remote_db, local_backup, port):
        print(f"✓ 数据库备份成功: {local_backup}")

        file_size = os.path.getsize(local_backup)
        print(f"文件大小: {file_size / 1024:.2f} KB")

        print("\n" + "=" * 60)
        print("✓ 备份完成！")
        print("=" * 60)
        return True
    else:
        print("\n✗ 备份失败！")
        return False


def main():
    success = backup_database()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
