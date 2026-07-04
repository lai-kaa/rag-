"""认证业务逻辑服务。"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserCreate, UserUpdate
from app.utils.jwt_utils import create_access_token
from app.utils.security import md5_hash, verify_password


class AuthService:
    """认证服务类，处理登录与用户管理业务。"""

    @staticmethod
    def login(db: Session, username: str, password: str) -> Optional[dict]:
        """用户登录，验证账号密码并生成 JWT。

        Args:
            db: 数据库会话
            username: 用户名
            password: 明文密码

        Returns:
            包含 token 和用户信息的字典，失败返回 None
        """
        user = db.query(User).filter(User.username == username, User.status == 1).first()
        if user is None or not verify_password(password, user.password):
            return None

        token = create_access_token({"user_id": user.id, "role": user.role})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
        }

    @staticmethod
    def create_user(db: Session, data: UserCreate) -> User:
        """创建新用户。

        Args:
            db: 数据库会话
            data: 用户创建数据

        Returns:
            新创建的用户对象
        """
        user = User(
            username=data.username,
            password=md5_hash(data.password),
            role=data.role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, data: UserUpdate) -> Optional[User]:
        """更新用户信息。

        Args:
            db: 数据库会话
            user_id: 用户ID
            data: 更新数据

        Returns:
            更新后的用户对象，不存在返回 None
        """
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return None

        if data.password is not None:
            user.password = md5_hash(data.password)
        if data.role is not None:
            user.role = data.role
        if data.status is not None:
            user.status = data.status

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """删除用户（软删除，设置 status=0）。

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            是否删除成功
        """
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return False
        user.status = 0
        db.commit()
        return True

    @staticmethod
    def list_users(db: Session) -> List[User]:
        """获取所有启用用户列表。"""
        return db.query(User).filter(User.status == 1).order_by(User.id).all()
