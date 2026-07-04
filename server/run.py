"""后端服务启动脚本（推荐在 PyCharm 或命令行中运行此文件）。"""

import os
import sys

# 将 server 目录设为工作目录，保证 app 包可被正确导入
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SERVER_DIR)
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

import uvicorn

if __name__ == "__main__":
    print("正在启动企业知识库 RAG 后端服务...")
    print("工作目录:", SERVER_DIR)
    print("访问地址: http://127.0.0.1:8000")
    print("API 文档: http://127.0.0.1:8000/docs")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
