"""
路线域接口（契约 2.2）
  GET  /routes            路线列表
  GET  /routes/{id}       路线详情（含 plan / stays / avoid）
  POST /routes/custom     自定义行程生成
"""
from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..errors import ApiError, CODE_NOT_FOUND, CODE_PARAM, ok
from .. import models as m
from ..schemas import CustomRouteBody
from .. import serializers as sz

router = APIRouter(tags=["routes"])

# 自定义行程生成规则（与前端 mock 一致）：每 3 个景点 1 天，时间点 09:00/11:30/14:30
DAY_TIMES = ["09:00", "11:30", "14:30"]


def _load_route(db: Session, route_id: int) -> m.Route:
    route = db.execute(
        select(m.Route)
        .where(m.Route.id == route_id, m.Route.status == 1)
        .options(
            selectinload(m.Route.plans).selectinload(m.RoutePlan.items),
            selectinload(m.Route.stays),
            selectinload(m.Route.avoids),
            selectinload(m.Route.spot_links),
        )
    ).scalar_one_or_none()
    if route is None:
        raise ApiError(CODE_NOT_FOUND, "路线不存在")
    return route


@router.get("/routes")
def list_routes(
    days: int = 0,
    suit: str = "",
    keyword: str = "",
    page: int = 1,
    pageSize: int = 20,
    db: Session = Depends(get_db),
):
    """路线列表：days / suit（短标签）/ keyword 筛选 + 分页"""
    page = max(1, int(page or 1))
    page_size = min(100, max(1, int(pageSize or 20)))
    stmt = select(m.Route).where(m.Route.status == 1)
    if days:
        stmt = stmt.where(m.Route.days == int(days))
    if suit:
        stmt = stmt.where(m.Route.suit_short == suit)
    if keyword:
        kw = f"%{keyword.strip()}%"
        stmt = stmt.where(
            or_(
                m.Route.name.like(kw),
                m.Route.overview.like(kw),
                m.Route.suitable.like(kw),
                m.Route.foods.like(kw),
            )
        )
    total = len(db.execute(stmt.with_only_columns(m.Route.id)).all())
    rows = db.execute(
        stmt.order_by(m.Route.sort, m.Route.id)
        .options(
            selectinload(m.Route.plans).selectinload(m.RoutePlan.items),
            selectinload(m.Route.stays),
            selectinload(m.Route.avoids),
            selectinload(m.Route.spot_links),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).scalars().all()
    return ok({"list": [sz.route_to_json(r) for r in rows], "total": total})


@router.get("/routes/{route_id}")
def get_route(route_id: int, db: Session = Depends(get_db)):
    """路线详情"""
    return ok(sz.route_to_json(_load_route(db, route_id)))


@router.post("/routes/custom")
def custom_route(body: CustomRouteBody, db: Session = Depends(get_db)):
    """自定义行程生成：每 3 个景点 1 天，时间点 09:00 / 11:30 / 14:30"""
    spot_ids = [int(i) for i in (body.spotIds or []) if i]
    if not spot_ids:
        raise ApiError(CODE_PARAM, "请至少选择一个景点")

    spots = {
        s.id: s
        for s in db.execute(select(m.Spot).where(m.Spot.id.in_(spot_ids))).scalars().all()
    }

    groups = [spot_ids[i:i + 3] for i in range(0, len(spot_ids), 3)]
    days = []
    for gi, group in enumerate(groups):
        items = []
        for si, sid in enumerate(group):
            spot = spots.get(sid)
            items.append(
                {
                    "time": DAY_TIMES[si],
                    "name": spot.name if spot else str(sid),
                    "desc": f"{spot.district} · {spot.cat}" if spot else "",
                }
            )
        day_label = f"DAY {gi + 1}"
        days.append({"day": day_label, "title": day_label, "items": items})

    return ok(
        {
            "title": body.title or f"我的铜仁 {len(groups)} 日游",
            "dayCount": len(groups),
            "days": days,
            "plan": days,
        }
    )
