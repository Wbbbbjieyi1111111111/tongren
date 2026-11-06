"""
内容域接口（契约 2.1 / 2.3）
  GET /spots   /spots/{id}   /spots/{id}/related
  GET /foods /folk /festivals /ethnic /seasons /banners /notices
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..errors import ApiError, CODE_NOT_FOUND, CODE_PARAM, ok
from .. import models as m
from .. import serializers as sz

router = APIRouter(tags=["content"])


def paging(page: int, page_size: int) -> tuple[int, int]:
    page = max(1, int(page or 1))
    page_size = min(100, max(1, int(page_size or 20)))
    return page, page_size


def load_spot(db: Session, spot_id: int) -> m.Spot:
    spot = db.execute(
        select(m.Spot)
        .where(m.Spot.id == spot_id, m.Spot.status == 1)
        .options(selectinload(m.Spot.images))
    ).scalar_one_or_none()
    if spot is None:
        raise ApiError(CODE_NOT_FOUND, "景点不存在")
    return spot


# ---------------------------------------------------------------- 景点

@router.get("/spots")
def list_spots(
    keyword: str = "",
    level: str = "",
    cat: str = "",
    district: str = "",
    page: int = 1,
    pageSize: int = 20,
    db: Session = Depends(get_db),
):
    """景点列表：keyword / level / cat / district 筛选 + 分页"""
    page, page_size = paging(page, pageSize)
    stmt = select(m.Spot).where(m.Spot.status == 1)
    if keyword:
        kw = f"%{keyword.strip()}%"
        stmt = stmt.where(
            or_(
                m.Spot.name.like(kw),
                m.Spot.brief.like(kw),
                m.Spot.cat.like(kw),
                m.Spot.district.like(kw),
            )
        )
    if level:
        stmt = stmt.where(m.Spot.level == level)
    if cat:
        stmt = stmt.where(m.Spot.cat == cat)
    if district:
        stmt = stmt.where(m.Spot.district == district)

    total = len(db.execute(stmt.with_only_columns(m.Spot.id)).all())
    rows = db.execute(
        stmt.order_by(m.Spot.sort, m.Spot.id)
        .options(selectinload(m.Spot.images))
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).scalars().all()
    return ok({"list": [sz.spot_to_json(s) for s in rows], "total": total})


@router.get("/spots/{spot_id}")
def get_spot(spot_id: int, db: Session = Depends(get_db)):
    """景点详情"""
    return ok(sz.spot_to_json(load_spot(db, spot_id)))


@router.get("/spots/{spot_id}/related")
def related_spots(spot_id: int, limit: int = 4, db: Session = Depends(get_db)):
    """相关推荐：同品类优先，其余按评分补齐（与前端 mock 口径一致）"""
    spot = load_spot(db, spot_id)
    limit = min(10, max(1, int(limit or 4)))
    others = db.execute(
        select(m.Spot)
        .where(m.Spot.id != spot.id, m.Spot.status == 1)
        .options(selectinload(m.Spot.images))
    ).scalars().all()
    same_cat = sorted(
        [s for s in others if s.cat == spot.cat], key=lambda s: (-float(s.score), s.id)
    )
    rest = sorted(
        [s for s in others if s.cat != spot.cat], key=lambda s: (-float(s.score), s.id)
    )
    return ok([sz.spot_to_json(s) for s in (same_cat + rest)[:limit]])


# ---------------------------------------------------------------- 文化内容

@router.get("/foods")
def list_foods(db: Session = Depends(get_db)):
    rows = db.execute(select(m.Food).order_by(m.Food.sort, m.Food.id)).scalars().all()
    return ok({"list": [sz.food_to_json(r) for r in rows]})


@router.get("/folk")
def list_folk(db: Session = Depends(get_db)):
    rows = db.execute(select(m.Folk).order_by(m.Folk.sort, m.Folk.id)).scalars().all()
    return ok({"list": [sz.folk_to_json(r) for r in rows]})


@router.get("/festivals")
def list_festivals(db: Session = Depends(get_db)):
    rows = db.execute(
        select(m.Festival).order_by(m.Festival.sort, m.Festival.id)
    ).scalars().all()
    return ok({"list": [sz.festival_to_json(r) for r in rows]})


@router.get("/ethnic")
def list_ethnic(db: Session = Depends(get_db)):
    rows = db.execute(select(m.Ethnic).order_by(m.Ethnic.sort, m.Ethnic.id)).scalars().all()
    return ok({"list": [sz.ethnic_to_json(r) for r in rows]})


@router.get("/seasons")
def list_seasons(db: Session = Depends(get_db)):
    rows = db.execute(select(m.Season).order_by(m.Season.sort, m.Season.id)).scalars().all()
    return ok({"list": [sz.season_to_json(r) for r in rows]})


@router.get("/banners")
def list_banners(db: Session = Depends(get_db)):
    rows = db.execute(
        select(m.Banner).where(m.Banner.status == 1).order_by(m.Banner.sort, m.Banner.id)
    ).scalars().all()
    return ok({"list": [sz.banner_to_json(r) for r in rows]})


@router.get("/notices")
def list_notices(db: Session = Depends(get_db)):
    rows = db.execute(
        select(m.Notice)
        .where(m.Notice.status == 1)
        .order_by(m.Notice.sort.desc(), m.Notice.publish_date.desc())
    ).scalars().all()
    return ok({"list": [sz.notice_to_json(r) for r in rows]})
