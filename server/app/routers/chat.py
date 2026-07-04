"""问答会话与 RAG 问答 API 路由。"""

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.chat import ChatMessage, ChatSession
from app.models.user import User
from app.schemas.chat import AskRequest, AskResponse, MessageResponse, SessionCreate, SessionResponse
from app.services.rag_service import get_rag_service
from app.utils.deps import get_current_user
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/chat", tags=["问答"])


@router.get("/sessions", response_model=List[SessionResponse], summary="获取会话列表")
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取当前用户的所有问答会话。"""
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )


@router.post("/sessions", response_model=SessionResponse, summary="创建会话")
def create_session(
    data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建新的问答会话。"""
    session = ChatSession(user_id=current_user.id, title=data.title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.delete("/sessions/{session_id}", summary="删除会话")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除指定会话及其所有消息。"""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
    db.delete(session)
    db.commit()
    return {"message": "会话已删除"}


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse], summary="获取会话消息")
def get_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取指定会话的所有消息记录。"""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.id).all()
    result = []
    for msg in messages:
        sources = json.loads(msg.sources) if msg.sources else None
        result.append(MessageResponse(
            id=msg.id,
            session_id=msg.session_id,
            role=msg.role,
            content=msg.content,
            sources=sources,
            created_at=msg.created_at,
        ))
    return result


@router.post("/ask", response_model=AskResponse, summary="知识库问答")
def ask(data: AskRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """向知识库提问并获取 RAG 增强回答。"""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == data.session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    # 先读取近期对话历史（不含本次提问），用于多轮语境与检索增强
    history_limit = settings.RAG_HISTORY_TURNS * 2
    recent_msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.id.desc())
        .limit(history_limit)
        .all()
    )
    recent_msgs.reverse()
    chat_history = [{"role": m.role, "content": m.content} for m in recent_msgs]

    is_first_msg = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).count() == 0

    # 保存用户消息
    user_msg = ChatMessage(session_id=session.id, role="user", content=data.question)
    db.add(user_msg)

    if is_first_msg:
        session.title = data.question[:30]

    # RAG 检索问答（传入对话历史）
    try:
        result = get_rag_service().query(data.question, chat_history=chat_history)
    except Exception as e:
        logger.error("RAG 问答失败: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"问答服务异常: {e}")

    # 保存助手回复
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=result["answer"],
        sources=json.dumps(result["sources"], ensure_ascii=False) if result["sources"] else None,
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    logger.info("问答完成: session=%s, user=%s", session.id, current_user.username)
    return AskResponse(answer=result["answer"], sources=result["sources"], message_id=assistant_msg.id)
