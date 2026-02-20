import json
import os
import sys

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


def stop_service():
    config = load_config()
    if not config:
        print("✗ 加载配置文件失败")
        return False

    hostname = config.get("hostname")
    username = config.get("username")
    password = config.get("password")
    port = config.get("port", 22)

    if not all([hostname, username, password]):
        print("✗ 配置文件缺少必要信息")
        return False

    print("=" * 60)
    print("停止 ScoutsLens 服务")
    print("=" * 60)
    print(f"服务器: {hostname}")

    commands = [
        ("停止应用服务", "systemctl stop scoutslens"),
        ("停止 Nginx", "systemctl stop nginx"),
        ("检查应用服务状态", "systemctl status scoutslens"),
        ("检查 Nginx 状态", "systemctl status nginx"),
    ]

    all_success = True
    for desc, cmd in commands:
        print(f"\n{desc}...")
        exit_status, stdout, stderr = execute_remote_command(
            hostname, username, password, cmd, port
        )

        if exit_status == 0 or "inactive" in stdout:
            print(f"✓ {desc} 成功")
            if stdout:
                print(stdout[:200])
        else:
            print(f"✗ {desc} 失败")
            if stderr:
                print(stderr)
            all_success = False

    print("\n" + "=" * 60)
    if all_success:
        print("✓ 服务停止成功！")
    else:
        print("✗ 部分服务停止失败！")
    print("=" * 60)

    return all_success


def main():
    success = stop_service()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
