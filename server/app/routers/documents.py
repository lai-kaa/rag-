"""知识库文档管理 API 路由（管理员专用）。"""

import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.rag_service import get_rag_service
from app.utils.deps import require_admin
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/documents", tags=["文档管理"])

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}


@router.get("", response_model=List[DocumentResponse], summary="获取文档列表")
def list_documents(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """获取所有正常状态的文档列表（管理员）。"""
    return db.query(Document).filter(Document.status == 1).order_by(Document.id.desc()).all()


@router.post("", response_model=DocumentUploadResponse, summary="上传文档")
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """上传文档并进行向量化入库（管理员）。"""
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型，仅支持: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    save_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(settings.UPLOAD_DIR, save_name)

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    doc_title = title or file.filename or save_name
    document = Document(
        title=doc_title,
        file_name=file.filename or save_name,
        file_path=save_path,
        file_type=ext,
        file_size=len(content),
        upload_user_id=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        chunk_count = get_rag_service().ingest_document(save_path, document.id, doc_title)
        document.chunk_count = chunk_count
        db.commit()
    except Exception as e:
        logger.error("文档向量化失败: %s", e)
        document.status = 0
        db.commit()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"文档向量化失败: {e}")

    logger.info("文档上传成功: id=%s, title=%s", document.id, doc_title)
    return DocumentUploadResponse(id=document.id, title=doc_title, chunk_count=document.chunk_count)


@router.delete("/{doc_id}", summary="删除文档")
def delete_document(doc_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """删除文档及其向量数据（管理员）。"""
    document = db.query(Document).filter(Document.id == doc_id, Document.status == 1).first()
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    get_rag_service().delete_document_vectors(doc_id)

    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    document.status = 0
    db.commit()
    logger.info("文档已删除: id=%s", doc_id)
    return {"message": "文档已删除"}
