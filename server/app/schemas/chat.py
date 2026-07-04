"""Pydantic 请求/响应模型 - 问答模块。"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    """创建会话请求体。"""

    title: str = Field(default="新对话", description="会话标题")


class SessionResponse(BaseModel):
    """会话信息响应体。"""

    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    """消息信息响应体。"""

    id: int
    session_id: int
    role: str
    content: str
    sources: Optional[Any] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AskRequest(BaseModel):
    """问答请求体。"""

    session_id: int = Field(..., description="会话ID")
    question: str = Field(..., min_length=1, description="用户问题")


class AskResponse(BaseModel):
    """问答响应体。"""

    answer: str
    sources: List[Dict[str, Any]] = []
    message_id: int
