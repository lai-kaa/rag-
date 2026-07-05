"""FastAPI 应用入口模块。"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import check_database_connection
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

    if check_database_connection():
        logger.info("数据库连接正常")
    else:
        logger.error("数据库连接失败，请检查 MYSQL_* 环境变量及云端白名单")

    logger.info("企业知识库 RAG 问答系统启动成功")
    yield
    logger.info("企业知识库 RAG 问答系统已关闭")


app = FastAPI(
    title="企业知识库 RAG 问答系统",
    description="基于 LangChain + Chroma 的企业内部知识库问答 Agent",
    version="1.0.0",
    lifespan=lifespan,
)

# 跨域配置（allow_credentials=True 时不能使用 allow_origins=["*"]）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """数据库异常统一返回 JSON，确保 CORS 头正常附加。"""
    logger.error("数据库异常: %s %s", request.url.path, exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "数据库连接失败，请检查云端数据库配置与白名单"},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """未捕获异常统一返回 JSON，避免 500 裸响应导致浏览器 CORS 误报。"""
    logger.exception("未处理异常: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试"},
    )


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(stats.router)


@app.get("/", summary="健康检查")
def root():
    """服务健康检查接口。"""
    db_ok = check_database_connection()
    vector_count = None
    try:
        from app.services.rag_service import get_rag_service
        vector_count = get_rag_service().vectorstore._collection.count()
    except Exception:
        pass
    return {
        "message": "企业知识库 RAG 问答系统运行中",
        "version": "1.0.0",
        "database": "ok" if db_ok else "error",
        "vector_count": vector_count,
    }


if __name__ == "__main__":
    server_dir = str(Path(__file__).resolve().parent.parent)
    os.chdir(server_dir)
    if server_dir not in sys.path:
        sys.path.insert(0, server_dir)

    import uvicorn

    print("正在启动企业知识库 RAG 后端服务...")
    print("工作目录:", server_dir)
    print("访问地址: http://127.0.0.1:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
