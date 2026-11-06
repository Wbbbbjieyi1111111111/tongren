# Python 数据分析模块接入指南

> 目标：你在 Python 侧实现「客流趋势 / 区县分布 / 品类占比 / 景点排行 / 季节指数 /
> 热力网格 / 客流预测」，把结果写进 MySQL 的 `t_analytics_*` 表；
> 小程序的 `/api/v1/analytics/*` 接口把这些表读出来返回，前端即可无缝切换。

---

## 1. 建议的目录结构

```
backend/
├── app.py                    # FastAPI / Flask 入口，挂载 /api/v1 路由
├── config.py                 # 数据库连接、路径、常量
├── requirements.txt
├── db/
│   ├── schema.sql            # 直接用小程序 docs/schema.sql
│   └── seed/                 # 从 common/mock 导出的种子 JSON
├── models/                   # SQLAlchemy 模型
│   ├── spot.py  route.py  culture.py  user.py  analytics.py
├── api/                      # 路由层（薄，只查表拼 JSON）
│   ├── content.py            # /spots /routes /foods ...
│   └── analytics.py          # /analytics/*
├── analytics/                # ★ 你的分析代码
│   ├── loader.py             # 从 MySQL 读原始行为数据
│   ├── features.py           # 特征工程
│   ├── models/               # 预测模型（sklearn / xgboost）
│   ├── pipelines/            # 每张 t_analytics_* 表一个 pipeline
│   │   ├── overview.py  trend.py  district.py  category.py
│   │   ├── ranking.py  season.py  heat.py  prediction.py
│   └── run_all.py            # 定时任务入口
├── scheduler/
│   └── cron.py               # APScheduler：每日 02:00 跑 run_all.py
└── tests/
```

---

## 2. 依赖

```txt
# requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
pymysql==1.1.1
cryptography==42.0.8        # MySQL 8 caching_sha2_password 需要
pandas==2.2.2
numpy==1.26.4
scikit-learn==1.5.1
joblib==1.4.2
apscheduler==3.10.4
pydantic==2.8.2
```

> 用 Flask 也行，把 `FastAPI` 换成 `flask` + `flask-cors` 即可，路由层写法改成蓝图。

---

## 3. 数据库连接

```python
# backend/config.py
import os
from sqlalchemy import create_engine

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PWD  = os.getenv("DB_PWD", "your_password")
DB_NAME = os.getenv("DB_NAME", "tongren")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4",
    pool_pre_ping=True, pool_recycle=3600, pool_size=10, max_overflow=20,
    future=True,
)
```

---

## 4. 数据来源

| 事实表 | 内容 | 典型分析 |
|---|---|---|
| `t_user_log` | 前端埋点（`page_view` / `spot_view` / `search` / `favorite` / `trip_generate`） | 客流趋势、热力、排行、搜索热度 |
| `t_user_favorite` | 收藏行为 | 景点偏好、品类占比 |
| `t_user_trip` | 用户生成的自定义行程 | 路线组合分析、停留时长预测 |
| `t_spot` / `t_route` / `t_spot_image` … | 维度表（维度 join 用） | 区县、品类、季节标签 |

> **务必先让前端埋点落库**（`app.track()` → `POST /api/v1/user/log` → `t_user_log`）。
> 只靠静态内容无法算出「客流」。

---

## 5. 一条完整的分析 pipeline 示例

以「区县分布」为例，其余 pipeline 同构。

```python
# backend/analytics/loader.py
import pandas as pd
from sqlalchemy import text
from config import engine

def load_logs(start: str, end: str) -> pd.DataFrame:
    sql = text("""
        SELECT created_at, user_id, event, target_type, target_id, keyword, page, channel
        FROM   t_user_log
        WHERE  created_at >= :start AND created_at < :end
    """)
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params={"start": start, "end": end},
                         parse_dates=["created_at"])
    return df

def load_spots() -> pd.DataFrame:
    sql = text("SELECT id, name, district, cat, level, score FROM t_spot WHERE status = 1")
    with engine.connect() as conn:
        return pd.read_sql(sql, conn)
```

```python
# backend/analytics/pipelines/district.py
import pandas as pd
from sqlalchemy import text
from config import engine
from analytics.loader import load_logs, load_spots

STAT_DATE = "2026-05-20"

def run(start: str, end: str) -> int:
    logs = load_logs(start, end)
    spots = load_spots()

    # 1) 景点浏览 → 区县
    view = logs[logs["event"] == "spot_view"].merge(
        spots[["id", "district"]], left_on="target_id", right_on="id", how="inner"
    )
    # 每个用户对同一景点只计一次，避免刷量
    dist = (view.groupby("district")
                .apply(lambda g: g["user_id"].nunique())
                .sort_values(ascending=False))

    # 2) 写回（先删当天再插，保证幂等）
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM t_analytics_district WHERE stat_date = :d"),
                     {"d": STAT_DATE})
        for district, value in dist.items():
            conn.execute(text("""
                INSERT INTO t_analytics_district (stat_date, district, value, unit)
                VALUES (:d, :district, :value, '万人次')
            """), {"d": STAT_DATE, "district": district, "value": float(value)})
    return len(dist)
```

```python
# backend/analytics/run_all.py
from datetime import datetime, timedelta
from analytics.pipelines import overview, trend, district, category, \
                              ranking, season, heat, prediction

def main():
    end = datetime.now()
    start = end - timedelta(days=365)
    s, e = start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")

    tasks = [overview, trend, district, category, ranking, season, heat, prediction]
    for t in tasks:
        try:
            n = t.run(s, e)
            print(f"[OK]   {t.__name__}: {n} rows")
        except Exception as ex:
            print(f"[FAIL] {t.__name__}: {ex}")
            raise

if __name__ == "__main__":
    main()
```

---

## 6. 客流预测模型（`pipelines/prediction.py`）

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

def features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["month"]  = df["date"].dt.month
    df["weekday"]= df["date"].dt.weekday
    df["is_holiday"] = df["date"].dt.strftime("%m-%d").isin(HOLIDAYS).astype(int)
    # 滞后特征
    for lag in (1, 7, 30):
        df[f"lag_{lag}"] = df["visitors"].shift(lag)
    df["ma7"]  = df["visitors"].rolling(7).mean()
    df["ma30"] = df["visitors"].rolling(30).mean()
    return df.dropna()

def run(start: str, end: str) -> int:
    daily = daily_visitors(start, end)      # date, visitors
    feat  = features(daily)
    X, y = feat.drop(columns=["date", "visitors"]), feat["visitors"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, shuffle=False)

    model = GradientBoostingRegressor(random_state=42).fit(Xtr, ytr)
    mae   = mean_absolute_error(yte, model.predict(Xte))

    # 未来 30 天递归预测
    future = make_future_frame(daily, 30)
    pred   = model.predict(future[X.columns])

    rows = [
        ("未来 30 日客流预测", f"峰值 {pred.max():.0f} 万人次",
         f"模型 MAE={mae:.1f}，建议按峰值 1.2 倍预留运力"),
        ("推荐加码景区", pick_hot_spot(model, daily),
         "搜索热度环比上升，建议增加投放"),
    ]
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM t_analytics_prediction WHERE stat_date=:d"),
                     {"d": STAT_DATE})
        for label, value, advice in rows:
            conn.execute(text("""
                INSERT INTO t_analytics_prediction
                    (stat_date, model_name, label, value, advice, confidence)
                VALUES (:d, 'gbdt_visitors', :l, :v, :a, :c)
            """), {"d": STAT_DATE, "l": label, "v": value, "a": advice, "c": 1 - mae / 100})
    return len(rows)
```

---

## 7. API 层：把表读出来返回给小程序

```python
# backend/api/analytics.py
from fastapi import APIRouter, Query
from sqlalchemy import text
from config import engine

router = APIRouter(prefix="/analytics")

def _rows(sql: str, **params):
    with engine.connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), params).mappings()]

@router.get("/all")
def analytics_all(startDate: str | None = None, endDate: str | None = None):
    return {
        "updatedAt": _last_updated(),
        "source": "python-analysis",
        "overview":  {"list": _rows("SELECT metric_key AS `key`, label, value, unit, delta, trend "
                                    "FROM t_analytics_overview WHERE stat_date=(SELECT MAX(stat_date) FROM t_analytics_overview)")},
        "trend":     {"list": _rows("SELECT label, value FROM t_analytics_trend "
                                    "WHERE stat_date=(SELECT MAX(stat_date) FROM t_analytics_trend) ORDER BY id"),
                      "unit": "万人次"},
        "district":  {"list": _rows("SELECT district AS label, value FROM t_analytics_district "
                                    "WHERE stat_date=(SELECT MAX(stat_date) FROM t_analytics_district)"),
                      "unit": "万人次"},
        "category":  {"list": _rows("SELECT category AS label, value FROM t_analytics_category "
                                    "WHERE stat_date=(SELECT MAX(stat_date) FROM t_analytics_category)"),
                      "unit": "%"},
        "ranking":   {"list": _rows("SELECT rank, name, score, visitors FROM t_analytics_ranking "
                                    "WHERE stat_date=(SELECT MAX(stat_date) FROM t_analytics_ranking) ORDER BY rank")},
        "season":    {"list": _rows("SELECT season AS label, value, note FROM t_analytics_season "
                                    "WHERE stat_date=(SELECT MAX(stat_date) FROM t_analytics_season)"),
                      "unit": "指数"},
        "heat":      {"list": _rows("SELECT grid_row AS `row`, grid_col AS col, value FROM t_analytics_heat "
                                    "WHERE stat_date=(SELECT MAX(stat_date) FROM t_analytics_heat)"),
                      "rows": 4, "cols": 4},
        "prediction":{"list": _rows("SELECT label, value, advice FROM t_analytics_prediction "
                                    "WHERE stat_date=(SELECT MAX(stat_date) FROM t_analytics_prediction)")},
    }
```

> 返回结构必须与前端 `common/api.js` 里 `getMockAnalytics()` **完全一致**，
> 前端 `pages/data/data` 就不用改一行代码。

---

## 8. 定时调度

```python
# backend/scheduler/cron.py
from apscheduler.schedulers.blocking import BlockingScheduler
from analytics.run_all import main

if __name__ == "__main__":
    BlockingScheduler(timezone="Asia/Shanghai").add_job(
        main, "cron", hour=2, minute=30, id="daily-analysis", replace_existing=True
    ).start()
```

或直接用系统 cron：

```bash
30 2 * * * cd /opt/tongren/backend && /usr/bin/python3 -m analytics.run_all >> /var/log/tongren-analysis.log 2>&1
```

---

## 9. 联调自检清单

- [ ] `GET /api/v1/analytics/all` 返回 `{"code":0,"data":{...}}`，且 `data.overview.list` 有 4 条。
- [ ] `data.trend.list` 的 `label` 是「1月」「2月」这种前端能直接显示的文案。
- [ ] `data.ranking.list[].name` 是景点中文名，前端直接显示。
- [ ] `data.heat.rows / cols` 与 `list` 长度匹配（4×4 = 16 条）。
- [ ] `data.updatedAt` 是可读时间字符串。
- [ ] 小程序 `common/config.js` 的 `mode` 改成 `'api'`、`baseUrl` 指向服务后，
      数据分析页的 KPI / 折线 / 环形 / 排行 / 预测全部有值。

---

## 10. 常见坑

| 现象 | 原因 | 处理 |
|---|---|---|
| 中文乱码 | 连接字符集不是 utf8mb4 | 连接串加 `?charset=utf8mb4`，建库也用 utf8mb4 |
| `Access denied`（MySQL 8） | caching_sha2 认证 | 装 `cryptography` 或把账号改成 `mysql_native_password` |
| 前端一直显示占位 | `mode` 还是 `mock` 或 `code` 不是 0 | 改 `mode`，检查响应体 `code===0` |
| `t_user_log` 为空 | 前端埋点没上报 | 确认 `app.track()` 已调用且 `/user/log` 接口存在 |
| 预测值与实际差很大 | 滞后特征泄露 | 训练集/测试集必须 `shuffle=False` 按时间切分 |
