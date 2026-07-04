"""Pydantic 请求/响应模型 - 文档模块。"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """文档信息响应体。"""

    id: int
    title: str
    file_name: str
    file_type: str
    file_size: int
    chunk_count: int
    upload_user_id: int
    status: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    """文档上传成功响应体。"""

    id: int
    title: str
    chunk_count: int
    message: str = "文档上传并向量化成功"
