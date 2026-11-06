"""
全局配置 —— 读取环境变量 / .env
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录（tongren-backend/）
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


class Settings:
    # MySQL
    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = _int("DB_PORT", 3306)
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "tongren")

    # 安全
    SECRET_KEY: str = os.getenv("SECRET_KEY", "tongren-dev-secret")
    TOKEN_EXPIRE_DAYS: int = _int("TOKEN_EXPIRE_DAYS", 30)

    # 启动建表
    AUTO_CREATE_TABLES: bool = os.getenv("AUTO_CREATE_TABLES", "1") == "1"

    # 分析 pipeline 定时任务
    ANALYTICS_SCHEDULER_ON: bool = os.getenv("ANALYTICS_SCHEDULER_ON", "1") == "1"
    ANALYTICS_CRON_HOUR: int = _int("ANALYTICS_CRON_HOUR", 3)
    ANALYTICS_CRON_MINUTE: int = _int("ANALYTICS_CRON_MINUTE", 30)

    # AI 管家「咪噜」：DeepSeek / 小米 MiMo
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    XIAOMI_API_KEY: str = os.getenv("XIAOMI_API_KEY", "")
    XIAOMI_BASE_URL: str = os.getenv("XIAOMI_BASE_URL", "https://api.xiaomimimo.com/v1")
    XIAOMI_MODEL: str = os.getenv("XIAOMI_MODEL", "mimo-v2.6-pro")

    @property
    def db_url(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )


settings = Settings()
