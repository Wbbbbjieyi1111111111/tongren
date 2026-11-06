"""
Pydantic 请求体 —— 字段名与 docs/API-CONTRACT.md 完全一致
"""
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class LoginBody(BaseModel):
    phone: str
    password: str


class RegisterBody(BaseModel):
    phone: str
    password: str
    nickname: str = ""


class LogItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    event: str
    target_type: str = Field(default="", alias="targetType")
    target_id: int = Field(default=0, alias="targetId")
    keyword: str = ""
    page: str = ""
    channel: str = ""
    ts: Optional[int] = None


class LogBody(LogItem):
    """POST /user/log —— 单条埋点"""


class LogBatchBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    list: List[LogItem] = Field(default_factory=list)


class FavoriteBody(BaseModel):
    type: str
    targetId: int
    favorite: bool


class TripBody(BaseModel):
    title: str = ""
    days: int = 1
    spotIds: List[int] = Field(default_factory=list)
    plan: Any = None
    source: str = "custom"


class CustomRouteBody(BaseModel):
    spotIds: List[int] = Field(default_factory=list)
    days: int = 0
    title: str = ""
