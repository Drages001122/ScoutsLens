import os
import subprocess
import sys


def run_command(command, description):
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {command}")
    print("=" * 60)

    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True, encoding='utf-8'
        )
        print(result.stdout)
        if result.stderr:
            print("警告:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False


def build_frontend():
    print("\n" + "=" * 60)
    print("开始构建前端")
    print("=" * 60)

    frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")

    if not os.path.exists(frontend_dir):
        print(f"✗ 前端目录不存在: {frontend_dir}")
        return False

    os.chdir(frontend_dir)

    commands = [("npm install", "安装前端依赖"), ("npm run build", "构建前端")]

    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False

    print("\n✓ 前端构建完成")
    return True


def build_backend():
    print("\n" + "=" * 60)
    print("检查后端依赖")
    print("=" * 60)

    backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")

    if not os.path.exists(backend_dir):
        print(f"✗ 后端目录不存在: {backend_dir}")
        return False

    requirements_file = os.path.join(backend_dir, "requirements.txt")

    if not os.path.exists(requirements_file):
        print(f"✗ requirements.txt 不存在: {requirements_file}")
        return False

    print(f"✓ 后端依赖文件存在: {requirements_file}")
    return True


def main():
    print("=" * 60)
    print("ScoutsLens 项目构建脚本")
    print("=" * 60)

    success = True

    if not build_frontend():
        success = False

    if not build_backend():
        success = False

    print("\n" + "=" * 60)
    if success:
        print("✓ 构建成功完成！")
    else:
        print("✗ 构建失败！")
    print("=" * 60)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
