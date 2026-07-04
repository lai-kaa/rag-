"""Pydantic 请求/响应模型 - 认证模块。"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求体。"""

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """登录成功返回的令牌信息。"""

    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str


class UserCreate(BaseModel):
    """创建用户请求体。"""

    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, description="密码")
    role: str = Field(default="user", description="角色: admin/user")


class UserUpdate(BaseModel):
    """更新用户请求体。"""

    password: Optional[str] = Field(None, min_length=6, description="新密码")
    role: Optional[str] = Field(None, description="角色")
    status: Optional[int] = Field(None, description="状态: 1-启用, 0-禁用")


class UserResponse(BaseModel):
    """用户信息响应体。"""

    id: int
    username: str
    role: str
    status: int
    created_at: datetime

    model_config = {"from_attributes": True}
