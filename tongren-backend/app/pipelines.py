"""
数据分析 pipeline —— 从 t_user_log（分析原料）聚合 / 训练，写入 t_analytics_* 结果表

设计约定
  - 幂等：每次以 stat_date = 当天 为粒度「先 DELETE 后 INSERT」，可重复执行；
  - 建模：趋势预测用 XGBoost（缺失时回退 sklearn 线性回归），random_state=42；
  - 出口：/analytics/* 接口只读结果表，不关心本模块细节。
"""
from datetime import date, datetime, timedelta

import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from . import models as m

try:  # XGBoost 可选
    from xgboost import XGBRegressor

    def _fit_predict(series: list[float], steps: int) -> list[float]:
        """series: 历史月度序列 → 未来 steps 个预测值"""
        import numpy as np

        X = np.arange(len(series)).reshape(-1, 1)
        y = np.array(series, dtype=float)
        model = XGBRegressor(
            n_estimators=200, max_depth=3, learning_rate=0.1, random_state=42, verbosity=0
        )
        model.fit(X, y)
        Xf = np.arange(len(series), len(series) + steps).reshape(-1, 1)
        return [max(0.0, float(v)) for v in model.predict(Xf)]

    MODEL_NAME = "xgb_visitors"
except Exception:  # pragma: no cover - 无 xgboost 环境
    from sklearn.linear_model import LinearRegression

    def _fit_predict(series: list[float], steps: int) -> list[float]:
        import numpy as np

        X = np.arange(len(series)).reshape(-1, 1)
        y = np.array(series, dtype=float)
        model = LinearRegression()
        model.fit(X, y)
        Xf = np.arange(len(series), len(series) + steps).reshape(-1, 1)
        return [max(0.0, float(v)) for v in model.predict(Xf)]

    MODEL_NAME = "linear_visitors"

SEASON_OF_MONTH = {
    1: "冬", 2: "冬", 3: "春", 4: "春", 5: "春", 6: "夏",
    7: "夏", 8: "夏", 9: "秋", 10: "秋", 11: "秋", 12: "冬",
}
SEASON_NOTE = {"春": "杜鹃花期", "夏": "避暑旺季", "秋": "彩林最佳", "冬": "雪景温泉"}
DAY_BUCKETS = ["凌晨", "上午", "下午", "晚上"]  # 0-6 / 6-12 / 12-18 / 18-24


def _replace(db: Session, model, stat_date: date, rows: list) -> int:
    """幂等写入：先删当日，再插新结果"""
    db.execute(delete(model).where(model.stat_date == stat_date))
    for row in rows:
        row.stat_date = stat_date
        db.add(row)
    return len(rows)


def run_all(db: Session) -> dict:
    """执行全量分析，返回任务摘要（同时记录 t_analysis_task）"""
    task = m.AnalysisTask(task_name="daily_analytics", status="running")
    db.add(task)
    db.commit()

    try:
        logs = pd.read_sql(
            select(
                m.UserLog.event, m.UserLog.target_type, m.UserLog.target_id,
                m.UserLog.user_id, m.UserLog.created_at,
            ),
            db.bind,
        )
        if logs.empty:
            task.status = "success"
            task.message = "t_user_log 为空，保留基线数据不覆盖"
            task.finished_at = datetime.now()
            db.commit()
            return {"status": "success", "rows_written": 0, "message": task.message}

        logs["created_at"] = pd.to_datetime(logs["created_at"])
        spots = pd.read_sql(
            select(m.Spot.id, m.Spot.name, m.Spot.cat, m.Spot.district, m.Spot.score),
            db.bind,
        )
        today = date.today()
        rows_written = 0

        views = logs[logs["event"].isin(["spot_view", "page_view", "favorite", "trip_generate"])]
        spot_views = views[views["target_type"] == "spot"].merge(
            spots, left_on="target_id", right_on="id", how="left"
        )

        # ---- 趋势（按月） ----
        monthly = views.set_index("created_at").resample("ME").size()
        trend_rows = [
            m.AnalyticsTrend(
                period="month", label=f"{ts.month}月", value=float(v), unit="人次"
            )
            for ts, v in monthly.items()
        ]
        rows_written += _replace(db, m.AnalyticsTrend, today, trend_rows)

        # ---- 区县分布 ----
        dist = (
            spot_views.dropna(subset=["district"])
            .groupby("district").size().sort_values(ascending=False)
        )
        rows_written += _replace(
            db, m.AnalyticsDistrict, today,
            [m.AnalyticsDistrict(district=k, value=float(v), unit="人次") for k, v in dist.items()],
        )

        # ---- 品类占比 ----
        cat = spot_views.dropna(subset=["cat"]).groupby("cat").size()
        cat_pct = (cat / cat.sum() * 100).round(2).sort_values(ascending=False)
        rows_written += _replace(
            db, m.AnalyticsCategory, today,
            [m.AnalyticsCategory(category=k, value=float(v), unit="%") for k, v in cat_pct.items()],
        )

        # ---- 景点排行 ----
        top = spot_views.groupby(["target_id", "name", "score"]).size().sort_values(ascending=False).head(10)
        ranking_rows = []
        for i, ((tid, name, score), cnt) in enumerate(top.items(), start=1):
            ranking_rows.append(
                m.AnalyticsRanking(
                    target_type="spot", target_id=int(tid), name=str(name),
                    rank_=i, score=float(score or 0), visitors=float(cnt),
                )
            )
        rows_written += _replace(db, m.AnalyticsRanking, today, ranking_rows)

        # ---- 季节指数 ----
        season = views.groupby(views["created_at"].dt.month.map(SEASON_OF_MONTH)).size()
        peak = float(season.max()) if len(season) else 1.0
        rows_written += _replace(
            db, m.AnalyticsSeason, today,
            [
                m.AnalyticsSeason(
                    season=s, value=round(float(season.get(s, 0)) / peak * 100, 2),
                    note=SEASON_NOTE.get(s, ""), unit="指数",
                )
                for s in ["春", "夏", "秋", "冬"]
            ],
        )

        # ---- 热力网格（行=流量前4区县，列=时段） ----
        top_districts = list(dist.head(4).index)
        heat_rows = []
        for ri, d in enumerate(top_districts):
            sub = spot_views[spot_views["district"] == d]
            buckets = sub.groupby((sub["created_at"].dt.hour // 6)).size()
            for ci in range(4):
                heat_rows.append(
                    m.AnalyticsHeat(grid_row=ri, grid_col=ci, value=float(buckets.get(ci, 0)))
                )
        rows_written += _replace(db, m.AnalyticsHeat, today, heat_rows)

        # ---- 概览 KPI ----
        total_views = int(len(views))
        avg_spots = float(views[views["target_type"] == "spot"].groupby("user_id").size().mean() or 0)
        hot_name = ranking_rows[0].name if ranking_rows else ""
        satisfaction = round(float(spots["score"].mean() or 0) / 5 * 100, 1)
        mid = max(1, len(monthly) // 2)
        prev, cur = float(monthly.iloc[:mid].sum() or 1), float(monthly.iloc[mid:].sum())
        delta = f"{(cur - prev) / prev * 100:+.1f}%"
        overview_rows = [
            m.AnalyticsOverview(metric_key="visitors", label="累计客流", value=str(total_views), unit="人次", delta=delta, trend="up" if cur >= prev else "down"),
            m.AnalyticsOverview(metric_key="avgStay", label="人均浏览景点", value=f"{avg_spots:.1f}", unit="个", delta="", trend="flat"),
            m.AnalyticsOverview(metric_key="hotSpot", label="最热景点", value=hot_name, unit="", delta="", trend="up"),
            m.AnalyticsOverview(metric_key="satisfaction", label="景点口碑", value=str(satisfaction), unit="%", delta="", trend="flat"),
        ]
        rows_written += _replace(db, m.AnalyticsOverview, today, overview_rows)

        # ---- 预测（XGBoost / 线性回归） ----
        series = [float(v) for v in monthly.tolist()]
        forecast = _fit_predict(series, steps=2) if len(series) >= 2 else [series[-1] * 1.1 if series else 0.0]
        peak_value = max(forecast) if forecast else 0.0
        prediction_rows = [
            m.AnalyticsPrediction(
                model_name=MODEL_NAME, label="未来 30 日客流预测",
                value=f"峰值 {peak_value:.0f} 人次",
                advice="建议按峰值提前增开运力与讲解场次", confidence=0.7500,
            ),
            m.AnalyticsPrediction(
                model_name=MODEL_NAME, label="推荐加码景区",
                value=hot_name or "梵净山", advice="浏览热度领先，建议加大曝光", confidence=0.7000,
            ),
        ]
        rows_written += _replace(db, m.AnalyticsPrediction, today, prediction_rows)

        task.status = "success"
        task.rows_written = rows_written
        task.message = f"写入 {rows_written} 行聚合结果"
        task.finished_at = datetime.now()
        db.commit()
        return {"status": "success", "rows_written": rows_written, "message": task.message}
    except Exception as exc:  # 失败也要落任务记录，便于排查
        db.rollback()
        task.status = "failed"
        task.message = str(exc)[:500]
        task.finished_at = datetime.now()
        db.commit()
        return {"status": "failed", "rows_written": 0, "message": task.message}
