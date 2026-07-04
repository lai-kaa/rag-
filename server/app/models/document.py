"""知识库文档 ORM 模型。"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Document(Base):
    """知识库文档表模型，记录上传的文档元信息。"""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="文档ID")
    title: Mapped[str] = mapped_column(String(200), nullable=False, comment="文档标题")
    file_name: Mapped[str] = mapped_column(String(255), nullable=False, comment="原始文件名")
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="存储路径")
    file_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="文件类型")
    file_size: Mapped[int] = mapped_column(Integer, default=0, comment="文件大小")
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, comment="向量切片数量")
    upload_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), comment="上传用户ID")
    status: Mapped[int] = mapped_column(Integer, default=1, comment="状态: 1-正常, 0-已删除")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), comment="上传时间")
