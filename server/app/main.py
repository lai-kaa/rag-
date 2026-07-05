"""FastAPI 应用入口模块。"""
import sys
from pathlib import Path
# 将server文件夹加入Python搜索路径
sys.path.append(str(Path(__file__).parent.parent))
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, chat, documents, stats, users
from app.utils.logger import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理。"""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    logger.info("企业知识库 RAG 问答系统启动成功")
    yield
    logger.info("企业知识库 RAG 问答系统已关闭")




app = FastAPI(
    title="企业知识库 RAG 问答系统",
    description="基于 LangChain + Ollama + Chroma 的企业内部知识库问答 Agent",
    version="1.0.0",
    lifespan=lifespan,
)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://laika1.pages.dev"
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(stats.router)


@app.get("/", summary="健康检查")
def root():
    """服务健康检查接口。"""
    return {"message": "企业知识库 RAG 问答系统运行中", "version": "1.0.0"}


if __name__ == "__main__":
    # 支持直接运行 main.py（需使用 python 解释器，不要用 conda.exe）
    import sys
    from pathlib import Path

    server_dir = str(Path(__file__).resolve().parent.parent)
    os.chdir(server_dir)
    if server_dir not in sys.path:
        sys.path.insert(0, server_dir)

    import uvicorn

    print("正在启动企业知识库 RAG 后端服务...")
    print("工作目录:", server_dir)
    print("访问地址: http://127.0.0.1:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
