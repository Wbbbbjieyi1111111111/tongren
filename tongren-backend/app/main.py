"""
大美铜仁 · 文旅小程序后端（FastAPI）

启动：
  1. 复制 .env.example 为 .env，改好 MySQL 连接
  2. mysql -u root -p < sql/schema.sql && mysql -u root -p tongren < sql/init_data.sql
  3. pip install -r requirements.txt
  4. uvicorn app.main:app --host 0.0.0.0 --port 8000

联调：把 tongren-miniapp/common/config.js 的 mode 改为 'api'、
      baseUrl 指向 http://127.0.0.1:8000 即可，前端页面零改动。
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, SessionLocal, engine
from .errors import (
    ApiError,
    api_error_handler,
    fail,
    server_error_handler,
    validation_error_handler,
)
from .routers import admin, ai, analytics, content, routes, search, user

logger = logging.getLogger("tongren")


def _start_scheduler():
    """数据分析 pipeline 每日定时跑批（ANALYTICS_SCHEDULER_ON=0 关闭）"""
    if not settings.ANALYTICS_SCHEDULER_ON:
        return None
    try:
        from apscheduler.schedulers.background import BackgroundScheduler

        from . import pipelines

        def job():
            db = SessionLocal()
            try:
                result = pipelines.run_all(db)
                logger.info("scheduled analytics: %s", result)
            finally:
                db.close()

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            job, "cron",
            hour=settings.ANALYTICS_CRON_HOUR,
            minute=settings.ANALYTICS_CRON_MINUTE,
        )
        scheduler.start()
        return scheduler
    except Exception as exc:  # 调度器不可用不影响 API 服务
        logger.warning("analytics scheduler disabled: %s", exc)
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.AUTO_CREATE_TABLES:
        Base.metadata.create_all(engine)
    scheduler = _start_scheduler()
    yield
    if scheduler is not None:
        scheduler.shutdown(wait=False)


app = FastAPI(
    title="大美铜仁 · 小程序后端",
    version="1.0.0",
    description="接口契约见 tongren-miniapp/docs/API-CONTRACT.md",
    lifespan=lifespan,
)

# 开发期允许小程序开发者工具跨域调用；生产请收紧为正式域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 统一异常 → 统一响应体 { code, message, data }
app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, server_error_handler)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info("%s %s -> %s", request.method, request.url.path, response.status_code)
    return response


# 路由汇总：全部业务接口统一 /api/v1 前缀
for router in (content.router, routes.router, search.router, user.router, analytics.router, admin.router, ai.router):
    app.include_router(router, prefix="/api/v1")

# 静态资源：pandas+matplotlib 生成的分析图表
_static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
os.makedirs(os.path.join(_static_dir, "charts"), exist_ok=True)
app.mount("/static", StaticFiles(directory=_static_dir), name="static")


@app.get("/", include_in_schema=False)
def root():
    return {"code": 0, "message": "大美铜仁 · 后端服务运行中", "data": {"docs": "/docs"}}
