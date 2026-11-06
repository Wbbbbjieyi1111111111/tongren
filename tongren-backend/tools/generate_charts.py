"""
用 pandas + matplotlib 从 t_user_log 生成 3 张真实分析图表，保存到 static/charts/

生成内容：
  1. ranking.png    —— 景点热度排行（横向条形图，Top 10）
  2. trend.png      —— 游客访问趋势（折线图，近 30 天）
  3. category.png   —— 游客偏好统计（饼图，景点品类占比）

用法：
  python tools/generate_charts.py
"""
import os
import sys
from datetime import date, timedelta

import matplotlib
matplotlib.use("Agg")  # 无头模式
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
from sqlalchemy import select

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal, engine
from app import models as m

# ---- 中文字体：Windows 上优先用微软雅黑 / 黑体 ----
def _setup_chinese_font():
    candidates = ["Microsoft YaHei", "SimHei", "STHeiti", "PingFang SC"]
    available = {f.name for f in fm.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams["font.sans-serif"] = [name]
            break
    plt.rcParams["axes.unicode_minus"] = False

_setup_chinese_font()

# 项目配色（抹茶色系，与小程序一致）
C_GREEN_DARK = "#3A5B42"
C_GREEN = "#6B966F"
C_GREEN_LIGHT = "#A9C9A0"
C_SAND = "#D9C9A8"
C_BG = "#F7F7F0"
C_TEXT = "#2C3A2E"

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "charts")
os.makedirs(OUT_DIR, exist_ok=True)


def chart_ranking(db):
    """景点热度排行：按浏览量 Top 10"""
    logs = pd.read_sql(
        select(m.UserLog.event, m.UserLog.target_type, m.UserLog.target_id),
        db.bind,
    )
    spots = pd.read_sql(
        select(m.Spot.id, m.Spot.name, m.Spot.cat, m.Spot.district),
        db.bind,
    )
    views = logs[logs["target_type"] == "spot"]
    if views.empty:
        _save_empty("ranking.png", "暂无访问数据")
        return
    merged = views.merge(spots, left_on="target_id", right_on="id", how="left")
    top = merged.groupby("name").size().sort_values(ascending=True).tail(10)

    fig, ax = plt.subplots(figsize=(8, 5), dpi=120)
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    bars = ax.barh(top.index, top.values, color=C_GREEN, edgecolor="none", height=0.6)
    # 数值标签
    for bar, val in zip(bars, top.values):
        ax.text(bar.get_width() + max(top.values) * 0.01, bar.get_y() + bar.get_height() / 2,
                str(int(val)), va="center", fontsize=11, color=C_TEXT)
    ax.set_title("景点热度排行 Top 10", fontsize=16, fontweight="bold", color=C_GREEN_DARK, pad=15)
    ax.set_xlabel("浏览量（人次）", fontsize=12, color=C_TEXT)
    ax.tick_params(axis="y", labelsize=11, colors=C_TEXT)
    ax.tick_params(axis="x", labelsize=10, colors=C_TEXT)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "ranking.png"), bbox_inches="tight", facecolor=C_BG)
    plt.close()
    print(f"  [OK] ranking.png  Top1={top.index[-1]}({int(top.values[-1])}次)")


def chart_trend(db):
    """游客访问趋势：近 30 天每日访问量折线图"""
    logs = pd.read_sql(
        select(m.UserLog.event, m.UserLog.created_at),
        db.bind,
    )
    if logs.empty:
        _save_empty("trend.png", "暂无访问数据")
        return
    logs["created_at"] = pd.to_datetime(logs["created_at"])
    logs["date"] = logs["created_at"].dt.date
    start = date.today() - timedelta(days=29)
    daily = logs[logs["date"] >= start].groupby("date").size()
    # 补齐缺失日期
    full_range = pd.date_range(start, date.today(), freq="D")
    daily = daily.reindex(full_range.date, fill_value=0)

    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=120)
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.plot(daily.index, daily.values, color=C_GREEN, linewidth=2.5, marker="o",
            markersize=4, markerfacecolor="white", markeredgewidth=1.5)
    ax.fill_between(daily.index, daily.values, alpha=0.15, color=C_GREEN)
    ax.set_title("近 30 天游客访问趋势", fontsize=16, fontweight="bold", color=C_GREEN_DARK, pad=15)
    ax.set_ylabel("访问量（人次）", fontsize=12, color=C_TEXT)
    ax.tick_params(axis="both", labelsize=10, colors=C_TEXT)
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter("%m-%d"))
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "trend.png"), bbox_inches="tight", facecolor=C_BG)
    plt.close()
    print(f"  [OK] trend.png  近30天总访问={int(daily.sum())}人次")


def chart_category(db):
    """游客偏好统计：景点品类占比饼图"""
    logs = pd.read_sql(
        select(m.UserLog.event, m.UserLog.target_type, m.UserLog.target_id),
        db.bind,
    )
    spots = pd.read_sql(
        select(m.Spot.id, m.Spot.cat),
        db.bind,
    )
    views = logs[logs["target_type"] == "spot"]
    if views.empty:
        _save_empty("category.png", "暂无访问数据")
        return
    merged = views.merge(spots, left_on="target_id", right_on="id", how="left")
    cat = merged.groupby("cat").size().sort_values(ascending=False)

    colors = [C_GREEN_DARK, C_GREEN, C_GREEN_LIGHT, C_SAND, "#B7B2A6"]
    fig, ax = plt.subplots(figsize=(7, 7), dpi=120)
    fig.patch.set_facecolor(C_BG)
    wedges, texts, autotexts = ax.pie(
        cat.values, labels=cat.index, autopct="%1.1f%%",
        colors=colors[:len(cat)], startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 12, "color": C_TEXT}
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
    ax.set_title("游客偏好统计（景点品类占比）", fontsize=16, fontweight="bold", color=C_GREEN_DARK, pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "category.png"), bbox_inches="tight", facecolor=C_BG)
    plt.close()
    print(f"  [OK] category.png  品类数={len(cat)}")


def _save_empty(name, msg):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.text(0.5, 0.5, msg, ha="center", va="center", fontsize=16, color=C_GREEN)
    ax.axis("off")
    plt.savefig(os.path.join(OUT_DIR, name), bbox_inches="tight", facecolor=C_BG)
    plt.close()


def main():
    print("=" * 60)
    print(" 数据分析图表生成 · pandas + matplotlib")
    print("=" * 60)
    db = SessionLocal()
    try:
        chart_ranking(db)
        chart_trend(db)
        chart_category(db)
    finally:
        db.close()
    print()
    print(f"图表已保存到: {OUT_DIR}")
    print("访问地址: http://127.0.0.1:8000/static/charts/{ranking,trend,category}.png")


if __name__ == "__main__":
    main()
