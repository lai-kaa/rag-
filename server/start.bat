@echo off
chcp 65001 >nul
cd /d %~dp0

REM 优先使用 rag-kb 环境（Python 3.11），避免 weixin 环境（Python 3.14）编译失败
set PYTHON_EXE=python
if exist "D:\anaconda\envs\rag-kb\python.exe" (
    set PYTHON_EXE=D:\anaconda\envs\rag-kb\python.exe
)

echo 使用解释器: %PYTHON_EXE%
echo 正在启动后端服务...
%PYTHON_EXE% run.py
pause
