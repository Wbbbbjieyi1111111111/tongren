"""
种子数据灌库脚本 —— 确保各表总量 >= 200 条，t_user_log >= 500 条（给 pipelines 做原料）

用法：
  cd tongren-backend
  python -m tools.seed_data
  或
  python tools/seed_data.py
"""
import os
import random
import sys
from datetime import date, datetime, timedelta

# 确保 app 包可导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv  # noqa: E402
load_dotenv()

from app.database import SessionLocal, engine  # noqa: E402
from app import models as m  # noqa: E402
from app.security import hash_password  # noqa: E402

random.seed(42)

DISTRICTS = ["江口县", "碧江区", "松桃县", "石阡县", "万山区", "印江县", "玉屏县", "德江县", "沿河县", "思南县"]
CATS = ["自然风光", "古镇人文", "温泉休闲", "红色景点", "民族村寨"]
LEVELS = ["5A", "4A", "3A"]
IMAGES_POOL = [
    "fanjingshan.jpg", "yamugou.jpg", "taiping-river.jpg", "jinjiang-night.jpg",
    "miaowangcheng.jpg", "shiqian-spring.jpg", "zhaisha.jpg", "yunshe.jpg",
    "zhongnanmen.jpg", "zhusha.jpg", "gelao-festival.jpg", "gelao-festival-mono.jpg",
    "miao-silver.jpg", "tujia-dance.jpg", "fanjingshan.jpg",
]

SPOT_TEMPLATES = [
    # (name, level, cat, district, score, brief, slogan, ticket, open_, traffic, duration, food_tag)
    ("梵净山", "5A", "自然风光", "江口县", 4.9, "世界自然遗产，云海之上的天空之城", "云海翻涌处，山是一尊佛", "旺季 100 元 / 淡季 50 元", "08:00–18:00（旺季）", "铜仁站 → 江口客运站 → 游客中心", "建议 4–6 小时", ["锅巴粉", "江口米豆腐"]),
    ("苗王城", "4A", "民族村寨", "松桃县", 4.7, "保存完好的苗族古寨，被誉为苗家第一城", "千年苗寨，银饰闪光", "80 元", "08:30–17:30", "铜仁 → 松桃大巴 → 苗王城", "建议 3–4 小时", ["松桃卤鸭", "苗家酸汤鱼"]),
    ("石阡温泉", "4A", "温泉休闲", "石阡县", 4.6, "千年温泉古镇，国家级温泉康养基地", "千年温泉，泡去风尘", "温泉票 128 元起", "09:00–23:00", "铜仁 → 石阡大巴 → 温泉度假中心", "建议 半天", ["石阡苔茶", "泉都绿壳蛋"]),
    ("亚木沟", "4A", "自然风光", "江口县", 4.6, "峡谷幽泉，梵净山下的翡翠项链", "深山里的翡翠", "98 元", "08:00–17:00", "江口县 → 亚木沟景区", "建议 3–4 小时", ["江口米豆腐", "豆腐干"]),
    ("中南门古城", "4A", "古镇人文", "碧江区", 4.8, "铜仁市中心保存完好的明清古城街区", "铜仁的城市根脉", "免费", "全天开放", "铜仁市中心步行可达", "建议 2–3 小时", ["锅巴粉", "铜仁豆浆粉"]),
    ("寨沙侗寨", "4A", "民族村寨", "江口县", 4.5, "梵净山下的侗寨，夜色动人", "侗寨夜色，鼓楼欢歌", "免费", "全天开放", "江口县 → 寨沙侗寨", "建议 2–3 小时", ["侗家腊肉", "糯米腌鱼"]),
    ("云舍村", "4A", "民族村寨", "江口县", 4.4, "土家第一村，依山而建的土家寨子", "土家第一村", "免费", "全天开放", "江口县 → 云舍村", "建议 2 小时", ["土家腊肉", "油茶汤"]),
    ("大明边城", "3A", "古镇人文", "碧江区", 4.3, "以明代历史为主题的文化旅游区", "穿越六百年，寻梦大明", "60 元", "08:30–17:30", "铜仁市中心 → 大明边城", "建议 2–3 小时", ["铜仁米粉", "糖麻圆"]),
    ("朱砂古镇", "4A", "古镇人文", "万山区", 4.5, "中国最大的朱砂矿遗址改造而成的景区", "千年朱砂，万山红遍", "90 元", "08:30–17:00", "铜仁 → 万山大巴", "建议 3 小时", ["万山朱砂糕", "刺梨汁"]),
    ("九龙洞", "3A", "自然风光", "碧江区", 4.2, "喀斯特溶洞群，洞内钟乳石千姿百态", "地下龙宫，别有洞天", "70 元", "08:00–17:30", "铜仁 → 九龙洞景区", "建议 2–3 小时", ["铜仁砂锅粉", "炸洋芋"]),
    ("天生桥大峡谷", "3A", "自然风光", "江口县", 4.3, "峡谷幽深，天桥凌空，飞瀑直下", "天生一座桥，飞架大峡谷", "50 元", "08:30–17:00", "江口县 → 天生桥", "建议 2 小时", ["江口米豆腐", "豆腐干"]),
    ("太平河漂流", "3A", "自然风光", "江口县", 4.4, "梵净山下清凉漂流，夏日必选", "夏日清凉，从这里开始", "漂流票 120 元", "09:00–16:00", "江口县 → 太平河漂流起点", "建议 2–3 小时", ["锅巴粉", "凉拌折耳根"]),
]

# 额外景点（扩充到 ~40 条）
EXTRA_SPOT_PATTERNS = [
    # 组合真实铜仁元素生成新景点
    ("梵净山 · 老金顶", "5A", "自然风光", "江口县", 4.8, "梵净山第二高峰，云海日出绝佳观赏点", "金顶日出，万山朝拜", "含在梵净山门票内", "08:00–17:30", "梵净山景区内徒步", "建议 2–3 小时", ["江口米豆腐", "锅巴粉"]),
    ("苗王城 · 平茶苗寨", "3A", "民族村寨", "松桃县", 4.3, "苗王城的姊妹寨，原生态苗族风情", "平茶苗寨，银饰之乡", "60 元", "08:30–17:00", "松桃县 → 平茶苗寨", "建议 2 小时", ["苗家酸汤鱼", "松桃卤鸭"]),
    ("石阡 · 佛顶山", "4A", "自然风光", "石阡县", 4.5, "贵州第二高峰，与梵净山并称姊妹山", "佛顶山巅，云海无际", "80 元", "08:00–17:00", "石阡县 → 佛顶山", "建议 4–5 小时", ["石阡苔茶", "泉都绿壳蛋"]),
    ("万山 · 九丰农业园", "3A", "自然风光", "万山区", 4.1, "现代生态农业观光园，采摘好去处", "九丰农业，四季采摘", "40 元", "08:30–17:30", "铜仁 → 万山九丰", "建议 2 小时", ["万山朱砂糕", "刺梨汁"]),
    ("碧江 · 锦江夜色", "免费", "古镇人文", "碧江区", 4.5, "锦江河畔夜景，中南门古城对岸", "锦江夜色，星光与灯火", "免费", "18:00–23:00", "铜仁市中心锦江两岸", "建议 1–2 小时", ["铜仁豆浆粉", "糖麻圆"]),
    ("江口 · 德旺茶园", "3A", "自然风光", "江口县", 4.0, "梵净山茶核心产区，万亩茶园连绵", "云雾深处，茶香千里", "免费", "08:00–17:00", "江口县德旺乡", "建议 1–2 小时", ["梵净山茶", "江口米豆腐"]),
    ("思南 · 思州石砚博物馆", "3A", "古镇人文", "思南县", 4.2, "中国四大名砚之一思州石砚的主题展馆", "思州石砚，文房瑰宝", "30 元", "08:30–17:00", "思南县博物馆", "建议 1–2 小时", ["思南花甜粑", "酸汤鱼"]),
    ("沿河 · 乌江百里画廊", "4A", "自然风光", "沿河县", 4.6, "乌江中下游最壮美河段，山水如黛", "乌江画廊，百里山水", "船票 150 元", "08:30–17:00", "沿河县乌江码头", "建议 3–4 小时", ["沿河土家酸汤鱼", "糯米糍粑"]),
    ("印江 · 木黄会师纪念馆", "3A", "红色景点", "印江县", 4.3, "红二六军团会师地，贵州重要红色地标", "木黄会师，星火燎原", "免费", "08:30–17:00", "印江县木黄镇", "建议 2 小时", ["印江绿豆粉", "酸汤鱼"]),
    ("德江 · 土家炸龙节广场", "3A", "民族村寨", "德江县", 4.2, "土家炸龙节发源地，节庆文化主题广场", "炸龙狂舞，土家狂欢", "免费", "全天开放", "德江县县城", "建议 1–2 小时", ["土家炸龙宴", "糯米糍粑"]),
    ("玉屏 · 箫笛文化园", "3A", "古镇人文", "玉屏县", 4.3, "中国箫笛之乡，箫笛制作与演奏文化展示", "箫笛声声，玉屏天籁", "40 元", "08:30–17:00", "玉屏县箫笛文化园", "建议 2 小时", ["玉屏箫笛", "侗家腌鱼"]),
    ("松桃 · 寨英古镇", "3A", "古镇人文", "松桃县", 4.2, "明代屯堡要塞，苗汉融合的商贸古镇", "寨英古镇，苗汉交融", "50 元", "08:30–17:30", "松桃县寨英镇", "建议 2 小时", ["松桃卤鸭", "苗家腊肉"]),
    ("江口 · 闵孝河湿地公园", "3A", "自然风光", "江口县", 4.1, "梵净山下的湿地公园，白鹭栖息之地", "闵孝河畔，白鹭翩翩", "免费", "全天开放", "江口县闵孝镇", "建议 1–2 小时", ["锅巴粉", "江口米豆腐"]),
    ("石阡 · 困牛山战斗遗址", "3A", "红色景点", "石阡县", 4.2, "红军困牛山战斗旧址，红色教育基地", "困牛山巅，红军忠魂", "免费", "08:30–17:00", "石阡县龙塘镇困牛山", "建议 2 小时", ["石阡苔茶", "泉都绿壳蛋"]),
    ("万山区 · 朱砂矿洞遗址", "4A", "古镇人文", "万山区", 4.4, "千年朱砂矿开采遗址，洞内奇观", "千年矿洞，朱砂秘境", "含朱砂古镇门票", "08:30–17:00", "万山朱砂古镇内", "建议 2 小时", ["万山朱砂糕", "刺梨汁"]),
    ("碧江区 · 三江公园", "免费", "自然风光", "碧江区", 4.0, "锦江、大江、小江三江汇流处", "三江汇流，铜仁门户", "免费", "全天开放", "铜仁市中心三江公园", "建议 1 小时", ["铜仁豆浆粉", "糖麻圆"]),
    ("江口 · 鱼泉生态园", "3A", "自然风光", "江口县", 4.0, "梵净山麓的生态农庄，亲子采摘", "鱼泉农庄，田园乐趣", "30 元", "08:30–17:30", "江口县鱼泉村", "建议 2 小时", ["干锅鱼", "农家小炒"]),
    ("松桃 · 盘石苗族边防线", "3A", "民族村寨", "松桃县", 4.1, "苗王城后山的苗族边防线遗址", "苗疆长城，边防线关", "40 元", "08:30–17:00", "松桃县盘石镇", "建议 2 小时", ["苗家酸汤鱼", "松桃卤鸭"]),
    ("石阡 · 楼上古寨", "3A", "民族村寨", "石阡县", 4.2, "保存完好的侗族古寨，被誉为侗族文化活化石", "楼上古寨，侗家秘境", "50 元", "08:30–17:00", "石阡县国荣乡楼上村", "建议 2 小时", ["石阡苔茶", "侗家腌鱼"]),
    ("沿河 · 麻阳河黑叶猴保护区", "4A", "自然风光", "沿河县", 4.5, "国家级自然保护区，黑叶猴栖息地", "麻阳河畔，猴群出没", "60 元", "08:00–17:00", "沿河县麻阳河", "建议 3 小时", ["沿河土家酸汤鱼", "糯米糍粑"]),
    ("思南 · 乌江腾龙峡", "3A", "自然风光", "思南县", 4.3, "乌江峡谷风光，腾龙桥横跨天堑", "腾龙桥畔，乌江天险", "80 元", "08:30–17:00", "思南县腾龙峡", "建议 2–3 小时", ["思南花甜粑", "酸汤鱼"]),
    ("德江 · 武陵高山草场", "3A", "自然风光", "德江县", 4.2, "武陵山区的高山草场，夏季凉爽", "武陵草场，云顶之境", "40 元", "08:30–17:00", "德江县高山乡", "建议 2 小时", ["土家腊肉", "糯米糍粑"]),
    ("玉屏 · 茶花泉景区", "3A", "自然风光", "玉屏县", 4.1, "万亩茶花园，冬末初春赏花好去处", "茶花泉畔，茶花烂漫", "30 元", "08:30–17:30", "玉屏县茶花泉", "建议 2 小时", ["侗家腌鱼", "油茶汤"]),
    ("万山区 · 中华山", "3A", "自然风光", "万山区", 4.0, "万山近郊山峰，登高望远好去处", "中华山顶，俯瞰万山", "免费", "08:00–17:00", "万山区中华山", "建议 2 小时", ["万山朱砂糕", "刺梨汁"]),
    ("碧江区 · 文笔峰公园", "免费", "自然风光", "碧江区", 4.1, "铜仁市区登高观城的地标山峰", "文笔峰顶，一览铜仁", "免费", "全天开放", "铜仁市区文笔峰", "建议 1 小时", ["铜仁豆浆粉", "糖麻圆"]),
    ("江口 · 寨抱村", "4A", "民族村寨", "江口县", 4.4, "梵净山下的侗寨，曾获中国最美村寨称号", "寨抱侗寨，最美村寨", "免费", "全天开放", "江口县寨抱村", "建议 2 小时", ["侗家腊肉", "糯米腌鱼"]),
    ("松桃 · 老寨苗族银饰工坊", "免费", "民族村寨", "松桃县", 4.2, "苗族银饰锻制技艺传承工坊", "苗银之光，手工之美", "免费", "08:30–17:00", "松桃县老寨村", "建议 1–2 小时", ["苗家酸汤鱼", "松桃卤鸭"]),
    ("石阡 · 中坝温泉小镇", "3A", "温泉休闲", "石阡县", 4.3, "石阡温泉集群之一，性价比高", "中坝温泉，平价好汤", "88 元", "09:00–23:00", "石阡县中坝镇", "建议 半天", ["石阡苔茶", "泉都绿壳蛋"]),
    ("印江 · 梵净山护国寺", "免费", "自然风光", "印江县", 4.3, "梵净山四大皇庵之首，海拔较高", "护国古寺，山巅禅意", "免费（含在梵净山门票内）", "08:00–17:00", "梵净山景区内", "建议 1–2 小时", ["印江绿豆粉", "酸汤鱼"]),
    ("德江 · 扶阳古城", "3A", "古镇人文", "德江县", 4.1, "唐代扶阳县治遗址，土家吊脚楼群", "扶阳古城，唐遗土家", "40 元", "08:30–17:00", "德江县扶阳镇", "建议 2 小时", ["土家腊肉", "糯米糍粑"]),
]


def _seed_spots(db: SessionLocal):
    """景点 + 图片"""
    existing = db.query(m.Spot).all()
    if existing:
        print(f"  [spot] 已存在 {len(existing)} 条，跳过")
        return
    all_spots = SPOT_TEMPLATES + EXTRA_SPOT_PATTERNS
    spot_objs = []
    for i, tpl in enumerate(all_spots, start=1):
        (name, level, cat, district, score, brief, slogan, ticket, open_, traffic, duration, foods) = tpl
        spot = m.Spot(
            name=name, level=level, cat=cat, district=district,
            score=score, brief=brief, slogan=slogan,
            img=random.choice(IMAGES_POOL),
            ticket=ticket, open_=open_, traffic=traffic, duration=duration,
            intro=[
                f"{name}位于{district}，是铜仁市重要的旅游目的地之一。{brief}，近年来基础设施不断完善，已成为吸引省内外游客的热门景区。",
                f"前往{name}游玩建议提前做好行程规划，旺季尤其需要预约购票。景区内配套设施完善，有餐饮、住宿、导游等多种服务供游客选择。"
            ],
            tips=[
                "建议穿舒适的运动鞋，部分路段坡度较大",
                "夏季注意防晒补水，冬季注意保暖",
                "可搭配周边景点组成 2–3 日行程"
            ],
            foods=foods,
            sort=i,
            status=1,
        )
        db.add(spot)
        spot_objs.append(spot)
    db.flush()  # 拿到 id

    # 图片（每个景点 2-4 张）
    for spot in spot_objs:
        num_imgs = random.randint(2, 4)
        for j in range(num_imgs):
            db.add(m.SpotImage(
                spot_id=spot.id,
                file=random.choice(IMAGES_POOL),
                sort=j,
            ))
    db.commit()
    print(f"  [spot] 写入 {len(spot_objs)} 条 + 图片")


def _seed_routes(db: SessionLocal):
    """路线 + 子表"""
    existing = db.query(m.Route).all()
    if existing:
        print(f"  [route] 已存在 {len(existing)} 条，跳过")
        return

    # 先查所有景点 id
    spot_ids = [s.id for s in db.query(m.Spot).all()]

    route_templates = [
        # (name, days, suitable, suit_short, difficulty, overview, foods, tip, cover, num_spots)
        ("两日游 · 梵净山朝圣", 2, "徒步 / 摄影爱好者", "徒步", "★★☆", "梵净山 → 苗王城 → 亚木沟", "酸汤牛肉、江口米豆腐", "需提前预约，备雨具与防滑鞋", "fanjingshan.jpg", 4),
        ("三日游 · 铜仁文化深度", 3, "文化爱好者", "文化", "★☆☆", "中南门古城 → 苗王城 → 云舍 → 石阡温泉", "铜仁米粉、石阡苔茶", "温泉需自备泳衣，古城晚上夜景更佳", "zhongnanmen.jpg", 5),
        ("一日游 · 梵净山精华", 1, "时间紧张游客", "精华", "★★★", "梵净山一日游", "江口米豆腐", "建议早上 8 点前到，避免索道排队", "fanjingshan.jpg", 2),
        ("两日游 · 温泉避暑", 2, "家庭游 / 老人", "温泉", "★☆☆", "石阡温泉 + 佛顶山", "石阡苔茶、泉都绿壳蛋", "温泉泡久了记得多喝水", "shiqian-spring.jpg", 3),
        ("三日游 · 侗寨苗乡风情", 3, "摄影 / 民族文化", "民族", "★★☆", "苗王城 + 寨沙侗寨 + 云舍 + 石阡", "侗家腊肉、苗家酸汤鱼", "苗寨部分地区需要当地向导", "miaowangcheng.jpg", 5),
        ("两日游 · 红色铜仁", 2, "红色文化爱好者", "红色", "★★☆", "困牛山 + 木黄会师 + 中南门古城", "铜仁豆浆粉", "建议穿正式服装参观红色景点", "zhongnanmen.jpg", 3),
        ("五日游 · 大铜仁环线", 5, "深度游 / 自驾", "环线", "★★★", "江口 → 松桃 → 石阡 → 沿河 → 思南", "铜仁美食全记录", "自驾需注意山路弯多，建议包车", "fanjingshan.jpg", 8),
        ("一日游 · 中南门老城漫步", 1, "休闲游 / 城市游", "休闲", "★☆☆", "中南门古城 + 三江公园 + 锦江夜游", "锅巴粉、糖麻圆", "建议晚上去，夜景更好", "zhongnanmen.jpg", 2),
        ("两日游 · 生态铜仁", 2, "自然爱好者", "生态", "★★☆", "梵净山 + 亚木沟 + 天生桥 + 麻阳河", "江口米豆腐", "山区信号不好，提前下离线地图", "yamugou.jpg", 5),
        ("三日游 · 美食之旅", 3, "吃货 / 家庭游", "美食", "★☆☆", "铜仁市区 + 江口 + 石阡 + 松桃", "铜仁美食全记录", "留好肚子，每站都有特色美食", "food-noodle.jpg", 4),
        ("四日游 · 全景铜仁", 4, "首次来铜仁", "全景", "★★☆", "梵净山 + 苗王城 + 石阡温泉 + 中南门 + 云舍", "铜仁美食全记录", "行程较满，建议每天按时出发", "fanjingshan.jpg", 6),
        ("两日游 · 江口深度", 2, "摄影 / 徒步", "江口", "★★☆", "梵净山 + 亚木沟 + 寨沙 + 云舍", "江口米豆腐、锅巴粉", "江口民宿很多，建议提前预订", "yunshe.jpg", 4),
        ("一日游 · 朱砂古镇探秘", 1, "古镇 / 猎奇", "探秘", "★☆☆", "朱砂古镇一日游", "万山朱砂糕", "矿洞内凉，建议带件薄外套", "zhusha.jpg", 2),
        ("两日游 · 乌江画廊", 2, "摄影 / 休闲", "乌江", "★★☆", "沿河乌江画廊 + 麻阳河", "沿河酸汤鱼", "船票建议提前买，旺季一票难求", "taiping-river.jpg", 3),
        ("三日游 · 儿童亲子", 3, "亲子游", "亲子", "★☆☆", "梵净山（索道）+ 中南门 + 温泉 + 侗寨", "铜仁美食", "小朋友记得带帽子和防晒霜", "fanjingshan.jpg", 5),
    ]

    route_objs = []
    for i, tpl in enumerate(route_templates, start=1):
        (name, days, suitable, suit_short, difficulty, overview, foods, tip, cover, num_spots) = tpl
        route = m.Route(
            name=name, days=days, suitable=suitable, suit_short=suit_short,
            difficulty=difficulty, overview=overview, foods=foods, tip=tip,
            cover=cover, sort=i, status=1,
        )
        db.add(route)
        route_objs.append(route)
    db.flush()

    for route in route_objs:
        # spot 关联
        chosen = random.sample(spot_ids, min(3 + route.days, len(spot_ids)))
        for k, sid in enumerate(chosen):
            db.add(m.RouteSpot(route_id=route.id, spot_id=sid, sort=k + 1))

        # 每天一个 plan
        for d in range(route.days):
            day_label = f"Day {d + 1}"
            plan = m.RoutePlan(
                route_id=route.id, day_index=d + 1, day_label=day_label,
                title=f"{day_label} · {['精华漫步', '深度游览', '文化探访', '休闲时光', '美食之旅'][d % 5]}",
            )
            db.add(plan)
            db.flush()
            # 每天 2-4 个 item
            for idx in range(random.randint(2, 4)):
                db.add(m.RoutePlanItem(
                    plan_id=plan.id,
                    time_=["08:30", "11:00", "14:00", "16:30"][idx % 4],
                    name=random.choice(["出发前往景区", "游览核心景点", "特色午餐", "周边散步", "合影留念", "返程酒店"]),
                    desc_=random.choice(["车程约 1 小时", "游览约 2 小时", "品尝当地特色美食", "购买伴手礼"]),
                    sort=idx,
                ))

        # 住宿 1-2 条
        stay_names = ["寨沙侗寨民宿", "江口梵净山大酒店", "石阡温泉度假中心", "苗王城侗家客栈", "铜仁市中心酒店"]
        for s in range(random.randint(1, 2)):
            db.add(m.RouteStay(
                route_id=route.id, name=stay_names[s],
                type=random.choice(["侗寨民宿", "商务酒店", "温泉度假酒店"]),
                price=f"¥{random.choice(['180', '260', '380', '480'])} 起",
                desc_="设施齐全，位置便利，当地口碑不错",
                sort=s,
            ))

        # 避坑提示 1-3 条
        avoids = [
            "旺季索道排队较长，建议 8 点前入园",
            "山区信号不稳定，提前下载离线地图",
            "苗族村寨部分区域需保持安静，尊重当地习俗",
            "温泉泡久了记得补充水分",
            "山路弯多，自驾注意减速慢行",
            "景区物价稍高，可自备零食和水",
        ]
        for a in random.sample(avoids, random.randint(1, 2)):
            db.add(m.RouteAvoid(route_id=route.id, content=a, sort=random.randint(1, 5)))

    db.commit()
    print(f"  [route] 写入 {len(route_objs)} 条 + 子表")


def _seed_culture(db: SessionLocal):
    """文化内容"""
    if db.query(m.Food).all():
        print("  [culture] 已存在，扩充中...")

    foods = [
        ("锅巴粉", "小吃", "food-noodle.jpg", "铜仁人最爱的早餐，米浆薄如蝉翼，微微焦香让人上瘾"),
        ("江口米豆腐", "小吃", "food-rice.jpg", "梵净山下的特色小吃，米香浓郁，凉拌煎炒皆宜"),
        ("酸汤牛肉", "正餐", "food-beef.jpg", "苗家酸汤与黄牛肉的绝配，酸辣开胃，越吃越想吃"),
        ("石阡苔茶", "饮品", "", "石阡特产，贵州名茶之一，汤色翠绿，回甘悠长"),
        ("铜仁豆浆粉", "早餐", "food-noodle.jpg", "铜仁中心城区的传统早餐，豆花嫩，粉条滑"),
        ("苗家酸汤鱼", "正餐", "food-rice.jpg", "苗族特色菜，红酸汤配河鱼，酸辣鲜香"),
        ("松桃卤鸭", "正餐", "food-beef.jpg", "松桃县特产，卤香浓郁，鸭肉紧实不柴"),
        ("侗家腊肉", "正餐", "food-beef.jpg", "侗寨过年必备，烟熏风味独特，搭配糯米食用最佳"),
        ("泉都绿壳蛋", "小吃", "", "石阡特产，蛋清醇厚，蛋黄饱满，营养价值高"),
        ("土家油茶汤", "饮品", "", "土家族传统饮品，茶叶炒香后加水煮，解腻消食"),
        ("糖麻圆", "甜品", "food-rice.jpg", "铜仁街头常见的甜品，糯米油炸后滚白糖，香甜可口"),
        ("万山朱砂糕", "甜品", "", "万山区特产，以朱砂为名的特色糕点，口感绵密"),
        ("油粑粑", "小吃", "food-noodle.jpg", "铜仁街头小吃，糯米浆油炸，外酥里嫩"),
        ("花甜粑", "甜品", "", "思南特产，糯米做的花形甜品，甜而不腻"),
        ("土家炸龙宴", "正餐", "food-beef.jpg", "德江土家炸龙节的特色宴席，菜品丰盛"),
    ]
    for f in foods:
        db.add(m.Food(name=f[0], tag=f[1], file=f[2], desc_=f[3], sort=len(db.query(m.Food).all()) + 1))

    folks = [
        ("土家摆手舞", "国家级非遗", "土家族古老的集体舞蹈，鼓点为节，动作粗犷有力"),
        ("苗族银饰锻制技艺", "国家级非遗", "松桃苗族银饰手工锻制，历经千锤百炼"),
        ("思州石砚制作技艺", "国家级非遗", "中国四大名砚之一，思南传统技艺"),
        ("玉屏箫笛制作技艺", "国家级非遗", "玉屏箫笛音色清越，有仙笛之誉"),
        ("侗族大歌", "世界级非遗", "侗族多声部无伴奏合唱，天籁之音"),
        ("苗族古歌", "国家级非遗", "苗族口头流传的史诗，记录民族起源"),
        ("石阡苔茶制作技艺", "国家级非遗", "石阡手工制茶工艺，代代相传"),
        ("土家织锦", "国家级非遗", "西兰卡普，土家族传统织锦工艺"),
    ]
    for f in folks:
        db.add(m.Folk(name=f[0], level=f[1], desc_=f[2], sort=len(db.query(m.Folk).all()) + 1))

    festivals = [
        ("正月", "十五", "元宵灯会", "碧江区", "铜仁市中心元宵灯会，舞龙舞狮放河灯"),
        ("二月", "初二", "土家社日", "沿河、德江", "土家族春耕前的祭祀节日，有传统仪式"),
        ("四月", "八", "苗族姊妹节", "松桃", "苗族青年男女社交的浪漫节日，又名东方情人节"),
        ("五月", "初五", "龙船节", "碧江区", "锦江龙舟赛，热闹非凡"),
        ("六月", "十九", "梵净山庙会", "江口县", "每年农历六月十九的梵净山观音庙会，香客云集"),
        ("八月", "十三", "土家炸龙节", "德江县", "德江土家炸龙节，烧龙狂舞，惊险刺激"),
        ("九月", "初九", "重阳节登高", "全市", "武陵山区重阳节登高赏秋传统"),
        ("腊月", "二十三", "侗族小年", "玉屏、江口", "侗族的传统小年，杀年猪打糍粑"),
    ]
    for f in festivals:
        db.add(m.Festival(month=f[0], day=f[1], name=f[2], place=f[3], desc_=f[4], sort=len(db.query(m.Festival).all()) + 1))

    ethnics = [
        ("苗族", "摆手舞 · 苗银 · 姊妹节", "松桃苗乡，银光成诗。苗族是铜仁人口最多的少数民族，善歌舞、爱银饰。", "miao-silver.jpg", 1),
        ("土家族", "西兰卡普 · 过社 · 炸龙", "沿河、德江土家，依山而居。土家族有独特的织锦技艺和摆手舞。", "tujia-dance.jpg", 0),
        ("侗族", "大歌 · 鼓楼 · 腌鱼", "玉屏、江口侗寨，鼓楼是侗寨的灵魂，大歌是天籁之声。", "yunshe.jpg", 0),
        ("仡佬族", "傩戏 · 敬酒歌", "石阡仡佬族是贵州最古老的世居民族之一，傩戏独具特色。", "gelao-festival.jpg", 1),
    ]
    for e in ethnics:
        db.add(m.Ethnic(name=e[0], keys_=e[1], desc_=e[2], file=e[3], mono=e[4], sort=len(db.query(m.Ethnic).all()) + 1))

    # seasons 保持 4 条
    if not db.query(m.Season).all():
        for s in [("春", "3月–5月", "15–25℃", "杜鹃花开，万物复苏", "leaf"),
                  ("夏", "6月–8月", "22–32℃", "避暑旺季，梵净山下清凉宜人", "sun"),
                  ("秋", "9月–11月", "12–22℃", "彩林最佳，万山红遍层林尽染", "leaf"),
                  ("冬", "12月–2月", "2–12℃", "雪景温泉，泡汤赏雪两不误", "calendar")]:
            db.add(m.Season(name=s[0], months=s[1], temp=s[2], note=s[3], icon=s[4], sort=len(db.query(m.Season).all()) + 1))

    # banners
    banners = [
        ("fanjingshan.jpg", "世界自然遗产", "云海之上，天空之城", "梵净山 · 江口县 · 5A", "spot", 1),
        ("miaowangcheng.jpg", "千年苗寨", "苗银闪光处，苗家第一城", "苗王城 · 松桃县 · 4A", "spot", 2),
        ("shiqian-spring.jpg", "温泉之都", "千年温泉，泡去风尘", "石阡温泉 · 石阡县 · 4A", "spot", 3),
        ("zhongnanmen.jpg", "城市根脉", "明清古城，铜仁记忆", "中南门古城 · 碧江区 · 4A", "spot", 4),
        ("zhaisha.jpg", "侗寨夜色", "鼓楼月下，侗歌悠扬", "寨沙侗寨 · 江口县 · 4A", "spot", 5),
        ("yamugou.jpg", "峡谷幽泉", "深山里的翡翠项链", "亚木沟 · 江口县 · 4A", "spot", 6),
        ("jinjiang-night.jpg", "夜色铜仁", "锦江灯火，璀璨如昼", "碧江区 · 夜景", "spot", 7),
        ("taiping-river.jpg", "清凉漂流", "夏日好去处，清凉一整夏", "太平河漂流 · 江口县", "route", 8),
    ]
    for i, b in enumerate(banners, start=1):
        db.add(m.Banner(file=b[0], eyebrow=b[1], title=b[2], meta=b[3], link_type=b[4], link_id=b[5], sort=i, status=1))

    # notices
    notices = [
        ("梵净山旺季预约公告", "梵净山旺季（3–11 月）需提前 1–3 天在官方渠道实名预约购票，未预约无法入园。", date.today() - timedelta(days=3)),
        ("雨季旅游安全提示", "近期铜仁进入雨季，山区道路湿滑，建议携带防滑鞋和雨具，注意出行安全。", date.today() - timedelta(days=1)),
        ("景区开放时间调整通知", "夏季景区开放时间调整为 07:30–18:00，请游客合理安排行程。", date.today() - timedelta(days=7)),
        ("文化演出时间公布", "中南门古城每晚 20:00 有免费侗歌苗舞演出，欢迎游客前往观看。", date.today() - timedelta(days=5)),
        ("温泉票价格公示", "石阡温泉全新改版后票价调整为 128 元起，学生、老人可享半价优惠。", date.today() - timedelta(days=10)),
    ]
    for n in notices:
        db.add(m.Notice(title=n[0], content=n[1], publish_date=n[2], sort=random.randint(1, 10), status=1))

    db.commit()
    print("  [culture] 文化内容扩充完成")


def _seed_users(db: SessionLocal):
    """测试用户"""
    existing = db.query(m.User).all()
    if len(existing) >= 3:
        print(f"  [user] 已有 {len(existing)} 条，跳过")
        return

    test_users = [
        ("13800000001", "测试用户一", "123456"),
        ("13800000002", "铜仁旅行者", "123456"),
        ("13800000003", "梵净山粉丝", "123456"),
        ("13800000004", "苗寨探秘者", "123456"),
        ("13800000005", "温泉泡汤达人", "123456"),
    ]
    for phone, nickname, pwd in test_users:
        # 检查是否存在
        if db.query(m.User).filter(m.User.phone == phone).first():
            continue
        db.add(m.User(
            openid=f"phone:{phone}", phone=phone, nickname=nickname,
            avatar="", password_hash=hash_password(pwd),
        ))
    db.commit()
    print(f"  [user] 写入测试账号，密码统一 123456")


def _seed_logs(db: SessionLocal, count=800):
    """用户行为日志（pipelines 原料）—— 随机分布到过去 180 天"""
    existing = db.query(m.UserLog).all()
    if len(existing) >= 500:
        print(f"  [user_log] 已有 {len(existing)} 条，跳过")
        return

    spot_ids = [s.id for s in db.query(m.Spot).all()]
    route_ids = [r.id for r in db.query(m.Route).all()]
    user_ids = [u.id for u in db.query(m.User).all()] + [0, 0, 0]  # 大量游客

    events_weighted = (
        ["spot_view"] * 50 +  # 50% 景点浏览
        ["page_view"] * 20 +   # 20% 页面浏览
        ["search"] * 10 +      # 10% 搜索
        ["favorite"] * 8 +     # 8% 收藏
        ["trip_generate"] * 7 +  # 7% 路线生成
        ["login_view"] * 5     # 5% 登录页
    )
    keywords = ["梵净山", "石阡温泉", "苗王城", "中南门", "亚木沟", "朱砂古镇", "云舍", "太平河", "天生桥", "佛顶山", "乌江画廊"]
    pages = [
        "pages/home/home", "pages/spots/spots", "pages/spot-detail/spot-detail",
        "pages/routes/routes", "pages/route-detail/route-detail", "pages/custom/custom",
        "pages/food/food", "pages/data/data", "pages/search/search", "pages/login/login",
    ]

    now = datetime.now()
    batch_size = 200
    written = 0
    target = count - len(existing)

    while written < target:
        batch_n = min(batch_size, target - written)
        logs = []
        for _ in range(batch_n):
            event = random.choice(events_weighted)
            days_ago = random.randint(0, 180)
            hour = random.randint(6, 23)
            minute = random.randint(0, 59)
            ts = now - timedelta(days=days_ago, hours=23 - hour, minutes=60 - minute)

            target_type = ""
            target_id = 0
            if event in ("spot_view", "favorite"):
                target_type = "spot"
                target_id = random.choice(spot_ids) if spot_ids else 0
            elif event == "trip_generate":
                target_type = "route"
                target_id = random.choice(route_ids) if route_ids else 0
            elif event == "page_view":
                target_type = "spot"
                target_id = random.choice(spot_ids) if spot_ids and random.random() < 0.6 else 0

            logs.append(m.UserLog(
                user_id=random.choice(user_ids),
                event=event,
                target_type=target_type,
                target_id=target_id,
                keyword=random.choice(keywords) if event == "search" else "",
                page=random.choice(pages),
                channel="miniapp",
                created_at=ts,
            ))

        db.add_all(logs)
        db.commit()
        written += batch_n
        print(f"  [user_log] 已写入 {written}/{target}")

    print(f"  [user_log] 完成，共写入 {written} 条新日志")


def _seed_favorites_and_trips(db: SessionLocal):
    """用户收藏与行程（少量即可）"""
    if db.query(m.UserFavorite).all():
        print("  [favorite/trip] 已有数据，跳过")
        return

    users = db.query(m.User).all()
    spot_ids = [s.id for s in db.query(m.Spot).all()]
    route_ids = [r.id for r in db.query(m.Route).all()]

    for u in users[:3]:
        # 收藏 2-4 个景点
        for sid in random.sample(spot_ids, random.randint(2, 4)):
            db.add(m.UserFavorite(user_id=u.id, target_type="spot", target_id=sid, favorite=1))
        # 收藏 1-2 条路线
        for rid in random.sample(route_ids, random.randint(1, 2)):
            db.add(m.UserFavorite(user_id=u.id, target_type="route", target_id=rid, favorite=1))

    db.commit()
    print("  [favorite] 收藏数据写入完成")


def main():
    print("=" * 60)
    print(" 种子数据灌库脚本 · 大美铜仁")
    print("=" * 60)
    print()

    db = SessionLocal()
    try:
        _seed_spots(db)
        _seed_routes(db)
        _seed_culture(db)
        _seed_users(db)
        _seed_logs(db, count=800)
        _seed_favorites_and_trips(db)

        # 最终统计
        print()
        print("-" * 60)
        print(" 最终各表数据量：")
        print("-" * 60)
        tables = [
            ("t_spot", m.Spot), ("t_spot_image", m.SpotImage),
            ("t_route", m.Route),
            ("t_food", m.Food), ("t_folk", m.Folk), ("t_festival", m.Festival),
            ("t_ethnic", m.Ethnic), ("t_season", m.Season),
            ("t_banner", m.Banner), ("t_notice", m.Notice),
            ("t_user", m.User), ("t_user_log", m.UserLog),
            ("t_user_favorite", m.UserFavorite), ("t_user_trip", m.UserTrip),
        ]
        total = 0
        for name, model in tables:
            n = len(db.query(model).all())
            print(f"  {name:30s} = {n:4d}")
            total += n
        print(f"  {'合计':30s} = {total:4d}")
        print()
        print(">= 200 条要求：", "✅ 已达标" if total >= 200 else f"❌ 当前 {total}，请补数据")
    finally:
        db.close()


if __name__ == "__main__":
    main()
