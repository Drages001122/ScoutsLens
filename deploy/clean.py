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


def identify_corrupted_files(hostname, username, password, port, remote_dir):
    print(f"\n正在扫描目录: {remote_dir}")
    print("=" * 60)

    exit_status, stdout, stderr = execute_remote_command(
        hostname, username, password, f"find {remote_dir} -type f -name '*\\*'", port
    )

    corrupted_files = []
    if exit_status == 0 and stdout:
        corrupted_files = [
            line.strip() for line in stdout.strip().split("\n") if line.strip()
        ]

    exit_status, stdout, stderr = execute_remote_command(
        hostname, username, password, f"find {remote_dir} -type f -name '*/*'", port
    )

    if exit_status == 0 and stdout:
        for line in stdout.strip().split("\n"):
            line = line.strip()
            if line and line not in corrupted_files:
                corrupted_files.append(line)

    exit_status, stdout, stderr = execute_remote_command(
        hostname,
        username,
        password,
        f"find {remote_dir} -type f -name '*.tmp' -o -name '*.temp' -o -name '*.bak'",
        port,
    )

    if exit_status == 0 and stdout:
        for line in stdout.strip().split("\n"):
            line = line.strip()
            if line and line not in corrupted_files:
                corrupted_files.append(line)

    exit_status, stdout, stderr = execute_remote_command(
        hostname,
        username,
        password,
        f"find {remote_dir} -type f -name '*.tar.gz'",
        port,
    )

    if exit_status == 0 and stdout:
        for line in stdout.strip().split("\n"):
            line = line.strip()
            if line and "/tmp/" in line:
                if line not in corrupted_files:
                    corrupted_files.append(line)

    return corrupted_files


def identify_empty_dirs(hostname, username, password, port, remote_dir):
    print(f"\n正在扫描空目录: {remote_dir}")
    print("=" * 60)

    exit_status, stdout, stderr = execute_remote_command(
        hostname, username, password, f"find {remote_dir} -type d -empty", port
    )

    empty_dirs = []
    if exit_status == 0 and stdout:
        empty_dirs = [
            line.strip() for line in stdout.strip().split("\n") if line.strip()
        ]

    return empty_dirs


def backup_before_cleanup(hostname, username, password, port, remote_project_dir):
    print("\n" + "=" * 60)
    print("创建备份")
    print("=" * 60)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"/tmp/scoutslens_cleanup_backup_{timestamp}"

    exit_status, _, _ = execute_remote_command(
        hostname, username, password, f"mkdir -p {backup_dir}", port
    )

    if exit_status != 0:
        print("✗ 创建备份目录失败")
        return None

    print("正在备份数据库...")
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
        print("⚠ 数据库备份失败")

    print(f"✓ 备份目录: {backup_dir}")
    return backup_dir


def clean_corrupted_files(hostname, username, password, port, corrupted_files):
    if not corrupted_files:
        print("\n✓ 没有发现损坏的文件")
        return True

    print(f"\n发现 {len(corrupted_files)} 个损坏/残余文件:")
    print("=" * 60)
    for i, file in enumerate(corrupted_files[:20], 1):
        print(f"{i}. {file}")
    if len(corrupted_files) > 20:
        print(f"... 还有 {len(corrupted_files) - 20} 个文件")

    print("\n是否删除这些文件? (y/n): ", end="")
    confirm = input().strip().lower()

    if confirm != "y":
        print("取消删除操作")
        return False

    print("\n正在删除损坏的文件...")
    deleted_count = 0
    failed_count = 0

    for file in corrupted_files:
        exit_status, _, _ = execute_remote_command(
            hostname, username, password, f"rm -f '{file}'", port
        )
        if exit_status == 0:
            deleted_count += 1
        else:
            failed_count += 1

    print(f"✓ 删除完成: 成功 {deleted_count} 个, 失败 {failed_count} 个")
    return True


def clean_empty_dirs(hostname, username, password, port, empty_dirs):
    if not empty_dirs:
        print("\n✓ 没有发现空目录")
        return True

    print(f"\n发现 {len(empty_dirs)} 个空目录:")
    print("=" * 60)
    for i, dir in enumerate(empty_dirs[:20], 1):
        print(f"{i}. {dir}")
    if len(empty_dirs) > 20:
        print(f"... 还有 {len(empty_dirs) - 20} 个目录")

    print("\n是否删除这些空目录? (y/n): ", end="")
    confirm = input().strip().lower()

    if confirm != "y":
        print("取消删除操作")
        return False

    print("\n正在删除空目录...")
    deleted_count = 0
    failed_count = 0

    for dir in sorted(empty_dirs, reverse=True):
        exit_status, _, _ = execute_remote_command(
            hostname, username, password, f"rmdir '{dir}' 2>/dev/null", port
        )
        if exit_status == 0:
            deleted_count += 1
        else:
            failed_count += 1

    print(f"✓ 删除完成: 成功 {deleted_count} 个, 失败 {failed_count} 个")
    return True


def full_cleanup_and_redeploy(hostname, username, password, port, remote_project_dir):
    print("\n" + "=" * 60)
    print("完全清理并重新部署")
    print("=" * 60)
    print("⚠ 警告: 此操作将删除 /var/www/ 目录下的所有内容!")
    print("=" * 60)

    print("\n请确认以下信息:")
    print(f"服务器: {hostname}")
    print("清理目录: /var/www/")
    print(f"项目目录: {remote_project_dir}")
    print("\n此操作将:")
    print("1. 备份数据库")
    print("2. 停止服务")
    print("3. 删除整个 /var/www/ 目录")
    print("4. 重新创建目录结构")
    print("5. 需要手动重新部署代码")

    print("\n是否继续? (输入 'yes' 确认): ", end="")
    confirm = input().strip()

    if confirm != "yes":
        print("取消操作")
        return False

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


def verify_cleanup(hostname, username, password, port, remote_project_dir):
    print("\n" + "=" * 60)
    print("验证清理结果")
    print("=" * 60)

    checks = []

    exit_status, stdout, stderr = execute_remote_command(
        hostname,
        username,
        password,
        "find /var/www/ -type f -name '*\\*' -o -name '*/*'",
        port,
    )
    if exit_status == 0 and not stdout.strip():
        checks.append(("损坏文件检查", "通过", "未发现损坏文件"))
    else:
        checks.append(("损坏文件检查", "失败", f"仍有损坏文件: {stdout.strip()[:100]}"))

    exit_status, stdout, stderr = execute_remote_command(
        hostname,
        username,
        password,
        f"test -f {remote_project_dir}/database/scoutslens.db && echo 'exists'",
        port,
    )
    if exit_status == 0 and "exists" in stdout:
        checks.append(("数据库文件", "通过", "数据库文件存在"))
    else:
        checks.append(("数据库文件", "警告", "数据库文件不存在（可能需要重新部署）"))

    exit_status, stdout, stderr = execute_remote_command(
        hostname,
        username,
        password,
        f"test -d {remote_project_dir}/backend && echo 'exists'",
        port,
    )
    if exit_status == 0 and "exists" in stdout:
        checks.append(("后端目录", "通过", "后端目录存在"))
    else:
        checks.append(("后端目录", "警告", "后端目录不存在（可能需要重新部署）"))

    exit_status, stdout, stderr = execute_remote_command(
        hostname,
        username,
        password,
        f"test -d {remote_project_dir}/frontend/dist && echo 'exists'",
        port,
    )
    if exit_status == 0 and "exists" in stdout:
        checks.append(("前端目录", "通过", "前端目录存在"))
    else:
        checks.append(("前端目录", "警告", "前端目录不存在（可能需要重新部署）"))

    for check_name, status, message in checks:
        status_symbol = "✓" if status == "通过" else ("⚠" if status == "警告" else "✗")
        print(f"{status_symbol} {check_name}: {status} - {message}")

    all_passed = all(status in ["通过", "警告"] for _, status, _ in checks)
    return all_passed


def main():
    print("=" * 60)
    print("ScoutsLens 远程服务器清理工具")
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
    print(f"项目目录: {remote_project_dir}")
    print("清理范围: /var/www/")

    print("\n请选择清理模式:")
    print("1. 识别并清理损坏/残余文件")
    print("2. 完全清理并重新部署")
    print("3. 仅扫描（不删除）")

    choice = input("\n请输入选项 (1/2/3): ").strip()

    success = True

    if choice == "1":
        print("\n开始识别并清理损坏/残余文件...")

        corrupted_files = identify_corrupted_files(
            hostname, username, password, port, "/var/www/"
        )
        empty_dirs = identify_empty_dirs(
            hostname, username, password, port, "/var/www/"
        )

        if not clean_corrupted_files(
            hostname, username, password, port, corrupted_files
        ):
            success = False

        if not clean_empty_dirs(hostname, username, password, port, empty_dirs):
            success = False

        if success:
            verify_cleanup(hostname, username, password, port, remote_project_dir)

    elif choice == "2":
        success = full_cleanup_and_redeploy(
            hostname, username, password, port, remote_project_dir
        )

    elif choice == "3":
        print("\n开始扫描...")
        corrupted_files = identify_corrupted_files(
            hostname, username, password, port, "/var/www/"
        )
        empty_dirs = identify_empty_dirs(
            hostname, username, password, port, "/var/www/"
        )

        print("\n扫描完成:")
        print(f"损坏/残余文件: {len(corrupted_files)} 个")
        print(f"空目录: {len(empty_dirs)} 个")

    else:
        print("✗ 无效的选项")
        success = False

    print("\n" + "=" * 60)
    if success:
        print("✓ 操作完成！")
    else:
        print("✗ 操作失败或被取消！")
    print("=" * 60)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
