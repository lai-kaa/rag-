"""统计数据 API 路由（管理员专用）。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.stats import StatsOverview, StatsTrend
from app.services.stats_service import StatsService
from app.utils.deps import require_admin

router = APIRouter(prefix="/api/stats", tags=["统计"])


@router.get("/overview", response_model=StatsOverview, summary="统计概览")
def get_overview(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """获取管理后台统计概览数据。"""
    return StatsService.get_overview(db)


@router.get("/trend", response_model=StatsTrend, summary="统计趋势")
def get_trend(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """获取近 7 天问答趋势和文档类型分布。"""
    return StatsService.get_trend(db)
