"""初始化测试用户数据（数据库为空时执行）。"""

import os
import sys

SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SERVER_DIR)
sys.path.insert(0, SERVER_DIR)

from app.database import SessionLocal
from app.models.user import User
from app.utils.security import md5_hash

# 测试账号：密码均为 123456
TEST_USERS = [
    ("admin", "admin"),
    ("user1", "user"),
    ("user2", "user"),
]

PASSWORD_MD5 = md5_hash("123456")


def main():
    """向 users 表写入测试用户。"""
    db = SessionLocal()
    try:
        count = db.query(User).count()
        if count > 0:
            print(f"users 表已有 {count} 条数据，跳过初始化")
            return

        for username, role in TEST_USERS:
            db.add(User(username=username, password=PASSWORD_MD5, role=role, status=1))
        db.commit()
        print("测试用户初始化成功：")
        for username, role in TEST_USERS:
            print(f"  - {username} / 123456 ({role})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
