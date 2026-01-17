@echo off
chcp 65001 >nul
echo ========================================
echo   Sora-2 插件打包脚本
echo ========================================
echo.

cd /d "%~dp0"

REM 检查 Python 环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo [信息] 正在执行打包...
echo.

python build.py

echo.
echo [完成] 打包流程结束
pause
