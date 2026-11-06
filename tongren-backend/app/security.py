"""
鉴权：token 签发 / 校验（HMAC-SHA256，无状态）+ 密码哈希（PBKDF2）
"""
import base64
import hashlib
import hmac
import os
import time

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .errors import ApiError
from .models import User

PBKDF2_ITERATIONS = 120000


# ---------------------------------------------------------------- 密码

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return "pbkdf2${}${}${}".format(
        PBKDF2_ITERATIONS,
        salt.hex(),
        digest.hex(),
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iterations, salt_hex, digest_hex = stored.split("$")
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, AttributeError):
        return False


# ---------------------------------------------------------------- token

def _sign(payload: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256
    ).hexdigest()[:32]


def make_token(user_id: int) -> str:
    exp = int(time.time()) + settings.TOKEN_EXPIRE_DAYS * 86400
    payload = f"{user_id}.{exp}"
    raw = f"{payload}.{_sign(payload)}"
    return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("ascii")


def parse_token(token: str) -> int:
    """校验 token，返回 user_id；无效抛 ApiError(40101)"""
    try:
        raw = base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8")
        uid_str, exp_str, sign = raw.split(".")
        if not hmac.compare_digest(sign, _sign(f"{uid_str}.{exp_str}")):
            raise ValueError("bad signature")
        if int(exp_str) < time.time():
            raise ValueError("expired")
        return int(uid_str)
    except ApiError:
        raise
    except Exception:
        raise ApiError(40101, "登录已失效，请重新登录")


# ---------------------------------------------------------------- 依赖

def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    """要求登录的接口使用：Authorization: Bearer <token>"""
    if not authorization.startswith("Bearer "):
        raise ApiError(40101, "未登录")
    user_id = parse_token(authorization[7:].strip())
    user = db.get(User, user_id)
    if user is None:
        raise ApiError(40101, "用户不存在，请重新登录")
    return user


def get_optional_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User | None:
    """可选登录：token 缺失/失效时返回 None（游客）"""
    if not authorization.startswith("Bearer "):
        return None
    try:
        user_id = parse_token(authorization[7:].strip())
        return db.get(User, user_id)
    except ApiError:
        return None
