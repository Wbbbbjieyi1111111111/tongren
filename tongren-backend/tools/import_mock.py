#!/usr/bin/env python3
"""
把小程序 mock 种子数据同步到后端

  python tools/import_mock.py --sql   重新生成 sql/seed.json + sql/init_data.sql（需 node）
  python tools/import_mock.py --db    把 sql/seed.json 灌进 MySQL（读取 .env 连接配置）

数据源：tongren-miniapp/common/mock/{spots,routes,culture}.js + common/config.js
分析基线：与前端 common/api.js 的 getMockAnalytics() 占位数据一致，
         保证「分析 pipeline 未跑批」时 /analytics/* 也有可展示数据。
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MINIAPP = ROOT.parent / "tongren-miniapp"
SQL_DIR = ROOT / "sql"
SEED_PATH = SQL_DIR / "seed.json"

STAT_DATE = "2026-05-20"

# 与前端 mock 基线一致（api.js getMockAnalytics）
ANALYTICS_BASELINE = {
    "overview": [
        {"metric_key": "visitors", "label": "年游客量", "value": "1286", "unit": "万人次", "delta": "+12.4%", "trend": "up"},
        {"metric_key": "avgStay", "label": "平均停留", "value": "2.8", "unit": "天", "delta": "+0.3", "trend": "up"},
        {"metric_key": "hotSpot", "label": "最热景点", "value": "梵净山", "unit": "", "delta": "+18.6%", "trend": "up"},
        {"metric_key": "satisfaction", "label": "游客满意度", "value": "96.2", "unit": "%", "delta": "+1.8", "trend": "up"},
    ],
    "trend": [
        {"label": "1月", "value": 62}, {"label": "2月", "value": 78}, {"label": "3月", "value": 88},
        {"label": "4月", "value": 104}, {"label": "5月", "value": 128}, {"label": "6月", "value": 116},
        {"label": "7月", "value": 142}, {"label": "8月", "value": 151}, {"label": "9月", "value": 119},
        {"label": "10月", "value": 96}, {"label": "11月", "value": 74}, {"label": "12月", "value": 88},
    ],
    "trend_unit": "万人次",
    "district": [
        {"label": "梵净山", "value": 318}, {"label": "江口县", "value": 262},
        {"label": "石阡县", "value": 176}, {"label": "玉屏县", "value": 154},
        {"label": "万山区", "value": 121}, {"label": "德江县", "value": 96},
        {"label": "沿河县", "value": 88}, {"label": "思南县", "value": 71},
    ],
    "district_unit": "万人次",
    "category": [
        {"label": "自然风光", "value": 38}, {"label": "民族村寨", "value": 24},
        {"label": "温泉康养", "value": 18}, {"label": "古镇人文", "value": 12},
        {"label": "美食街区", "value": 8},
    ],
    "category_unit": "%",
    "ranking": [
        {"rank": 1, "name": "梵净山", "score": 4.9, "visitors": 318},
        {"rank": 2, "name": "中南门古城", "score": 4.8, "visitors": 262},
        {"rank": 3, "name": "苗王城", "score": 4.7, "visitors": 218},
        {"rank": 4, "name": "石阡温泉", "score": 4.6, "visitors": 176},
        {"rank": 5, "name": "亚木沟", "score": 4.6, "visitors": 154},
    ],
    "season": [
        {"label": "春", "value": 78, "note": "杜鹃花期"}, {"label": "夏", "value": 95, "note": "避暑旺季"},
        {"label": "秋", "value": 88, "note": "彩林最佳"}, {"label": "冬", "value": 46, "note": "雪景温泉"},
    ],
    "season_unit": "指数",
    "heat": [
        {"row": 0, "col": 0, "value": 12}, {"row": 0, "col": 1, "value": 26},
        {"row": 0, "col": 2, "value": 38}, {"row": 0, "col": 3, "value": 31},
        {"row": 1, "col": 0, "value": 18}, {"row": 1, "col": 1, "value": 44},
        {"row": 1, "col": 2, "value": 92}, {"row": 1, "col": 3, "value": 57},
        {"row": 2, "col": 0, "value": 9}, {"row": 2, "col": 1, "value": 33},
        {"row": 2, "col": 2, "value": 76}, {"row": 2, "col": 3, "value": 41},
        {"row": 3, "col": 0, "value": 7}, {"row": 3, "col": 1, "value": 21},
        {"row": 3, "col": 2, "value": 48}, {"row": 3, "col": 3, "value": 22},
    ],
    "prediction": [
        {"label": "未来 30 日客流预测", "value": "峰值 151 万人次", "advice": "7 月中旬建议增开 2 条运力"},
        {"label": "推荐加码景区", "value": "亚木沟 · 石阡温泉", "advice": "搜索热度环比 +26%"},
        {"label": "淡季营销建议", "value": "11 月 — 12 月", "advice": "温泉 + 雪景主题投放"},
    ],
}


# ---------------------------------------------------------------- 提取

def extract_mock() -> dict:
    """调 node 从 mock JS 提取数据"""
    script = ROOT / "tools" / "extract_mock.js"
    proc = subprocess.run(
        ["node", str(script), str(MINIAPP)],
        capture_output=True, text=True, encoding="utf-8", check=True,
    )
    return json.loads(proc.stdout)


# ---------------------------------------------------------------- SQL 生成

def sql_str(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"


def sql_json(value) -> str:
    return "CAST('" + json.dumps(value, ensure_ascii=False).replace("\\", "\\\\").replace("'", "''") + "' AS JSON)"


def insert_sql(table: str, columns: list[str], rows: list[list], json_cols: set[str] | None = None) -> str:
    if not rows:
        return ""
    json_cols = json_cols or set()
    values = []
    for row in rows:
        cells = [
            sql_json(v) if c in json_cols else sql_str(v)
            for c, v in zip(columns, row)
        ]
        values.append("(" + ", ".join(cells) + ")")
    cols = ", ".join(f"`{c}`" for c in columns)
    return f"INSERT INTO `{table}` ({cols}) VALUES\n  " + ",\n  ".join(values) + ";\n"


def build_sql(seed: dict) -> str:
    out = [
        "-- ============================================================================",
        "--  大美铜仁 · 初始化数据（由 tools/import_mock.py 从 common/mock 生成）",
        "--  用法：mysql -u root -p tongren < sql/init_data.sql",
        "--  重复执行安全：内容表先 DELETE 再 INSERT（幂等重建）",
        "-- ============================================================================",
        "",
        "USE `tongren`;",
        "SET NAMES utf8mb4;",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "",
    ]

    # ---------- 内容主数据（先清子表再清主表） ----------
    out.append("-- ---------- 内容主数据 ----------")
    for table in ("t_spot_image", "t_spot", "t_route_plan_item", "t_route_plan",
                  "t_route_stay", "t_route_avoid", "t_route_spot", "t_route",
                  "t_food", "t_folk", "t_festival", "t_ethnic", "t_season",
                  "t_banner", "t_notice"):
        out.append(f"DELETE FROM `{table}`;")

    spots = seed["spots"]
    out.append(insert_sql(
        "t_spot",
        ["id", "name", "level", "cat", "district", "score", "brief", "slogan", "img",
         "ticket", "open", "traffic", "duration", "intro", "tips", "foods", "sort"],
        [[s["id"], s["name"], s.get("level", ""), s.get("cat", ""), s.get("district", ""),
          s.get("score", 0), s.get("brief", ""), s.get("slogan", ""), s.get("img", ""),
          s.get("ticket", ""), s.get("open", ""), s.get("traffic", ""), s.get("duration", ""),
          s.get("intro", []), s.get("tips", []), s.get("foods", []), s["id"]] for s in spots],
        json_cols={"intro", "tips", "foods"},
    ))
    image_rows = []
    for s in spots:
        for i, file in enumerate(s.get("images") or []):
            image_rows.append([s["id"], file, i])
    out.append(insert_sql("t_spot_image", ["spot_id", "file", "sort"], image_rows))

    routes = seed["routes"]
    out.append(insert_sql(
        "t_route",
        ["id", "name", "days", "suitable", "suit_short", "difficulty", "overview",
         "foods", "tip", "cover", "sort"],
        [[r["id"], r["name"], r.get("days", 1), r.get("suitable", ""), r.get("suitShort", ""),
          r.get("difficulty", ""), r.get("overview", ""), r.get("foods", ""), r.get("tip", ""),
          r.get("cover", ""), r["id"]] for r in routes],
    ))
    plan_rows, item_rows, stay_rows, avoid_rows, link_rows = [], [], [], [], []
    plan_seq = 0
    for r in routes:
        for di, day in enumerate(r.get("plan") or [], start=1):
            plan_seq += 1
            plan_rows.append([plan_seq, r["id"], di, day.get("day", f"Day {di}"), day.get("title", "")])
            for si, it in enumerate(day.get("items") or []):
                item_rows.append([plan_seq, it.get("time", ""), it.get("name", ""), it.get("desc", ""), si])
        for si, stay in enumerate(r.get("stays") or []):
            stay_rows.append([r["id"], stay.get("name", ""), stay.get("type", ""),
                              stay.get("price", ""), stay.get("desc", ""), si])
        for si, avoid in enumerate(r.get("avoid") or []):
            avoid_rows.append([r["id"], avoid, si])
        for si, sid in enumerate(r.get("spotIds") or []):
            link_rows.append([r["id"], sid, si])
    out.append(insert_sql("t_route_plan", ["id", "route_id", "day_index", "day_label", "title"], plan_rows))
    out.append(insert_sql("t_route_plan_item", ["plan_id", "time", "name", "desc", "sort"], item_rows))
    out.append(insert_sql("t_route_stay", ["route_id", "name", "type", "price", "desc", "sort"], stay_rows))
    out.append(insert_sql("t_route_avoid", ["route_id", "content", "sort"], avoid_rows))
    out.append(insert_sql("t_route_spot", ["route_id", "spot_id", "sort"], link_rows))

    out.append(insert_sql("t_food", ["name", "tag", "file", "desc", "sort"],
                          [[x["name"], x.get("tag", ""), x.get("file", ""), x.get("desc", ""), i]
                           for i, x in enumerate(seed["foods"])]))
    out.append(insert_sql("t_folk", ["name", "level", "desc", "sort"],
                          [[x["name"], x.get("level", ""), x.get("desc", ""), i]
                           for i, x in enumerate(seed["folk"])]))
    out.append(insert_sql("t_festival", ["month", "day", "name", "place", "desc", "sort"],
                          [[x.get("month", ""), x.get("day", ""), x["name"], x.get("place", ""), x.get("desc", ""), i]
                           for i, x in enumerate(seed["festivals"])]))
    out.append(insert_sql("t_ethnic", ["name", "keys", "desc", "file", "mono", "sort"],
                          [[x["name"], x.get("keys", ""), x.get("desc", ""), x.get("file", ""),
                            1 if x.get("mono") else 0, i]
                           for i, x in enumerate(seed["ethnic"])]))
    out.append(insert_sql("t_season", ["name", "months", "temp", "note", "icon", "sort"],
                          [[x["name"], x.get("months", ""), x.get("temp", ""), x.get("note", ""),
                            x.get("icon", "leaf"), i]
                           for i, x in enumerate(seed["seasons"])]))
    out.append(insert_sql("t_banner", ["id", "file", "eyebrow", "title", "meta", "link_type", "link_id", "sort"],
                          [[x["id"], x.get("file", ""), x.get("eyebrow", ""), x.get("title", ""),
                            x.get("meta", ""), "spot", x["id"], x["id"]]
                           for x in seed["banners"]]))
    out.append(insert_sql("t_notice", ["id", "title", "content", "publish_date", "sort"],
                          [[x["id"], x["title"], x.get("content", x["title"]),
                            x.get("publish_date", "2026-01-01"), x["id"]]
                           for x in seed["notices"]]))

    # ---------- 分析基线（pipeline 未跑批时的占位数据） ----------
    out.append("-- ---------- 分析基线（stat_date = %s） ----------" % STAT_DATE)
    for table in ("t_analytics_overview", "t_analytics_trend", "t_analytics_district",
                  "t_analytics_category", "t_analytics_ranking", "t_analytics_season",
                  "t_analytics_heat", "t_analytics_prediction"):
        out.append(f"DELETE FROM `{table}` WHERE `stat_date` = '{STAT_DATE}';")

    b = ANALYTICS_BASELINE
    out.append(insert_sql(
        "t_analytics_overview",
        ["stat_date", "metric_key", "label", "value", "unit", "delta", "trend"],
        [[STAT_DATE, x["metric_key"], x["label"], x["value"], x["unit"], x["delta"], x["trend"]]
         for x in b["overview"]]))
    out.append(insert_sql(
        "t_analytics_trend", ["stat_date", "period", "label", "value", "unit"],
        [[STAT_DATE, "month", x["label"], x["value"], b["trend_unit"]] for x in b["trend"]]))
    out.append(insert_sql(
        "t_analytics_district", ["stat_date", "district", "value", "unit"],
        [[STAT_DATE, x["label"], x["value"], b["district_unit"]] for x in b["district"]]))
    out.append(insert_sql(
        "t_analytics_category", ["stat_date", "category", "value", "unit"],
        [[STAT_DATE, x["label"], x["value"], b["category_unit"]] for x in b["category"]]))
    out.append(insert_sql(
        "t_analytics_ranking", ["stat_date", "target_type", "target_id", "name", "rank", "score", "visitors"],
        [[STAT_DATE, "spot", 0, x["name"], x["rank"], x["score"], x["visitors"]] for x in b["ranking"]]))
    out.append(insert_sql(
        "t_analytics_season", ["stat_date", "season", "value", "note", "unit"],
        [[STAT_DATE, x["label"], x["value"], x["note"], b["season_unit"]] for x in b["season"]]))
    out.append(insert_sql(
        "t_analytics_heat", ["stat_date", "grid_row", "grid_col", "value"],
        [[STAT_DATE, x["row"], x["col"], x["value"]] for x in b["heat"]]))
    out.append(insert_sql(
        "t_analytics_prediction", ["stat_date", "model_name", "label", "value", "advice", "confidence"],
        [[STAT_DATE, "seed_baseline", x["label"], x["value"], x["advice"], 0.7] for x in b["prediction"]]))

    out.append("SET FOREIGN_KEY_CHECKS = 1;")
    return "\n".join(out)


# ---------------------------------------------------------------- 灌库

def load_seed() -> dict:
    if not SEED_PATH.exists():
        sys.exit(f"种子文件不存在，请先执行 --sql 生成：{SEED_PATH}")
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def insert_db() -> None:
    sys.path.insert(0, str(ROOT))
    import pymysql
    from app.config import settings

    seed = load_seed()
    conn = pymysql.connect(
        host=settings.DB_HOST, port=settings.DB_PORT, user=settings.DB_USER,
        password=settings.DB_PASSWORD, database=settings.DB_NAME, charset="utf8mb4",
    )
    with conn.cursor() as cur:
        for table in ("t_spot_image", "t_spot", "t_route_plan_item", "t_route_plan",
                      "t_route_stay", "t_route_avoid", "t_route_spot", "t_route",
                      "t_food", "t_folk", "t_festival", "t_ethnic", "t_season",
                      "t_banner", "t_notice"):
            cur.execute(f"DELETE FROM `{table}`")
        # 与 init_data.sql 相同口径：直接执行生成的 SQL 语句块最省事
        for statement in build_sql(seed).split(";\n"):
            stmt = "\n".join(
                line for line in statement.splitlines()
                if line.strip() and not line.strip().startswith("--")
                and not line.strip().startswith("USE ")
                and not line.strip().startswith("SET ")
            ).strip()
            if stmt:
                cur.execute(stmt)
    conn.commit()
    conn.close()
    print(f"已导入 MySQL：{settings.DB_NAME}（数据源 {SEED_PATH.name}）")


def main() -> None:
    args = set(sys.argv[1:])
    if "--db" in args:
        insert_db()
        return
    # 默认 --sql
    seed = extract_mock()
    SQL_DIR.mkdir(parents=True, exist_ok=True)
    SEED_PATH.write_text(json.dumps(seed, ensure_ascii=False, indent=1), encoding="utf-8")
    (SQL_DIR / "init_data.sql").write_text(build_sql(seed), encoding="utf-8")
    print(f"已生成：{SEED_PATH}\n已生成：{SQL_DIR / 'init_data.sql'}")


if __name__ == "__main__":
    main()
