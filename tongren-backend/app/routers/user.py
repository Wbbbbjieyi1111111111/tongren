"""
用户域接口（契约 4 + 扩展登录注册）
  POST /user/login          手机号 + 密码登录
  POST /user/register       注册（成功即登录态返回）
  POST /user/log            埋点上报（单条）
  POST /user/log/batch      埋点批量上报
  GET/POST /user/favorites  收藏查询 / 收藏切换
  GET/POST /user/trips      行程查询 / 行程保存

鉴权：favorites / trips 需要 Authorization: Bearer <token>
"""
import re
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..errors import ApiError, CODE_NOT_FOUND, CODE_PARAM, CODE_UNAUTH, ok
from .. import models as m
from ..schemas import FavoriteBody, LogBatchBody, LogBody, LoginBody, RegisterBody, TripBody
from ..security import get_current_user, get_optional_user, hash_password, make_token, verify_password
from .. import serializers as sz

router = APIRouter(prefix="/user", tags=["user"])

PHONE_RE = re.compile(r"^1\d{10}$")


def _check_password(password: str) -> str:
    pwd = password or ""
    if not 6 <= len(pwd) <= 32:
        raise ApiError(CODE_PARAM, "密码长度需为 6–32 位")
    return pwd


def _check_phone(phone: str) -> str:
    phone = (phone or "").strip()
    if not PHONE_RE.match(phone):
        raise ApiError(CODE_PARAM, "请输入正确的 11 位手机号")
    return phone


def _auth_payload(user: m.User) -> dict:
    return {"token": make_token(user.id), "user": sz.user_to_json(user)}


# ---------------------------------------------------------------- 登录注册

@router.post("/login")
def login(body: LoginBody, db: Session = Depends(get_db)):
    """手机号 + 密码登录，返回 { token, user }"""
    phone = _check_phone(body.phone)
    user = db.execute(select(m.User).where(m.User.phone == phone)).scalar_one_or_none()
    if user is None or not user.password_hash or not verify_password(body.password, user.password_hash):
        raise ApiError(CODE_UNAUTH, "手机号或密码错误")
    return ok(_auth_payload(user))


@router.post("/register")
def register(body: RegisterBody, db: Session = Depends(get_db)):
    """注册（openid 写 phone:<手机号> 以满足唯一约束），成功即返回登录态"""
    phone = _check_phone(body.phone)
    password = _check_password(body.password)
    exists = db.execute(select(m.User.id).where(m.User.phone == phone)).scalar_one_or_none()
    if exists is not None:
        raise ApiError(CODE_PARAM, "该手机号已注册，请直接登录")
    user = m.User(
        openid=f"phone:{phone}",
        phone=phone,
        nickname=(body.nickname or "").strip() or f"游客{phone[-4:]}",
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return ok(_auth_payload(user))


# ---------------------------------------------------------------- 埋点上报

def _log_time(ts: int | None) -> datetime:
    """客户端毫秒时间戳（可选），缺失或异常时用服务器时间"""
    if ts and 0 < ts < 4102444800000:  # < 2100 年
        return datetime.fromtimestamp(ts / 1000)
    return datetime.now()


@router.post("/log")
def report_log(
    body: LogBody,
    db: Session = Depends(get_db),
    user: m.User | None = Depends(get_optional_user),
):
    """单条埋点 → t_user_log"""
    db.add(
        m.UserLog(
            user_id=user.id if user else 0,
            event=(body.event or "")[:32],
            target_type=(body.target_type or "")[:16],
            target_id=int(body.target_id or 0),
            keyword=(body.keyword or "")[:64],
            page=(body.page or "")[:64],
            channel=(body.channel or "")[:32],
            created_at=_log_time(body.ts),
        )
    )
    db.commit()
    return ok({"ok": True})


@router.post("/log/batch")
def report_log_batch(
    body: LogBatchBody,
    db: Session = Depends(get_db),
    user: m.User | None = Depends(get_optional_user),
):
    """批量埋点 → t_user_log（单次最多 100 条）"""
    items = (body.list or [])[:100]
    for item in items:
        db.add(
            m.UserLog(
                user_id=user.id if user else 0,
                event=(item.event or "")[:32],
                target_type=(item.target_type or "")[:16],
                target_id=int(item.target_id or 0),
                keyword=(item.keyword or "")[:64],
                page=(item.page or "")[:64],
                channel=(item.channel or "")[:32],
                created_at=_log_time(item.ts),
            )
        )
    db.commit()
    return ok({"ok": True, "count": len(items)})


# ---------------------------------------------------------------- 收藏

@router.get("/favorites")
def get_favorites(db: Session = Depends(get_db), user: m.User = Depends(get_current_user)):
    """返回 { spotIds: [], routeIds: [] }"""
    rows = db.execute(
        select(m.UserFavorite).where(
            m.UserFavorite.user_id == user.id, m.UserFavorite.favorite == 1
        )
    ).scalars().all()
    spot_ids = sorted(r.target_id for r in rows if r.target_type == "spot")
    route_ids = sorted(r.target_id for r in rows if r.target_type == "route")
    return ok({"spotIds": spot_ids, "routeIds": route_ids})


@router.post("/favorites")
def sync_favorite(
    body: FavoriteBody,
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
):
    """收藏 / 取消收藏（upsert）"""
    target_type = body.type
    if target_type not in ("spot", "route"):
        raise ApiError(CODE_PARAM, "type 仅支持 spot / route")
    if not body.targetId:
        raise ApiError(CODE_PARAM, "targetId 不能为空")

    row = db.execute(
        select(m.UserFavorite).where(
            m.UserFavorite.user_id == user.id,
            m.UserFavorite.target_type == target_type,
            m.UserFavorite.target_id == body.targetId,
        )
    ).scalar_one_or_none()
    if row is None:
        row = m.UserFavorite(
            user_id=user.id,
            target_type=target_type,
            target_id=body.targetId,
            favorite=1 if body.favorite else 0,
        )
        db.add(row)
    else:
        row.favorite = 1 if body.favorite else 0
    db.commit()
    return ok({"ok": True, "favorite": bool(body.favorite)})


# ---------------------------------------------------------------- 行程

@router.get("/trips")
def get_trips(db: Session = Depends(get_db), user: m.User = Depends(get_current_user)):
    """行程列表（新→旧）"""
    rows = db.execute(
        select(m.UserTrip)
        .where(m.UserTrip.user_id == user.id)
        .order_by(m.UserTrip.created_at.desc(), m.UserTrip.id.desc())
    ).scalars().all()
    return ok({"list": [sz.trip_to_json(t) for t in rows], "total": len(rows)})


@router.post("/trips")
def save_trip(
    body: TripBody,
    db: Session = Depends(get_db),
    user: m.User = Depends(get_current_user),
):
    """保存自定义行程"""
    if not body.title and not body.spotIds:
        raise ApiError(CODE_PARAM, "行程标题或景点不能为空")
    trip = m.UserTrip(
        user_id=user.id,
        title=(body.title or f"我的铜仁 {body.days or 1} 日游")[:128],
        days=max(1, int(body.days or 1)),
        spot_ids=[int(i) for i in (body.spotIds or [])],
        plan=body.plan,
        source=(body.source or "custom")[:16],
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return ok({"ok": True, "tripId": trip.id})
