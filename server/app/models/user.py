"""用户 ORM 模型。"""

from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    """用户表模型，存储用户账号与角色信息。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(64), nullable=False, comment="密码(MD5)")
    role: Mapped[str] = mapped_column(Enum("admin", "user"), default="user", nullable=False, comment="角色")
    status: Mapped[int] = mapped_column(Integer, default=1, nullable=False, comment="状态: 1-启用, 0-禁用")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )
