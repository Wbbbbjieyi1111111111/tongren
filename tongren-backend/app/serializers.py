"""
ORM → 契约 JSON 序列化
字段名严格对齐 docs/API-CONTRACT.md，前端零改动直接消费
"""
from . import models as m


def spot_to_json(spot: m.Spot) -> dict:
    return {
        "id": spot.id,
        "name": spot.name,
        "level": spot.level,
        "cat": spot.cat,
        "district": spot.district,
        "score": float(spot.score or 0),
        "brief": spot.brief,
        "slogan": spot.slogan,
        "img": spot.img,
        "images": [img.file for img in spot.images] or ([spot.img] if spot.img else []),
        "ticket": spot.ticket,
        "open": spot.open_,
        "traffic": spot.traffic,
        "duration": spot.duration,
        "intro": spot.intro or [],
        "tips": spot.tips or [],
        "foods": spot.foods or [],
    }


def spot_to_row(spot: m.Spot, spot_type: str = "spot") -> dict:
    """搜索结果行：复用景点对象结构（契约 2.4），追加 type 便于前端分流"""
    return {
        "id": spot.id,
        "name": spot.name,
        "level": spot.level,
        "cat": spot.cat,
        "district": spot.district,
        "score": float(spot.score or 0),
        "brief": spot.brief,
        "img": spot.img,
        "type": spot_type,
    }


def route_to_json(route: m.Route) -> dict:
    return {
        "id": route.id,
        "name": route.name,
        "days": route.days,
        "suitable": route.suitable,
        "suitShort": route.suit_short,
        "difficulty": route.difficulty,
        "overview": route.overview,
        "foods": route.foods,
        "tip": route.tip,
        "cover": route.cover,
        "spotIds": [link.spot_id for link in route.spot_links],
        "plan": [
            {
                "day": plan.day_label,
                "title": plan.title,
                "items": [
                    {"time": item.time_, "name": item.name, "desc": item.desc_}
                    for item in plan.items
                ],
            }
            for plan in route.plans
        ],
        "stays": [
            {"name": s.name, "type": s.type, "price": s.price, "desc": s.desc_}
            for s in route.stays
        ],
        "avoid": [a.content for a in route.avoids],
    }


def food_to_json(row: m.Food) -> dict:
    return {"name": row.name, "tag": row.tag, "file": row.file, "desc": row.desc_}


def folk_to_json(row: m.Folk) -> dict:
    return {"name": row.name, "level": row.level, "desc": row.desc_}


def festival_to_json(row: m.Festival) -> dict:
    return {
        "month": row.month,
        "day": row.day,
        "name": row.name,
        "place": row.place,
        "desc": row.desc_,
    }


def ethnic_to_json(row: m.Ethnic) -> dict:
    return {
        "name": row.name,
        "keys": row.keys_,
        "desc": row.desc_,
        "file": row.file,
        "mono": bool(row.mono),
    }


def season_to_json(row: m.Season) -> dict:
    return {
        "name": row.name,
        "months": row.months,
        "temp": row.temp,
        "note": row.note,
        "icon": row.icon,
    }


def banner_to_json(row: m.Banner) -> dict:
    return {
        "id": row.id,
        "file": row.file,
        "eyebrow": row.eyebrow,
        "title": row.title,
        "meta": row.meta,
    }


def notice_to_json(row: m.Notice) -> dict:
    return {
        "id": row.id,
        "title": row.title,
        "publishedAt": row.publish_date.strftime("%Y-%m-%d") if row.publish_date else "",
    }


def user_to_json(user: m.User) -> dict:
    return {
        "id": user.id,
        "phone": user.phone,
        "nickname": user.nickname,
        "avatar": user.avatar,
    }


def trip_to_json(trip: m.UserTrip) -> dict:
    return {
        "id": trip.id,
        "title": trip.title,
        "days": trip.days,
        "spotIds": trip.spot_ids or [],
        "plan": trip.plan,
        "source": trip.source,
        "createdAt": trip.created_at.strftime("%Y-%m-%d %H:%M") if trip.created_at else "",
    }
