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


def check_service_status():
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
    print("ScoutsLens 服务状态检查")
    print("=" * 60)
    print(f"服务器: {hostname}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    checks = [
        ("应用服务状态", "systemctl is-active scoutslens"),
        ("Nginx 状态", "systemctl is-active nginx"),
        ("应用服务详情", "systemctl status scoutslens --no-pager"),
        ("Nginx 详情", "systemctl status nginx --no-pager"),
        ("磁盘使用情况", f"df -h {remote_project_dir}"),
        ("内存使用情况", "free -h"),
        ("CPU 使用情况", "top -bn1 | head -20"),
        ("应用服务日志", "journalctl -u scoutslens -n 10 --no-pager"),
        ("Nginx 访问日志", "tail -n 10 /var/log/nginx/access.log"),
        ("Nginx 错误日志", "tail -n 10 /var/log/nginx/error.log"),
    ]

    all_ok = True
    for desc, cmd in checks:
        print(f"\n{'='*60}")
        print(f"{desc}")
        print(f"{'='*60}")
        exit_status, stdout, stderr = execute_remote_command(
            hostname, username, password, cmd, port
        )

        if exit_status == 0:
            if stdout:
                print(stdout)
        else:
            print(f"✗ 获取 {desc} 失败")
            if stderr:
                print(stderr)
            all_ok = False

    print("\n" + "=" * 60)
    if all_ok:
        print("✓ 所有服务运行正常！")
    else:
        print("⚠ 部分服务可能存在问题，请检查上述输出！")
    print("=" * 60)

    return all_ok


def main():
    success = check_service_status()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
