"""
搜索接口（契约 2.4）
  GET /search?q=&type=all|spot|route|food

搜索行为落 t_user_log（event=search），是「搜索热度」分析的数据源
"""
from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..errors import ok
from .. import models as m
from ..security import get_optional_user
from .. import serializers as sz

router = APIRouter(tags=["search"])


@router.get("/search")
def search(
    q: str = "",
    type: str = "all",
    db: Session = Depends(get_db),
    user: m.User | None = Depends(get_optional_user),
):
    keyword = (q or "").strip()
    result: list[dict] = []

    def match_spot():
        kw = f"%{keyword}%"
        rows = db.execute(
            select(m.Spot)
            .where(
                m.Spot.status == 1,
                or_(
                    m.Spot.name.like(kw),
                    m.Spot.cat.like(kw),
                    m.Spot.district.like(kw),
                    m.Spot.brief.like(kw),
                ),
            )
            .order_by(m.Spot.sort, m.Spot.id)
        ).scalars().all()
        return [sz.spot_to_row(s, "spot") for s in rows]

    def match_route():
        kw = f"%{keyword}%"
        rows = db.execute(
            select(m.Route)
            .where(
                m.Route.status == 1,
                or_(
                    m.Route.name.like(kw),
                    m.Route.overview.like(kw),
                    m.Route.suitable.like(kw),
                    m.Route.foods.like(kw),
                ),
            )
            .order_by(m.Route.sort, m.Route.id)
        ).scalars().all()
        return [
            {
                "id": r.id,
                "name": r.name,
                "level": "",
                "cat": "路线",
                "district": "",
                "score": 0,
                "brief": r.overview,
                "img": r.cover,
                "type": "route",
            }
            for r in rows
        ]

    def match_food():
        kw = f"%{keyword}%"
        rows = db.execute(
            select(m.Food)
            .where(or_(m.Food.name.like(kw), m.Food.tag.like(kw), m.Food.desc_.like(kw)))
            .order_by(m.Food.sort, m.Food.id)
        ).scalars().all()
        return [
            {
                "id": r.id,
                "name": r.name,
                "level": "",
                "cat": r.tag,
                "district": "",
                "score": 0,
                "brief": r.desc_,
                "img": r.file,
                "type": "food",
            }
            for r in rows
        ]

    if keyword:
        if type == "spot":
            result = match_spot()
        elif type == "route":
            result = match_route()
        elif type == "food":
            result = match_food()
        else:
            result = match_spot() + match_route() + match_food()

        # 搜索日志 → t_user_log（分析原料）
        db.add(
            m.UserLog(
                user_id=user.id if user else 0,
                event="search",
                target_type="",
                target_id=0,
                keyword=keyword[:64],
                page="pages/search/search",
            )
        )
        db.commit()

    return ok({"list": result, "total": len(result), "keyword": keyword})
