"""
ORM 模型 —— 与 sql/schema.sql 逐表一一对应（表名 / 字段名完全一致）

Python 关键字冲突的列用「属性名_」映射到原文列名：
  desc→desc_   keys→keys_   open→open_   time→time_   rank→rank_
"""
from datetime import datetime

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def _now() -> datetime:
    """created_at / updated_at 的统一默认值"""
    return datetime.now()


# ============================================================================
#  一、内容主数据
# ============================================================================

class Spot(Base):
    __tablename__ = "t_spot"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    level: Mapped[str] = mapped_column(String(8), default="")
    cat: Mapped[str] = mapped_column(String(32), default="")
    district: Mapped[str] = mapped_column(String(32), default="")
    score: Mapped[float] = mapped_column(Numeric(2, 1), default=0)
    brief: Mapped[str] = mapped_column(String(255), default="")
    slogan: Mapped[str] = mapped_column(String(255), default="")
    img: Mapped[str] = mapped_column(String(128), default="")
    ticket: Mapped[str] = mapped_column(String(64), default="")
    open_: Mapped[str] = mapped_column("open", String(64), default="")
    traffic: Mapped[str] = mapped_column(String(128), default="")
    duration: Mapped[str] = mapped_column(String(64), default="")
    intro: Mapped[list | None] = mapped_column(JSON, nullable=True)
    tips: Mapped[list | None] = mapped_column(JSON, nullable=True)
    foods: Mapped[list | None] = mapped_column(JSON, nullable=True)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[object] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[object] = mapped_column(DateTime, default=_now, onupdate=_now)

    images: Mapped[list["SpotImage"]] = relationship(
        back_populates="spot", order_by="SpotImage.sort", cascade="all, delete-orphan"
    )


class SpotImage(Base):
    __tablename__ = "t_spot_image"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    spot_id: Mapped[int] = mapped_column(ForeignKey("t_spot.id", ondelete="CASCADE"))
    file: Mapped[str] = mapped_column(String(128), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)

    spot: Mapped[Spot] = relationship(back_populates="images")


class Route(Base):
    __tablename__ = "t_route"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    days: Mapped[int] = mapped_column(Integer, default=1)
    suitable: Mapped[str] = mapped_column(String(64), default="")
    suit_short: Mapped[str] = mapped_column(String(32), default="")
    difficulty: Mapped[str] = mapped_column(String(16), default="")
    overview: Mapped[str] = mapped_column(String(255), default="")
    foods: Mapped[str] = mapped_column(String(255), default="")
    tip: Mapped[str] = mapped_column(String(255), default="")
    cover: Mapped[str] = mapped_column(String(128), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[object] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[object] = mapped_column(DateTime, default=_now, onupdate=_now)

    plans: Mapped[list["RoutePlan"]] = relationship(
        back_populates="route", order_by="RoutePlan.day_index", cascade="all, delete-orphan"
    )
    stays: Mapped[list["RouteStay"]] = relationship(
        back_populates="route", order_by="RouteStay.sort", cascade="all, delete-orphan"
    )
    avoids: Mapped[list["RouteAvoid"]] = relationship(
        back_populates="route", order_by="RouteAvoid.sort", cascade="all, delete-orphan"
    )
    spot_links: Mapped[list["RouteSpot"]] = relationship(
        back_populates="route", order_by="RouteSpot.sort", cascade="all, delete-orphan"
    )


class RoutePlan(Base):
    __tablename__ = "t_route_plan"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("t_route.id", ondelete="CASCADE"))
    day_index: Mapped[int] = mapped_column(Integer, default=1)
    day_label: Mapped[str] = mapped_column(String(32), default="")
    title: Mapped[str] = mapped_column(String(64), default="")

    route: Mapped[Route] = relationship(back_populates="plans")
    items: Mapped[list["RoutePlanItem"]] = relationship(
        back_populates="plan", order_by="RoutePlanItem.sort", cascade="all, delete-orphan"
    )


class RoutePlanItem(Base):
    __tablename__ = "t_route_plan_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("t_route_plan.id", ondelete="CASCADE"))
    time_: Mapped[str] = mapped_column("time", String(8), default="")
    name: Mapped[str] = mapped_column(String(64), default="")
    desc_: Mapped[str] = mapped_column("desc", String(255), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)

    plan: Mapped[RoutePlan] = relationship(back_populates="items")


class RouteStay(Base):
    __tablename__ = "t_route_stay"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("t_route.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(128), default="")
    type: Mapped[str] = mapped_column(String(64), default="")
    price: Mapped[str] = mapped_column(String(32), default="")
    desc_: Mapped[str] = mapped_column("desc", String(255), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)

    route: Mapped[Route] = relationship(back_populates="stays")


class RouteAvoid(Base):
    __tablename__ = "t_route_avoid"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("t_route.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(String(255), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)

    route: Mapped[Route] = relationship(back_populates="avoids")


class RouteSpot(Base):
    __tablename__ = "t_route_spot"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("t_route.id", ondelete="CASCADE"))
    spot_id: Mapped[int] = mapped_column(ForeignKey("t_spot.id", ondelete="CASCADE"))
    sort: Mapped[int] = mapped_column(Integer, default=0)

    route: Mapped[Route] = relationship(back_populates="spot_links")


class Food(Base):
    __tablename__ = "t_food"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    tag: Mapped[str] = mapped_column(String(32), default="")
    file: Mapped[str] = mapped_column(String(128), default="")
    desc_: Mapped[str] = mapped_column("desc", String(255), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)


class Folk(Base):
    __tablename__ = "t_folk"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    level: Mapped[str] = mapped_column(String(64), default="")
    desc_: Mapped[str] = mapped_column("desc", String(255), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)


class Festival(Base):
    __tablename__ = "t_festival"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    month: Mapped[str] = mapped_column(String(32), default="")
    day: Mapped[str] = mapped_column(String(32), default="")
    name: Mapped[str] = mapped_column(String(64))
    place: Mapped[str] = mapped_column(String(64), default="")
    desc_: Mapped[str] = mapped_column("desc", String(255), default="")
    sort: Mapped[int] = mapped_column(Integer, default=0)


class Ethnic(Base):
    __tablename__ = "t_ethnic"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    keys_: Mapped[str] = mapped_column("keys", String(128), default="")
    desc_: Mapped[str] = mapped_column("desc", String(255), default="")
    file: Mapped[str] = mapped_column(String(128), default="")
    mono: Mapped[int] = mapped_column(Integer, default=0)
    sort: Mapped[int] = mapped_column(Integer, default=0)


class Season(Base):
    __tablename__ = "t_season"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(16))
    months: Mapped[str] = mapped_column(String(32), default="")
    temp: Mapped[str] = mapped_column(String(32), default="")
    note: Mapped[str] = mapped_column(String(128), default="")
    icon: Mapped[str] = mapped_column(String(32), default="leaf")
    sort: Mapped[int] = mapped_column(Integer, default=0)


class Banner(Base):
    __tablename__ = "t_banner"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file: Mapped[str] = mapped_column(String(128), default="")
    eyebrow: Mapped[str] = mapped_column(String(64), default="")
    title: Mapped[str] = mapped_column(String(128), default="")
    meta: Mapped[str] = mapped_column(String(128), default="")
    link_type: Mapped[str] = mapped_column(String(16), default="")
    link_id: Mapped[int] = mapped_column(Integer, default=0)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)


class Notice(Base):
    __tablename__ = "t_notice"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(128), default="")
    content: Mapped[str] = mapped_column(String(512), default="")
    publish_date: Mapped[object] = mapped_column(Date)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[int] = mapped_column(Integer, default=1)


# ============================================================================
#  二、用户行为（同时作为 Python 数据分析的原始输入）
# ============================================================================

class User(Base):
    __tablename__ = "t_user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    openid: Mapped[str] = mapped_column(String(64), default="")
    unionid: Mapped[str] = mapped_column(String(64), default="")
    nickname: Mapped[str] = mapped_column(String(64), default="")
    avatar: Mapped[str] = mapped_column(String(255), default="")
    # 账号密码登录扩展（见 sql/schema.sql 注释）：
    # openid 唯一约束下，账号注册用户写入 "phone:<手机号>"，微信登录用户写真实 openid
    phone: Mapped[str] = mapped_column(String(20), default="")
    password_hash: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[object] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[object] = mapped_column(DateTime, default=_now, onupdate=_now)


class UserFavorite(Base):
    __tablename__ = "t_user_favorite"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, default=0)
    target_type: Mapped[str] = mapped_column(String(16))
    target_id: Mapped[int] = mapped_column(Integer)
    favorite: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[object] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[object] = mapped_column(DateTime, default=_now, onupdate=_now)


class UserTrip(Base):
    __tablename__ = "t_user_trip"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(128), default="")
    days: Mapped[int] = mapped_column(Integer, default=1)
    spot_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    plan: Mapped[object | None] = mapped_column(JSON, nullable=True)
    source: Mapped[str] = mapped_column(String(16), default="custom")
    created_at: Mapped[object] = mapped_column(DateTime, default=_now)


class UserLog(Base):
    __tablename__ = "t_user_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, default=0)
    event: Mapped[str] = mapped_column(String(32))
    target_type: Mapped[str] = mapped_column(String(16), default="")
    target_id: Mapped[int] = mapped_column(Integer, default=0)
    keyword: Mapped[str] = mapped_column(String(64), default="")
    page: Mapped[str] = mapped_column(String(64), default="")
    channel: Mapped[str] = mapped_column(String(32), default="")
    created_at: Mapped[object] = mapped_column(DateTime, default=_now)


# ============================================================================
#  三、Python 数据分析结果表（/analytics/* 只读这些表）
# ============================================================================

class AnalyticsOverview(Base):
    __tablename__ = "t_analytics_overview"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_date: Mapped[object] = mapped_column(Date)
    metric_key: Mapped[str] = mapped_column(String(32))
    label: Mapped[str] = mapped_column(String(32), default="")
    value: Mapped[str] = mapped_column(String(32), default="0")
    unit: Mapped[str] = mapped_column(String(16), default="")
    delta: Mapped[str] = mapped_column(String(16), default="")
    trend: Mapped[str] = mapped_column(String(8), default="up")
    updated_at: Mapped[object] = mapped_column(DateTime, default=_now, onupdate=_now)


class AnalyticsTrend(Base):
    __tablename__ = "t_analytics_trend"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_date: Mapped[object] = mapped_column(Date)
    period: Mapped[str] = mapped_column(String(16), default="month")
    label: Mapped[str] = mapped_column(String(16))
    value: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    unit: Mapped[str] = mapped_column(String(16), default="")
    updated_at: Mapped[object] = mapped_column(DateTime, default=_now, onupdate=_now)


class AnalyticsDistrict(Base):
    __tablename__ = "t_analytics_district"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_date: Mapped[object] = mapped_column(Date)
    district: Mapped[str] = mapped_column(String(32))
    value: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    unit: Mapped[str] = mapped_column(String(16), default="")
    updated_at: Mapped[object] = mapped_column(DateTime, default=_now, onupdate=_now)


class AnalyticsCategory(Base):
    __tablename__ = "t_analytics_category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_date: Mapped[object] = mapped_column(Date)
    category: Mapped[str] = mapped_column(String(32))
    value: Mapped[float] = mapped_column(Numeric(8, 2), default=0)
    unit: Mapped[str] = mapped_column(String(16), default="%")
    updated_at: Mapped[object] = mapped_column(DateTime, default=_now, onupdate=_now)


class AnalyticsRanking(Base):
    __tablename__ = "t_analytics_ranking"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_date: Mapped[object] = mapped_column(Date)
    target_type: Mapped[str] = mapped_column(String(16), default="spot")
    target_id: Mapped[int] = mapped_column(Integer, default=0)
    name: Mapped[str] = mapped_column(String(64), default="")
    rank_: Mapped[int] = mapped_column("rank", Integer, default=0)
    score: Mapped[float] = mapped_column(Numeric(4, 2), default=0)
    visitors: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    updated_at: Mapped[object] = mapped_column(DateTime, default=_now, onupdate=_now)


class AnalyticsSeason(Base):
    __tablename__ = "t_analytics_season"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_date: Mapped[object] = mapped_column(Date)
    season: Mapped[str] = mapped_column(String(8))
    value: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    note: Mapped[str] = mapped_column(String(128), default="")
    unit: Mapped[str] = mapped_column(String(16), default="指数")
    updated_at: Mapped[object] = mapped_column(DateTime, default=_now, onupdate=_now)


class AnalyticsHeat(Base):
    __tablename__ = "t_analytics_heat"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_date: Mapped[object] = mapped_column(Date)
    grid_row: Mapped[int] = mapped_column(Integer, default=0)
    grid_col: Mapped[int] = mapped_column(Integer, default=0)
    value: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    updated_at: Mapped[object] = mapped_column(DateTime, default=_now, onupdate=_now)


class AnalyticsPrediction(Base):
    __tablename__ = "t_analytics_prediction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_date: Mapped[object] = mapped_column(Date)
    model_name: Mapped[str] = mapped_column(String(64), default="")
    label: Mapped[str] = mapped_column(String(64))
    value: Mapped[str] = mapped_column(String(128), default="")
    advice: Mapped[str] = mapped_column(String(255), default="")
    confidence: Mapped[float] = mapped_column(Numeric(5, 4), default=0)
    updated_at: Mapped[object] = mapped_column(DateTime, default=_now, onupdate=_now)


class AnalysisTask(Base):
    __tablename__ = "t_analysis_task"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_name: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default="running")
    started_at: Mapped[object] = mapped_column(DateTime, default=_now)
    finished_at: Mapped[object | None] = mapped_column(DateTime, nullable=True)
    rows_written: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(String(512), default="")
