"""数据库连接与会话管理模块。"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 云端 MySQL 连接参数（阿里云 PolarDB/RDS 等建议开启 MYSQL_SSL=true）
connect_args = {}
if settings.MYSQL_SSL:
    connect_args["ssl"] = {"ssl_disabled": False}

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """获取数据库会话的依赖注入函数。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """启动时检测数据库是否可连接。"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("数据库连接失败: %s", e)
        return False
