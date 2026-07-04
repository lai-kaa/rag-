"""密码加密工具模块。"""

import hashlib


def md5_hash(text: str) -> str:
    """对字符串进行 MD5 加密。

    Args:
        text: 待加密的明文

    Returns:
        32 位 MD5 十六进制字符串
    """
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配。

    Args:
        plain_password: 明文密码
        hashed_password: 数据库中存储的 MD5 密码

    Returns:
        密码是否匹配
    """
    return md5_hash(plain_password) == hashed_password
