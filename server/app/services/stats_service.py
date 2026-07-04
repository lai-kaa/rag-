"""统计数据业务逻辑服务。"""

from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.chat import ChatMessage, ChatSession
from app.models.document import Document
from app.models.user import User


class StatsService:
    """统计服务类，提供管理后台数据统计。"""

    @staticmethod
    def get_overview(db: Session) -> dict:
        """获取统计概览数据。

        Returns:
            包含用户数、文档数、会话数、今日问答数的字典
        """
        user_count = db.query(User).filter(User.status == 1).count()
        document_count = db.query(Document).filter(Document.status == 1).count()
        session_count = db.query(ChatSession).count()

        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_message_count = (
            db.query(ChatMessage)
            .filter(ChatMessage.role == "user", ChatMessage.created_at >= today_start)
            .count()
        )

        return {
            "user_count": user_count,
            "document_count": document_count,
            "session_count": session_count,
            "today_message_count": today_message_count,
        }

    @staticmethod
    def get_trend(db: Session, days: int = 7) -> dict:
        """获取近 N 天的问答趋势和文档类型分布。

        Args:
            db: 数据库会话
            days: 统计天数，默认 7 天

        Returns:
            包含 daily_messages 和 doc_types 的字典
        """
        daily_messages = []
        for i in range(days - 1, -1, -1):
            day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
            next_day = day + timedelta(days=1)
            count = (
                db.query(ChatMessage)
                .filter(
                    ChatMessage.role == "user",
                    ChatMessage.created_at >= day,
                    ChatMessage.created_at < next_day,
                )
                .count()
            )
            daily_messages.append({"date": day.strftime("%m-%d"), "count": count})

        doc_type_rows = (
            db.query(Document.file_type, func.count(Document.id))
            .filter(Document.status == 1)
            .group_by(Document.file_type)
            .all()
        )
        doc_types = [{"type": row[0].upper(), "count": row[1]} for row in doc_type_rows]

        return {"daily_messages": daily_messages, "doc_types": doc_types}
