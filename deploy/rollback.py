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


def upload_file(hostname, username, password, local_path, remote_path, port=22):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port, username, password)

        scp = SCPClient(ssh.get_transport())
        scp.put(local_path, remote_path)
        scp.close()
        ssh.close()

        return True
    except Exception as e:
        print(f"✗ 上传文件失败: {e}")
        return False


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


def check_fastapi_health(hostname, username, password, port):
    health_check_url = "http://127.0.0.1:8000/docs"
    exit_status, stdout, stderr = execute_remote_command(
        hostname,
        username,
        password,
        f"curl -s -o /dev/null -w '%{{http_code}}' {health_check_url}",
        port,
    )

    if exit_status == 0 and "200" in stdout:
        return True
    return False


def rollback():
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
    print("ScoutsLens FastAPI 回滚脚本")
    print("=" * 60)
    print(f"服务器: {hostname}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    local_backup_dir = os.path.join(os.path.dirname(__file__), "backups")

    if not os.path.exists(local_backup_dir):
        print(f"✗ 本地备份目录不存在: {local_backup_dir}")
        print("\n是否从远程服务器选择备份? (y/n): ", end="")
        choice = input().strip().lower()

        if choice == "y":
            return rollback_from_remote(
                hostname, username, password, port, remote_project_dir
            )
        else:
            return False

    backups = sorted(
        [f for f in os.listdir(local_backup_dir) if f.endswith(".db")], reverse=True
    )

    if not backups:
        print("✗ 本地没有找到可用的备份文件")
        print("\n是否从远程服务器选择备份? (y/n): ", end="")
        choice = input().strip().lower()

        if choice == "y":
            return rollback_from_remote(
                hostname, username, password, port, remote_project_dir
            )
        else:
            return False

    print("\n可用的本地备份文件:")
    for i, backup in enumerate(backups[:10], 1):
        backup_path = os.path.join(local_backup_dir, backup)
        size = os.path.getsize(backup_path) / 1024
        print(f"{i}. {backup} ({size:.2f} KB)")

    print("\n请选择要恢复的备份文件:")
    choice = input("输入编号 (1-10) 或输入 'remote' 从远程选择: ").strip()

    if choice.lower() == "remote":
        return rollback_from_remote(
            hostname, username, password, port, remote_project_dir
        )

    try:
        index = int(choice) - 1
        if index < 0 or index >= len(backups):
            print("✗ 无效的选择")
            return False

        selected_backup = backups[index]
        local_backup = os.path.join(local_backup_dir, selected_backup)
        remote_db = f"{remote_project_dir}/database/scoutslens.db"

        print(f"\n正在恢复备份: {selected_backup}")

        print("\n1. 备份当前数据库...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exit_status, _, _ = execute_remote_command(
            hostname,
            username,
            password,
            f"cp {remote_db} {remote_project_dir}/database/scoutslens_backup_{timestamp}.db",
            port,
        )

        if exit_status == 0:
            print("✓ 当前数据库已备份")
        else:
            print("⚠ 当前数据库备份失败，继续回滚...")

        print("\n2. 上传备份数据库...")
        if upload_file(hostname, username, password, local_backup, remote_db, port):
            print("✓ 备份数据库上传成功")
        else:
            print("✗ 备份数据库上传失败")
            return False

        print("\n3. 重启 FastAPI 服务...")
        exit_status, _, _ = execute_remote_command(
            hostname, username, password, "systemctl restart scoutslens", port
        )

        if exit_status == 0:
            print("✓ FastAPI 服务重启成功")
        else:
            print("⚠ FastAPI 服务重启可能存在问题")

        print("\n4. 等待服务启动...")
        import time

        time.sleep(3)

        print("\n5. 验证服务健康状态...")
        if check_fastapi_health(hostname, username, password, port):
            print("✓ FastAPI 服务健康检查通过")
        else:
            print("⚠ FastAPI 服务健康检查失败，请检查日志")

        print("\n" + "=" * 60)
        print("✓ 回滚完成！")
        print("=" * 60)
        print(f"\n已恢复备份: {selected_backup}")
        print("如果出现问题，可以使用之前的备份文件重新回滚")

        return True

    except ValueError:
        print("✗ 无效的输入")
        return False


def rollback_from_remote(hostname, username, password, port, remote_project_dir):
    print("\n" + "=" * 60)
    print("从远程服务器选择备份")
    print("=" * 60)

    remote_backup_dir = f"{remote_project_dir}/backups"

    exit_status, stdout, stderr = execute_remote_command(
        hostname, username, password, f"ls -t {remote_backup_dir}/scoutslens_*.db", port
    )

    if exit_status != 0 or not stdout.strip():
        print("✗ 远程服务器没有找到可用的备份文件")
        return False

    backups = [line.strip() for line in stdout.strip().split("\n") if line.strip()]

    if not backups:
        print("✗ 远程服务器没有找到可用的备份文件")
        return False

    print("\n可用的远程备份文件:")
    for i, backup in enumerate(backups[:10], 1):
        print(f"{i}. {backup}")

    print("\n请选择要恢复的备份文件:")
    choice = input("输入编号 (1-10): ").strip()

    try:
        index = int(choice) - 1
        if index < 0 or index >= len(backups):
            print("✗ 无效的选择")
            return False

        selected_backup = backups[index]
        remote_db = f"{remote_project_dir}/database/scoutslens.db"

        print(f"\n正在恢复远程备份: {selected_backup}")

        print("\n1. 备份当前数据库...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exit_status, _, _ = execute_remote_command(
            hostname,
            username,
            password,
            f"cp {remote_db} {remote_project_dir}/database/scoutslens_backup_{timestamp}.db",
            port,
        )

        if exit_status == 0:
            print("✓ 当前数据库已备份")
        else:
            print("⚠ 当前数据库备份失败，继续回滚...")

        print("\n2. 恢复备份数据库...")
        exit_status, _, _ = execute_remote_command(
            hostname, username, password, f"cp {selected_backup} {remote_db}", port
        )

        if exit_status == 0:
            print("✓ 备份数据库恢复成功")
        else:
            print("✗ 备份数据库恢复失败")
            return False

        print("\n3. 重启 FastAPI 服务...")
        exit_status, _, _ = execute_remote_command(
            hostname, username, password, "systemctl restart scoutslens", port
        )

        if exit_status == 0:
            print("✓ FastAPI 服务重启成功")
        else:
            print("⚠ FastAPI 服务重启可能存在问题")

        print("\n4. 等待服务启动...")
        import time

        time.sleep(3)

        print("\n5. 验证服务健康状态...")
        if check_fastapi_health(hostname, username, password, port):
            print("✓ FastAPI 服务健康检查通过")
        else:
            print("⚠ FastAPI 服务健康检查失败，请检查日志")

        print("\n" + "=" * 60)
        print("✓ 回滚完成！")
        print("=" * 60)
        print(f"\n已恢复备份: {selected_backup}")
        print("如果出现问题，可以使用之前的备份文件重新回滚")

        return True

    except ValueError:
        print("✗ 无效的输入")
        return False


def main():
    success = rollback()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
