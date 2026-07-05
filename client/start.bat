@echo off
chcp 65001 >nul
cd /d %~dp0

echo ========================================
echo  企业知识库 RAG 前端 - 启动脚本
echo ========================================
echo.

where node >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

if not exist node_modules (
    echo 未检测到 node_modules，正在安装依赖...
    call npm install
    if errorlevel 1 (
        echo 依赖安装失败
        pause
        exit /b 1
    )
)

echo 检查 5173 端口占用...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo 关闭占用 5173 端口的进程 PID=%%a
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo 启动开发服务: http://localhost:5173
echo 请确保后端已在 server 目录运行 python run.py
echo.
call npm run dev

pause
