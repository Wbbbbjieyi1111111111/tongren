"""
AI 管家「咪噜」接口
  POST /ai/chat     对话（DeepSeek / 小米 MiMo，自动降级）
  GET  /ai/prompts  预设提示词

响应体沿用统一约定 {code, message, data}
"""
import json
import logging
import urllib.error
import urllib.request

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..errors import CODE_PARAM, ApiError, ok
from .. import models as m

router = APIRouter(tags=["ai"])
logger = logging.getLogger(__name__)

PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "base_url": lambda: settings.DEEPSEEK_BASE_URL,
        "api_key": lambda: settings.DEEPSEEK_API_KEY,
        "model": lambda: settings.DEEPSEEK_MODEL,
    },
    "xiaomi": {
        "name": "小米 MiMo",
        "base_url": lambda: settings.XIAOMI_BASE_URL,
        "api_key": lambda: settings.XIAOMI_API_KEY,
        "model": lambda: settings.XIAOMI_MODEL,
    },
}

SYSTEM_PROMPT = """你是「咪噜」，贵州铜仁的文旅 AI 小管家，形象是一只抹茶绿色、大眼睛、头顶有小草芽的可爱小精灵。

你的说话风格：
1. 亲切、活泼、有温度，像本地朋友带路，不要官腔。
2. 每次回答都要自然地提到自己的名字「咪噜」，至少一次，例如「咪噜觉得……」「这个咪噜最清楚啦～」。
3. 回答控制在 120 字以内，条理清晰，必要时用短分行列出 2-3 点建议。
4. 遇到不确定的信息要诚实说明，并给出可执行的建议（如提前查官方公告、错峰出行）。
5. 可以使用少量可爱的语气词，但不要滥用表情符号。

你熟悉的铜仁知识：
{district_knowledge}

游客常问：天气适合玩什么、梵净山人多不多、哪条路线好爬、吃什么、怎么去、门票多少。
若问题与铜仁旅游无关，也要友好回应，并自然地把话题引回铜仁旅行。
"""

PRESET_PROMPTS = [
    {"icon": "sun", "text": "铜仁今天天气适合玩什么项目？"},
    {"icon": "mountain", "text": "梵净山今天人多不多？"},
    {"icon": "route", "text": "梵净山哪条路好爬一些？"},
    {"icon": "food", "text": "铜仁必吃的三个小吃是什么？"},
    {"icon": "pin", "text": "第一次来铜仁，两天怎么安排？"},
    {"icon": "star", "text": "带老人小孩去铜仁，推荐哪些景点？"},
]


class ChatMessage(BaseModel):
    role: str = "user"
    content: str = ""


class ChatIn(BaseModel):
    message: str = Field(default="", description="用户当前提问")
    history: list[ChatMessage] = Field(default_factory=list, description="历史对话")
    provider: str = Field(default="auto", description="auto / deepseek / xiaomi")


def _build_knowledge(db: Session) -> str:
    """把库里的景点/路线整理成轻量上下文，避免把整库塞给模型"""
    spots = db.execute(
        select(m.Spot.name, m.Spot.district, m.Spot.cat, m.Spot.level, m.Spot.score)
        .where(m.Spot.status == 1)
        .order_by(m.Spot.sort)
        .limit(30)
    ).all()
    routes = db.execute(
        select(m.Route.name, m.Route.days, m.Route.suitable).limit(15)
    ).all()

    lines = ["【铜仁景点】"]
    for name, district, cat, level, score in spots:
        lines.append(f"- {name}（{district}·{cat}·{level}·评分{score}）")
    lines.append("【热门路线】")
    for name, days, suitable in routes:
        lines.append(f"- {name}（{days}天·适合{suitable}）")
    return "\n".join(lines)


def _call_provider(provider: str, messages: list[dict]) -> str:
    cfg = PROVIDERS[provider]
    base_url = (cfg["base_url"]() or "").rstrip("/")
    api_key = cfg["api_key"]()
    model = cfg["model"]()
    if not api_key:
        raise RuntimeError(f"{cfg['name']} 未配置 API Key")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.75,
        "max_tokens": 900,
        "stream": False,
    }
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    choice = (body.get("choices") or [{}])[0]
    content = (choice.get("message") or {}).get("content", "")
    if not content:
        raise RuntimeError(f"{cfg['name']} 返回空内容")
    return content.strip()


def _local_fallback(message: str) -> str:
    """两个模型都不可用时的兜底回答，保证小程序始终有可用反馈"""
    text = (message or "").strip()
    if any(k in text for k in ("天气", "下雨", "温度")):
        return "咪噜来啦～铜仁山区天气变化快，咪噜建议出发前先看景区官方公告；如果是雨天，咪噜会推荐室内的中南门古城和老街美食，泡温泉也很舒服哦。"
    if "梵净山" in text and any(k in text for k in ("人多", "人多不多", "拥堵", "挤")):
        return "咪噜告诉你：梵净山旺季人多，尤其上午 9 点到 11 点是索道高峰。咪噜建议 8 点前入园，或者选择下午上山，人流会少很多～"
    if "梵净山" in text:
        return "咪噜最爱梵净山啦！咪噜建议走索道上下更省力，想徒步的话留足 6 小时，山上温差大，记得带外套。"
    if any(k in text for k in ("吃", "美食", "小吃")):
        return "咪噜流口水了～铜仁必吃：锅巴粉、江口米豆腐、酸汤牛肉。咪噜建议在市区中南门老街一次吃齐！"
    if any(k in text for k in ("路线", "行程", "两天", "三天")):
        return "咪噜帮你安排：两天可以走「梵净山 + 中南门古城」，三天加一站石阡温泉。咪噜提醒提前订好住宿哦～"
    return "咪噜在呢～这个问题咪噜暂时没查到确切答案，可以先告诉我你想去的景点或天数，咪噜帮你规划铜仁行程！"


@router.get("/ai/prompts")
def get_prompts():
    """预设提示词，供聊天页展示"""
    return ok({"list": PRESET_PROMPTS})


@router.post("/ai/chat")
def chat(body: ChatIn, db: Session = Depends(get_db)):
    message = (body.message or "").strip()
    if not message:
        raise ApiError(CODE_PARAM, "参数错误：message 不能为空")

    # 历史对话（最多保留最近 8 轮，避免过长）
    history = [
        {"role": h.role if h.role in ("user", "assistant") else "user", "content": h.content}
        for h in body.history[-8:]
        if h.content
    ]

    system = SYSTEM_PROMPT.format(district_knowledge=_build_knowledge(db))
    messages = [{"role": "system", "content": system}] + history + [{"role": "user", "content": message}]

    wanted = (body.provider or "auto").lower()
    order = ["deepseek", "xiaomi"] if wanted == "auto" else ([wanted] if wanted in PROVIDERS else ["deepseek", "xiaomi"])

    for provider in order:
        try:
            reply = _call_provider(provider, messages)
            return ok({
                "reply": reply,
                "provider": PROVIDERS[provider]["name"],
                "model": PROVIDERS[provider]["model"](),
            })
        except Exception as exc:  # noqa: BLE001
            logger.warning("咪噜调用 %s 失败: %s", provider, exc)

    return ok({
        "reply": _local_fallback(message),
        "provider": "咪噜本地知识库",
        "model": "offline",
    })
