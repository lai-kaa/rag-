"""应用配置模块，从环境变量读取配置项。"""

import os
from pathlib import Path

from dotenv import load_dotenv

# 加载 .env 文件
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    """全局配置类，集中管理所有配置项。"""

    # MySQL 数据库配置
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "1234")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "db")

    @property
    def DATABASE_URL(self) -> str:
        """构建 SQLAlchemy 数据库连接 URL。"""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"
        )

    # 模型提供方: ollama=本地Ollama | deepseek=DeepSeek API
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "deepseek")

    # Ollama 本地大模型配置（LLM_PROVIDER=ollama 时使用）
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen3:8b")
    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "qwen3-embedding:4b")

    # DeepSeek API 配置（LLM_PROVIDER=deepseek 时使用）
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    DEEPSEEK_TEMPERATURE: float = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.3"))
    DEEPSEEK_MAX_TOKENS: int = int(os.getenv("DEEPSEEK_MAX_TOKENS", "4096"))

    # 远程 Embedding API（LLM_PROVIDER=deepseek 时使用，无需本地模型）
    # DeepSeek 无 Embedding 接口，需配置 OpenAI 兼容的 Embedding 服务（如 SiliconFlow）
    EMBED_API_KEY: str = os.getenv("EMBED_API_KEY", "")
    EMBED_API_BASE_URL: str = os.getenv("EMBED_API_BASE_URL", "https://api.siliconflow.cn/v1")
    EMBED_API_MODEL: str = os.getenv("EMBED_API_MODEL", "BAAI/bge-m3")

    # RAG 检索与切片配置
    RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "300"))
    RAG_CHUNK_OVERLAP: int = int(os.getenv("RAG_CHUNK_OVERLAP", "120"))
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "6"))
    RAG_HISTORY_TURNS: int = int(os.getenv("RAG_HISTORY_TURNS", "5"))

    # Chroma 向量库持久化目录
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", str(BASE_DIR / "chroma_data"))

    # 文件上传目录
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))

    # 日志目录
    LOG_DIR: str = os.getenv("LOG_DIR", str(BASE_DIR / "logs"))

    # JWT 认证配置
    JWT_SECRET: str = os.getenv("JWT_SECRET", "rag-knowledge-base-secret-key-2026")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "72"))


settings = Settings()
