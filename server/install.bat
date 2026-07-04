@echo off
chcp 65001 >nul
cd /d %~dp0

echo ========================================
echo  企业知识库 RAG 后端 - 依赖安装脚本
echo ========================================
echo.
echo [说明] 当前 weixin 环境为 Python 3.14，多数依赖无预编译包，会编译失败。
echo        本脚本将创建 Python 3.11 的 conda 环境: rag-kb
echo.

where conda >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 conda，请先安装 Anaconda 并加入 PATH
    pause
    exit /b 1
)

conda env list | findstr /C:"rag-kb" >nul 2>&1
if errorlevel 1 (
    echo 正在创建 conda 环境 rag-kb ^(Python 3.11^)...
    conda create -n rag-kb python=3.11 -y
    if errorlevel 1 (
        echo 创建环境失败
        pause
        exit /b 1
    )
) else (
    echo 环境 rag-kb 已存在，跳过创建
)

echo.
echo 正在安装依赖...
call conda activate rag-kb
python -m pip install --upgrade pip
python -m pip install "numpy>=1.24.0,<2.0.0" --only-binary=:all:
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo 安装失败，请检查上方错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo  安装成功！
echo  激活环境: conda activate rag-kb
echo  启动服务: python run.py
echo ========================================
pause
