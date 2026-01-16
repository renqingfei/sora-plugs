@echo off
chcp 65001 >nul
echo 正在启动 Sora-2 视频生成插件...
echo.

cd /d "%~dp0"

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

REM 检查依赖
if not exist "venv" (
    echo [信息] 首次运行，正在创建虚拟环境...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [信息] 正在安装依赖...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
) else (
    call venv\Scripts\activate.bat
)

echo.
echo [信息] 插件启动中，端口: 13005
echo [信息] 按 Ctrl+C 停止服务
echo.

python main.py

pause
