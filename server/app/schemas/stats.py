"""Pydantic 请求/响应模型 - 统计模块。"""

from typing import List

from pydantic import BaseModel


class StatsOverview(BaseModel):
    """统计概览响应体。"""

    user_count: int
    document_count: int
    session_count: int
    today_message_count: int


class TrendItem(BaseModel):
    """趋势数据项。"""

    date: str
    count: int


class DocTypeItem(BaseModel):
    """文档类型分布项。"""

    type: str
    count: int


class StatsTrend(BaseModel):
    """统计趋势响应体。"""

    daily_messages: List[TrendItem]
    doc_types: List[DocTypeItem]
