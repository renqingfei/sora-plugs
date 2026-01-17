# -*- coding: utf-8 -*-
"""
Sora-2 插件打包脚本
使用 PyInstaller 将 Python 项目打包成单个 exe 文件
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

# 项目配置
PROJECT_NAME = "sora2-plugin"
MAIN_SCRIPT = "sora2-plugin/main.py"
ICON_FILE = None  # 如果有图标文件，设置路径，如: "icon.ico"
OUTPUT_DIR = "dist"
BUILD_DIR = "build"

# PyInstaller 配置
PYINSTALLER_OPTIONS = [
    "--name", PROJECT_NAME,           # 指定输出文件名
    "--onefile",                       # 打包成单个文件
    "--clean",                         # 清理临时文件
    "--noconfirm",                     # 不询问确认
    "--console",                       # 显示控制台窗口（用于查看日志）

    # 隐藏导入（确保所有依赖都被打包）
    "--hidden-import", "uvicorn.logging",
    "--hidden-import", "uvicorn.loops",
    "--hidden-import", "uvicorn.loops.auto",
    "--hidden-import", "uvicorn.protocols",
    "--hidden-import", "uvicorn.protocols.http",
    "--hidden-import", "uvicorn.protocols.http.auto",
    "--hidden-import", "uvicorn.protocols.websockets",
    "--hidden-import", "uvicorn.protocols.websockets.auto",
    "--hidden-import", "uvicorn.lifespan",
    "--hidden-import", "uvicorn.lifespan.on",

    # 添加数据文件（如果有配置文件需要打包）
    # "--add-data", "config.json;.",

    # 排除不需要的模块以减小体积
    "--exclude-module", "matplotlib",
    "--exclude-module", "numpy",
    "--exclude-module", "pandas",
    "--exclude-module", "PIL",
]

# 如果有图标文件，添加图标选项
if ICON_FILE and os.path.exists(ICON_FILE):
    PYINSTALLER_OPTIONS.extend(["--icon", ICON_FILE])


def check_pyinstaller():
    """检查 PyInstaller 是否已安装"""
    try:
        subprocess.run(
            ["pyinstaller", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_pyinstaller():
    """安装 PyInstaller"""
    print("正在安装 PyInstaller...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "pyinstaller"],
        check=True
    )
    print("[OK] PyInstaller 安装完成")


def clean_build():
    """清理之前的构建文件"""
    print("\n清理构建文件...")
    for dir_name in [BUILD_DIR, OUTPUT_DIR, "__pycache__"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  已删除: {dir_name}")

    # 删除 .spec 文件
    spec_file = f"{PROJECT_NAME}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"  已删除: {spec_file}")


def build_exe():
    """执行打包"""
    print("\n开始打包...")
    print(f"主脚本: {MAIN_SCRIPT}")
    print(f"输出目录: {OUTPUT_DIR}")

    # 构建 PyInstaller 命令
    command = [sys.executable, "-m", "PyInstaller"] + PYINSTALLER_OPTIONS + [MAIN_SCRIPT]

    print(f"\n执行命令: {' '.join(command)}\n")

    # 执行打包
    result = subprocess.run(command)

    if result.returncode == 0:
        print("\n[OK] 打包成功!")
        exe_path = Path(OUTPUT_DIR) / f"{PROJECT_NAME}.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n生成文件: {exe_path}")
            print(f"文件大小: {size_mb:.2f} MB")
        return True
    else:
        print("\n[ERROR] 打包失败!")
        return False


def create_zip():
    """创建发布包"""
    print("\n创建发布包...")

    exe_path = Path(OUTPUT_DIR) / f"{PROJECT_NAME}.exe"
    if not exe_path.exists():
        print("[ERROR] 未找到 exe 文件")
        return False

    # 创建压缩包
    zip_name = f"{PROJECT_NAME}-1.0.0"
    zip_path = Path(OUTPUT_DIR) / zip_name

    # 创建临时目录
    temp_dir = Path(OUTPUT_DIR) / "temp"
    temp_dir.mkdir(exist_ok=True)

    # 复制 exe 文件
    shutil.copy(exe_path, temp_dir / f"{PROJECT_NAME}.exe")

    # 复制 README（如果存在）
    readme_path = Path("sora2-plugin") / "README.md"
    if readme_path.exists():
        shutil.copy(readme_path, temp_dir / "README.md")

    # 创建 ZIP
    shutil.make_archive(str(zip_path), 'zip', temp_dir)

    # 删除临时目录
    shutil.rmtree(temp_dir)

    print(f"[OK] 发布包已创建: {zip_path}.zip")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print(f"  Sora-2 插件打包工具")
    print("=" * 60)

    # 检查主脚本是否存在
    if not os.path.exists(MAIN_SCRIPT):
        print(f"[ERROR] 错误: 未找到主脚本 {MAIN_SCRIPT}")
        sys.exit(1)

    # 检查并安装 PyInstaller
    if not check_pyinstaller():
        print("未检测到 PyInstaller，正在安装...")
        install_pyinstaller()
    else:
        print("[OK] PyInstaller 已安装")

    # 清理旧文件
    clean_build()

    # 执行打包
    if not build_exe():
        sys.exit(1)

    # 创建发布包
    create_zip()

    print("\n" + "=" * 60)
    print("  打包完成!")
    print("=" * 60)
    print(f"\n可执行文件: dist/{PROJECT_NAME}.exe")
    print(f"发布包: dist/{PROJECT_NAME}-1.0.0.zip")
    print("\n使用方法:")
    print(f"  1. 双击运行 {PROJECT_NAME}.exe")
    print(f"  2. 服务将在 http://127.0.0.1:13005 启动")
    print(f"  3. 按 Ctrl+C 停止服务\n")


if __name__ == "__main__":
    main()
