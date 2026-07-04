"""问答会话 ORM 模型。"""

from __future__ import annotations

from datetime import datetime

from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ChatSession(Base):
    """问答会话表模型，一个用户可有多个会话。"""

    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="会话ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), comment="用户ID")
    title: Mapped[str] = mapped_column(String(200), default="新对话", comment="会话标题")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    """对话消息表模型，存储用户与助手的对话内容。"""

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="消息ID")
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_sessions.id"), comment="会话ID")
    role: Mapped[str] = mapped_column(String(20), nullable=False, comment="角色: user/assistant")
    content: Mapped[str] = mapped_column(String(65535), nullable=False, comment="消息内容")
    sources: Mapped[Optional[str]] = mapped_column(String(65535), nullable=True, comment="引用来源JSON")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
