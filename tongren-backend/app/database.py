"""
SQLAlchemy 2.0 数据库连接与会话
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import settings

engine = create_engine(
    settings.db_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

Base = declarative_base()


def get_db():
    """FastAPI 依赖：每个请求一个会话"""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
