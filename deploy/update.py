import json
import os
import sys
import tarfile
import tempfile

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


def update_frontend():
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
    print("更新前端文件")
    print("=" * 60)
    print(f"服务器: {hostname}")

    local_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
    remote_dist = f"{remote_project_dir}/frontend/dist"

    if not os.path.exists(local_dist):
        print(f"✗ 本地前端构建目录不存在: {local_dist}")
        print("请先运行: python deploy/build.py")
        return False

    print("\n正在上传前端文件...")
    print(f"本地路径: {local_dist}")
    print(f"远程路径: {remote_dist}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)

    try:
        scp = SCPClient(ssh.get_transport())

        print("\n正在压缩前端文件以加快上传速度...")
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".tar.gz"
        ) as f:
            temp_archive = f.name

        print(f"创建压缩包: {os.path.basename(temp_archive)}")

        with tarfile.open(temp_archive, "w:gz") as tar:
            for root, dirs, files in os.walk(local_dist):
                for file in files:
                    local_file = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file, local_dist)
                    tar.add(local_file, arcname=relative_path)

        archive_size = os.path.getsize(temp_archive) / (1024 * 1024)
        print(f"压缩包大小: {archive_size:.2f} MB")

        print("\n正在上传压缩包到服务器...")
        scp.put(temp_archive, "/tmp/frontend_dist.tar.gz")
        print("✓ 压缩包上传完成")

        print("\n正在在服务器上解压文件...")
        exit_status, _, _ = execute_remote_command(
            hostname, username, password, f"mkdir -p {remote_dist}", port
        )
        exit_status, _, _ = execute_remote_command(
            hostname,
            username,
            password,
            f"tar -xzf /tmp/frontend_dist.tar.gz -C {remote_dist}",
            port,
        )
        execute_remote_command(
            hostname, username, password, "rm /tmp/frontend_dist.tar.gz", port
        )

        os.remove(temp_archive)
        print("✓ 前端文件解压完成")

        scp.close()
        ssh.close()

        print("\n✓ 前端更新完成！")
        return True

    except Exception as e:
        print(f"\n✗ 前端更新失败: {e}")
        return False


def update_backend():
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

    print("\n" + "=" * 60)
    print("更新后端代码")
    print("=" * 60)

    local_backend = os.path.join(os.path.dirname(__file__), "..", "backend")
    remote_backend = f"{remote_project_dir}/backend"

    if not os.path.exists(local_backend):
        print(f"✗ 本地后端目录不存在: {local_backend}")
        return False

    print("\n正在上传后端文件...")
    print(f"本地路径: {local_backend}")
    print(f"远程路径: {remote_backend}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)

    try:
        scp = SCPClient(ssh.get_transport())

        print("\n正在压缩后端文件以加快上传速度...")
        with tempfile.NamedTemporaryFile(
            mode="wb", delete=False, suffix=".tar.gz"
        ) as f:
            temp_archive = f.name

        print(f"创建压缩包: {os.path.basename(temp_archive)}")

        with tarfile.open(temp_archive, "w:gz") as tar:
            for root, dirs, files in os.walk(local_backend):
                for file in files:
                    local_file = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file, local_backend)
                    tar.add(local_file, arcname=relative_path)

        archive_size = os.path.getsize(temp_archive) / (1024 * 1024)
        print(f"压缩包大小: {archive_size:.2f} MB")

        print("\n正在上传压缩包到服务器...")
        scp.put(temp_archive, "/tmp/backend_dist.tar.gz")
        print("✓ 压缩包上传完成")

        print("\n正在在服务器上解压文件...")
        exit_status, _, _ = execute_remote_command(
            hostname, username, password, f"mkdir -p {remote_backend}", port
        )
        exit_status, _, _ = execute_remote_command(
            hostname,
            username,
            password,
            f"tar -xzf /tmp/backend_dist.tar.gz -C {remote_backend}",
            port,
        )
        execute_remote_command(
            hostname, username, password, "rm /tmp/backend_dist.tar.gz", port
        )

        os.remove(temp_archive)
        print("✓ 后端文件解压完成")

        scp.close()
        ssh.close()

        print("\n✓ 后端更新完成！")

        print("\n正在检查并创建虚拟环境...")
        exit_status, stdout, stderr = execute_remote_command(
            hostname,
            username,
            password,
            f"test -d {remote_backend}/venv && echo 'exists' || echo 'not exists'",
            port,
        )

        if "not exists" in stdout:
            print("虚拟环境不存在，正在创建...")
            exit_status, _, _ = execute_remote_command(
                hostname,
                username,
                password,
                f"cd {remote_backend} && python3 -m venv venv",
                port,
            )
            if exit_status == 0:
                print("✓ 虚拟环境创建完成")
            else:
                print("✗ 虚拟环境创建失败")
                return False

        print("\n正在安装依赖...")
        exit_status, _, _ = execute_remote_command(
            hostname,
            username,
            password,
            f"cd {remote_backend} && source venv/bin/activate && pip install -r requirements.txt",
            port,
        )

        if exit_status == 0:
            print("✓ 依赖安装完成")
        else:
            print("⚠ 依赖安装可能存在问题")

        exit_status, _, _ = execute_remote_command(
            hostname, username, password, "systemctl restart scoutslens", port
        )

        if exit_status == 0:
            print("✓ 后端服务重启完成")
        else:
            print("⚠ 后端服务重启可能存在问题")

        return True

    except Exception as e:
        print(f"\n✗ 后端更新失败: {e}")
        return False


def main():
    print("=" * 60)
    print("ScoutsLens 更新脚本")
    print("=" * 60)

    print("\n请选择要更新的内容:")
    print("1. 仅更新前端")
    print("2. 仅更新后端")
    print("3. 同时更新前端和后端")

    choice = input("\n请输入选项 (1/2/3): ").strip()

    success = True

    if choice == "1":
        if not update_frontend():
            success = False
    elif choice == "2":
        if not update_backend():
            success = False
    elif choice == "3":
        if not update_frontend():
            success = False
        if not update_backend():
            success = False
    else:
        print("✗ 无效的选项")
        success = False

    print("\n" + "=" * 60)
    if success:
        print("✓ 更新完成！")
    else:
        print("✗ 更新失败！")
    print("=" * 60)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
