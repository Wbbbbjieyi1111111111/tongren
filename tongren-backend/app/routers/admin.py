"""
运维接口（契约外运维约定）
  GET  /health                       健康检查（无鉴权）
  GET  /admin/content/{type}/sync    从 sql/seed.json 同步内容数据（幂等 upsert）
  POST /admin/analysis/rerun         手动触发数据分析 pipeline
"""
import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..errors import ApiError, CODE_NOT_FOUND, CODE_PARAM, ok
from .. import models as m
from .. import pipelines

router = APIRouter(tags=["admin"])

SEED_PATH = Path(__file__).resolve().parent.parent.parent / "sql" / "seed.json"

CONTENT_TYPES = (
    "spots", "routes", "foods", "folk", "festivals",
    "ethnic", "seasons", "banners", "notices",
)


@router.get("/health")
def health(db: Session = Depends(get_db)):
    """健康检查：API 存活 + 数据库连通性"""
    db_ok = True
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False
    return ok(
        {
            "status": "ok" if db_ok else "degraded",
            "db": "up" if db_ok else "down",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    )


# ---------------------------------------------------------------- 内容同步

def _load_seed() -> dict:
    if not SEED_PATH.exists():
        raise ApiError(CODE_NOT_FOUND, f"种子文件不存在：{SEED_PATH}")
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def _sync_spots(db: Session, rows: list[dict]) -> int:
    for item in rows:
        spot = db.get(m.Spot, item["id"])
        fields = dict(
            name=item["name"], level=item.get("level", ""), cat=item.get("cat", ""),
            district=item.get("district", ""), score=item.get("score", 0),
            brief=item.get("brief", ""), slogan=item.get("slogan", ""), img=item.get("img", ""),
            ticket=item.get("ticket", ""), open_=item.get("open", ""),
            traffic=item.get("traffic", ""), duration=item.get("duration", ""),
            intro=item.get("intro") or [], tips=item.get("tips") or [],
            foods=item.get("foods") or [], sort=item.get("id", 0), status=1,
        )
        if spot is None:
            spot = m.Spot(id=item["id"], **fields)
            db.add(spot)
        else:
            for k, v in fields.items():
                setattr(spot, k, v)
        db.flush()
        # 重建图片列表
        for old in list(spot.images):
            db.delete(old)
        db.flush()
        for i, file in enumerate(item.get("images") or []):
            db.add(m.SpotImage(spot_id=spot.id, file=file, sort=i))
    return len(rows)


def _sync_routes(db: Session, rows: list[dict]) -> int:
    for item in rows:
        route = db.get(m.Route, item["id"])
        fields = dict(
            name=item["name"], days=item.get("days", 1), suitable=item.get("suitable", ""),
            suit_short=item.get("suitShort", ""), difficulty=item.get("difficulty", ""),
            overview=item.get("overview", ""), foods=item.get("foods", ""), tip=item.get("tip", ""),
            cover=item.get("cover", ""), sort=item.get("id", 0), status=1,
        )
        if route is None:
            route = m.Route(id=item["id"], **fields)
            db.add(route)
        else:
            for k, v in fields.items():
                setattr(route, k, v)
        db.flush()
        # 重建子表（行程/住宿/避坑/景点关联）
        db.query(m.RouteSpot).filter(m.RouteSpot.route_id == route.id).delete()
        db.query(m.RouteAvoid).filter(m.RouteAvoid.route_id == route.id).delete()
        db.query(m.RouteStay).filter(m.RouteStay.route_id == route.id).delete()
        for plan in db.query(m.RoutePlan).filter(m.RoutePlan.route_id == route.id).all():
            db.query(m.RoutePlanItem).filter(m.RoutePlanItem.plan_id == plan.id).delete()
            db.delete(plan)
        db.flush()
        for di, day in enumerate(item.get("plan") or [], start=1):
            plan = m.RoutePlan(
                route_id=route.id, day_index=di,
                day_label=day.get("day", f"Day {di}"), title=day.get("title", ""),
            )
            db.add(plan)
            db.flush()
            for si, it in enumerate(day.get("items") or []):
                db.add(
                    m.RoutePlanItem(
                        plan_id=plan.id, time_=it.get("time", ""),
                        name=it.get("name", ""), desc_=it.get("desc", ""), sort=si,
                    )
                )
        for si, stay in enumerate(item.get("stays") or []):
            db.add(
                m.RouteStay(
                    route_id=route.id, name=stay.get("name", ""), type=stay.get("type", ""),
                    price=stay.get("price", ""), desc_=stay.get("desc", ""), sort=si,
                )
            )
        for si, avoid in enumerate(item.get("avoid") or []):
            db.add(m.RouteAvoid(route_id=route.id, content=avoid, sort=si))
        for si, sid in enumerate(item.get("spotIds") or []):
            db.add(m.RouteSpot(route_id=route.id, spot_id=int(sid), sort=si))
    return len(rows)


def _replace_table(db: Session, model, rows: list[dict], builder) -> int:
    db.query(model).delete()
    for item in rows:
        db.add(builder(item))
    return len(rows)


@router.get("/admin/content/{type}/sync")
def sync_content(type: str, db: Session = Depends(get_db)):
    """按类型从种子数据同步内容（先删后插 / upsert，可重复执行）"""
    if type not in CONTENT_TYPES:
        raise ApiError(CODE_PARAM, f"type 仅支持：{'、'.join(CONTENT_TYPES)}")
    seed = _load_seed()

    if type == "spots":
        count = _sync_spots(db, seed.get("spots", []))
    elif type == "routes":
        count = _sync_routes(db, seed.get("routes", []))
    elif type == "foods":
        count = _replace_table(db, m.Food, seed.get("foods", []),
                               lambda x: m.Food(name=x["name"], tag=x.get("tag", ""), file=x.get("file", ""), desc_=x.get("desc", "")))
    elif type == "folk":
        count = _replace_table(db, m.Folk, seed.get("folk", []),
                               lambda x: m.Folk(name=x["name"], level=x.get("level", ""), desc_=x.get("desc", "")))
    elif type == "festivals":
        count = _replace_table(db, m.Festival, seed.get("festivals", []),
                               lambda x: m.Festival(month=x.get("month", ""), day=x.get("day", ""), name=x["name"], place=x.get("place", ""), desc_=x.get("desc", "")))
    elif type == "ethnic":
        count = _replace_table(db, m.Ethnic, seed.get("ethnic", []),
                               lambda x: m.Ethnic(name=x["name"], keys_=x.get("keys", ""), desc_=x.get("desc", ""), file=x.get("file", ""), mono=1 if x.get("mono") else 0))
    elif type == "seasons":
        count = _replace_table(db, m.Season, seed.get("seasons", []),
                               lambda x: m.Season(name=x["name"], months=x.get("months", ""), temp=x.get("temp", ""), note=x.get("note", ""), icon=x.get("icon", "leaf")))
    elif type == "banners":
        count = _replace_table(db, m.Banner, seed.get("banners", []),
                               lambda x: m.Banner(id=x["id"], file=x.get("file", ""), eyebrow=x.get("eyebrow", ""), title=x.get("title", ""), meta=x.get("meta", ""), link_type="spot", link_id=x.get("id", 0), sort=x.get("id", 0)))
    else:  # notices
        count = _replace_table(db, m.Notice, seed.get("notices", []),
                               lambda x: m.Notice(id=x["id"], title=x["title"], content=x.get("content", x["title"]), publish_date=x.get("publish_date", "2026-01-01"), sort=x.get("id", 0)))
    db.commit()
    return ok({"type": type, "count": count})


# ---------------------------------------------------------------- 分析重跑

@router.post("/admin/analysis/rerun")
def rerun_analysis(db: Session = Depends(get_db)):
    """手动触发数据分析 pipeline（幂等，写入当日 stat_date）"""
    result = pipelines.run_all(db)
    return ok({"task": "daily_analytics", **result})
