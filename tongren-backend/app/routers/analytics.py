"""
分析域接口（契约 3）——只读 t_analytics_* 结果表，查表拼 JSON
  GET /analytics/all
  GET /analytics/overview|trend|district|category|ranking|season|heat|prediction

Python 分析 pipeline（app/pipelines.py）负责从 t_user_log 训练/聚合后写入这些表。
"""
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..errors import ok
from .. import models as m

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _fmt_time(dt) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else ""


def _latest_stat_date(db: Session) -> date | None:
    return db.execute(select(func.max(m.AnalyticsOverview.stat_date))).scalar_one_or_none()


def _in_range(stat_date: date, start: str, end: str) -> bool:
    if start and stat_date < date.fromisoformat(start):
        return False
    if end and stat_date > date.fromisoformat(end):
        return False
    return True


def _updated_at(db: Session, rows) -> str:
    stamps = [r.updated_at for r in rows if getattr(r, "updated_at", None)]
    return _fmt_time(max(stamps)) if stamps else ""


# ---------------------------------------------------------------- 单项

@router.get("/overview")
def overview(
    startDate: str = "", endDate: str = "", district: str = "",
    db: Session = Depends(get_db),
):
    stat = _latest_stat_date(db)
    rows = []
    if stat and _in_range(stat, startDate, endDate):
        rows = db.execute(
            select(m.AnalyticsOverview)
            .where(m.AnalyticsOverview.stat_date == stat)
            .order_by(m.AnalyticsOverview.id)
        ).scalars().all()
    data = {
        "list": [
            {
                "key": r.metric_key,
                "label": r.label,
                "value": r.value,
                "unit": r.unit,
                "delta": r.delta,
                "trend": r.trend,
            }
            for r in rows
        ],
        "updatedAt": _updated_at(db, rows),
    }
    return ok(data)


@router.get("/trend")
def trend(
    startDate: str = "", endDate: str = "", district: str = "",
    period: str = Query(default="month", pattern="^(day|month|quarter)$"),
    db: Session = Depends(get_db),
):
    stat = _latest_stat_date(db)
    rows = []
    if stat and _in_range(stat, startDate, endDate):
        rows = db.execute(
            select(m.AnalyticsTrend)
            .where(m.AnalyticsTrend.stat_date == stat, m.AnalyticsTrend.period == period)
            .order_by(m.AnalyticsTrend.id)
        ).scalars().all()
    unit = rows[0].unit if rows else "万人次"
    return ok(
        {
            "list": [{"label": r.label, "value": float(r.value)} for r in rows],
            "unit": unit,
            "updatedAt": _updated_at(db, rows),
        }
    )


@router.get("/district")
def district(
    startDate: str = "", endDate: str = "", district: str = "",
    db: Session = Depends(get_db),
):
    stat = _latest_stat_date(db)
    rows = []
    if stat and _in_range(stat, startDate, endDate):
        stmt = (
            select(m.AnalyticsDistrict)
            .where(m.AnalyticsDistrict.stat_date == stat)
            .order_by(m.AnalyticsDistrict.value.desc(), m.AnalyticsDistrict.id)
        )
        if district:
            stmt = stmt.where(m.AnalyticsDistrict.district == district)
        rows = db.execute(stmt).scalars().all()
    unit = rows[0].unit if rows else "万人次"
    return ok(
        {
            "list": [{"label": r.district, "value": float(r.value)} for r in rows],
            "unit": unit,
            "updatedAt": _updated_at(db, rows),
        }
    )


@router.get("/category")
def category(
    startDate: str = "", endDate: str = "", district: str = "",
    db: Session = Depends(get_db),
):
    stat = _latest_stat_date(db)
    rows = []
    if stat and _in_range(stat, startDate, endDate):
        rows = db.execute(
            select(m.AnalyticsCategory)
            .where(m.AnalyticsCategory.stat_date == stat)
            .order_by(m.AnalyticsCategory.value.desc(), m.AnalyticsCategory.id)
        ).scalars().all()
    return ok(
        {
            "list": [{"label": r.category, "value": float(r.value)} for r in rows],
            "unit": rows[0].unit if rows else "%",
            "updatedAt": _updated_at(db, rows),
        }
    )


@router.get("/ranking")
def ranking(
    startDate: str = "", endDate: str = "", district: str = "",
    db: Session = Depends(get_db),
):
    stat = _latest_stat_date(db)
    rows = []
    if stat and _in_range(stat, startDate, endDate):
        rows = db.execute(
            select(m.AnalyticsRanking)
            .where(m.AnalyticsRanking.stat_date == stat)
            .order_by(m.AnalyticsRanking.rank_)
        ).scalars().all()
    return ok(
        {
            "list": [
                {
                    "rank": r.rank_,
                    "name": r.name,
                    "score": float(r.score),
                    "visitors": float(r.visitors),
                }
                for r in rows
            ],
            "updatedAt": _updated_at(db, rows),
        }
    )


@router.get("/season")
def season(
    startDate: str = "", endDate: str = "", district: str = "",
    db: Session = Depends(get_db),
):
    stat = _latest_stat_date(db)
    rows = []
    if stat and _in_range(stat, startDate, endDate):
        rows = db.execute(
            select(m.AnalyticsSeason)
            .where(m.AnalyticsSeason.stat_date == stat)
            .order_by(m.AnalyticsSeason.id)
        ).scalars().all()
    return ok(
        {
            "list": [{"label": r.season, "value": float(r.value), "note": r.note} for r in rows],
            "unit": rows[0].unit if rows else "指数",
            "updatedAt": _updated_at(db, rows),
        }
    )


@router.get("/heat")
def heat(
    startDate: str = "", endDate: str = "", district: str = "",
    db: Session = Depends(get_db),
):
    stat = _latest_stat_date(db)
    rows = []
    if stat and _in_range(stat, startDate, endDate):
        rows = db.execute(
            select(m.AnalyticsHeat)
            .where(m.AnalyticsHeat.stat_date == stat)
            .order_by(m.AnalyticsHeat.grid_row, m.AnalyticsHeat.grid_col)
        ).scalars().all()
    grid = [{"row": r.grid_row, "col": r.grid_col, "value": float(r.value)} for r in rows]
    max_row = max((r.grid_row for r in rows), default=0) + 1
    max_col = max((r.grid_col for r in rows), default=0) + 1
    return ok(
        {
            "list": grid,
            "rows": max_row,
            "cols": max_col,
            "updatedAt": _updated_at(db, rows),
        }
    )


@router.get("/prediction")
def prediction(
    startDate: str = "", endDate: str = "", district: str = "",
    db: Session = Depends(get_db),
):
    stat = _latest_stat_date(db)
    rows = []
    if stat and _in_range(stat, startDate, endDate):
        rows = db.execute(
            select(m.AnalyticsPrediction)
            .where(m.AnalyticsPrediction.stat_date == stat)
            .order_by(m.AnalyticsPrediction.id)
        ).scalars().all()
    return ok(
        {
            "list": [{"label": r.label, "value": r.value, "advice": r.advice} for r in rows],
            "updatedAt": _updated_at(db, rows),
        }
    )


# ---------------------------------------------------------------- 聚合

@router.get("/all")
def analytics_all(
    startDate: str = "",
    endDate: str = "",
    district_: str = Query(default="", alias="district"),
    db: Session = Depends(get_db),
):
    """一次性返回全部分析数据（结构与前端 mock 完全一致）"""
    base = {"startDate": startDate, "endDate": endDate, "district": district_}
    ov = overview(**base, db=db)["data"]
    td = trend(**base, period="month", db=db)["data"]
    dt = district(**base, db=db)["data"]
    ct = category(**base, db=db)["data"]
    rk = ranking(**base, db=db)["data"]
    ss = season(**base, db=db)["data"]
    ht = heat(**base, db=db)["data"]
    fc = prediction(**base, db=db)["data"]

    stamps = [
        x["updatedAt"] for x in (ov, td, dt, ct, rk, ss, ht, fc) if x.get("updatedAt")
    ]
    return ok(
        {
            "updatedAt": max(stamps) if stamps else "",
            "source": "python-analysis",
            "overview": {"list": ov["list"]},
            "trend": {"list": td["list"], "unit": td["unit"]},
            "district": {"list": dt["list"], "unit": dt["unit"]},
            "category": {"list": ct["list"], "unit": ct["unit"]},
            "ranking": {"list": rk["list"]},
            "season": {"list": ss["list"], "unit": ss["unit"]},
            "heat": {"list": ht["list"], "rows": ht["rows"], "cols": ht["cols"]},
            "prediction": {"list": fc["list"]},
        }
    )
