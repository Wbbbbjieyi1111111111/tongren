# 大美铜仁 · 小程序后端接口契约 v1

> 本文件是小程序前端（`tongren-miniapp`）与未来 Python 后端之间的**唯一约定**。
> 前端已完成全部页面并把 `common/config.js` 的 `mode` 默认为 `'mock'`；
> 后端就绪后把 `mode` 改成 `'api'` 并把 `baseUrl` 指向服务地址即可，**前端页面代码零改动**。

---

## 1. 通用约定

| 项 | 约定 |
|---|---|
| 基础地址 | `config.baseUrl` + `config.apiPrefix`，默认 `https://api.example.com/api/v1` |
| 前缀 | 所有业务接口以 `/api/v1` 开头 |
| 编码 | `application/json; charset=utf-8` |
| 鉴权 | `Authorization: Bearer <token>`（可选；未登录时前端仍可浏览） |
| 超时 | 12000 ms（`config.timeout`） |

### 1.1 统一响应体

成功：

```json
{ "code": 0, "message": "ok", "data": { } }
```

失败：

```json
{ "code": 40401, "message": "景点不存在", "data": null }
```

> 前端 `common/api.js` 的 `request()` 只在 `res.data.code === 0` 时 resolve，
> 否则 reject 并调用 `app.toast(message)`。**`code` 必须是数字 0 表示成功。**

`code` 约定：

| code | 含义 |
|---|---|
| `0` | 成功 |
| `40001` | 参数错误 |
| `40401` | 资源不存在 |
| `50001` | 服务器内部错误 |
| `40101` | 未登录 / token 失效 |

### 1.2 分页约定

列表接口统一返回：

```json
{ "code": 0, "data": { "list": [], "total": 12 } }
```

请求参数：`page`（从 1 开始）、`pageSize`（默认 20，最大 100）。

---

## 2. 内容类接口

### 2.1 景点

#### `GET /api/v1/spots`

查询参数：

| 参数 | 类型 | 说明 |
|---|---|---|
| `keyword` | string | 名称/简介模糊匹配 |
| `level` | string | `5A` / `4A` / `3A` |
| `cat` | string | `自然风光` / `古镇人文` / `温泉休闲` / `红色景点` |
| `district` | string | `江口县` / `碧江区` / `松桃县` / `石阡县` / `万山区` / `印江县` |
| `page` / `pageSize` | int | 分页 |

响应 `data`：

```json
{
  "list": [
    {
      "id": 1,
      "name": "梵净山",
      "level": "5A",
      "cat": "自然风光",
      "district": "江口县",
      "score": 4.9,
      "brief": "世界自然遗产，云海之上的天空之城",
      "slogan": "云海翻涌处，山是一尊佛",
      "img": "fanjingshan.jpg",
      "images": ["fanjingshan.jpg", "yamugou.jpg", "taiping-river.jpg"],
      "ticket": "旺季 100 元 / 淡季 50 元",
      "open": "08:00–18:00（旺季）",
      "traffic": "铜仁站 → 江口客运站 → 游客中心",
      "duration": "建议 4–6 小时",
      "intro": ["…", "…"],
      "tips": ["…", "…", "…"],
      "foods": ["锅巴粉", "江口米豆腐"]
    }
  ],
  "total": 12
}
```

> `img` / `images[]` 返回的是**文件名**，前端通过 `api.toImageUrl(file)` 拼成完整 URL。
> 字段与 MySQL `t_spot` + `t_spot_image` 一一对应。

#### `GET /api/v1/spots/{id}`

返回单个景点对象，字段同上（不含 `total`）。

#### `GET /api/v1/spots/{id}/related?limit=4`

返回推荐景点数组（对象同上），按品类/区县/评分相似度排序。

---

### 2.2 路线

#### `GET /api/v1/routes`

参数：`days`（int，筛选天数）、`suit`（string，适合人群短标签）、`keyword`、分页参数。

`data`：

```json
{
  "list": [
    {
      "id": 2,
      "name": "两日游 · 梵净山朝圣",
      "days": 2,
      "suitable": "徒步 / 摄影爱好者",
      "suitShort": "徒步",
      "difficulty": "★★☆",
      "overview": "梵净山 → 苗王城 → 亚木沟",
      "foods": "酸汤牛肉、江口米豆腐",
      "tip": "需提前预约，备雨具与防滑鞋",
      "cover": "fanjingshan.jpg",
      "spotIds": [1, 2, 10],
      "plan": [
        {
          "day": "Day 1",
          "title": "梵净山朝圣",
          "items": [
            { "time": "08:30", "name": "出发前往江口", "desc": "铜仁市区出发，车程约 1 小时。" }
          ]
        }
      ],
      "stays": [
        { "name": "寨沙侗寨民宿", "type": "侗寨民宿", "price": "¥260 起", "desc": "…" }
      ],
      "avoid": ["周末老街人多，贵重物品随身放好"]
    }
  ],
  "total": 5
}
```

> 对应 MySQL：`t_route` + `t_route_plan` + `t_route_plan_item` + `t_route_stay` + `t_route_avoid` + `t_route_spot`。

#### `GET /api/v1/routes/{id}`

返回单个路线对象（结构同上）。

#### `POST /api/v1/routes/custom`

请求体：

```json
{ "spotIds": [1, 4, 6, 8], "days": 2, "title": "我的铜仁 2 日游" }
```

响应 `data`：

```json
{
  "title": "我的铜仁 2 日游",
  "dayCount": 2,
  "days": [
    {
      "day": "DAY 1",
      "title": "DAY 1",
      "items": [
        { "time": "09:00", "name": "梵净山", "desc": "…" },
        { "time": "11:30", "name": "苗王城", "desc": "…" },
        { "time": "14:30", "name": "石阡温泉", "desc": "…" }
      ]
    }
  ],
  "plan": [ "与 days 同构的数组，便于直接渲染时间轴" ]
}
```

> 前端 mock 规则：**每 3 个景点为 1 天**，每天时间点 `09:00 / 11:30 / 14:30`。
> 后端实现请保持一致，或返回同样结构即可（前端只按 `days[].items[]` 渲染）。

---

### 2.3 文化内容

| 方法 | 路径 | 返回数组字段 | MySQL 表 |
|---|---|---|---|
| GET | `/api/v1/foods` | `{name, tag, file, desc}` | `t_food` |
| GET | `/api/v1/folk` | `{name, level, desc}` | `t_folk` |
| GET | `/api/v1/festivals` | `{month, day, name, place, desc}` | `t_festival` |
| GET | `/api/v1/ethnic` | `{name, keys, desc, file, mono}` | `t_ethnic` |
| GET | `/api/v1/seasons` | `{name, months, temp, note, icon}` | `t_season` |
| GET | `/api/v1/banners` | `{id, file, eyebrow, title, meta}` | `t_banner` |
| GET | `/api/v1/notices` | `{id, title}` | `t_notice` |

> `file` 同样是文件名，前端拼 URL。`mono` 为 1 时前端给民族卡片叠加灰绿蒙层。

---

### 2.4 搜索

#### `GET /api/v1/search?q=梵净&type=all`

参数：`q`（关键词，必填）、`type`（`all` / `spot` / `route` / `food`）。

`data`：`{ "list": [...], "total": 3, "keyword": "梵净" }`，`list` 元素**直接复用景点对象结构**（与 `/api/v1/spots` 列表项字段完全一致），前端不做二次映射：

```json
{
  "list": [
    {
      "id": 1,
      "name": "梵净山",
      "level": "5A",
      "cat": "自然风光",
      "district": "江口县",
      "score": 4.9,
      "brief": "世界自然遗产，云海之上的天空之城",
      "img": "fanjingshan.jpg"
    }
  ],
  "total": 1,
  "keyword": "梵净"
}
```

> 前端 `pages/search/search.js` 的 `toRow()` 直接消费 `id / name / img / district / cat / score`，
> 因此后端 **必须返回上述原文字段名**，不要改成 `title / desc / tags`。
>
> `type` 参数支持 `all` / `spot` / `route` / `food`；前端当前只用 `all`，
> 混合搜索时建议在结果项上追加 `type` 字段（默认 `spot`）以便前端区分跳转目标。
>
> 搜索日志请落到 `t_user_log`（event=`search`），这是 Python 端「搜索热度」分析的数据源。

---

## 3. 数据分析接口（Python 分析结果，前端只读）

> **这些接口是给 Python 数据分析模块的出口。** Python 侧负责从 `t_user_log`
> 等原始表训练/推理，再把聚合结果写入 `t_analytics_*` 表；后端 API 只做「查表 + 拼 JSON」。
> 前端不关心模型细节，接口未就绪时自动降级为占位文案（不白屏）。

### 3.1 `GET /api/v1/analytics/all?startDate=&endDate=&district=`

一次性返回全部分析数据，**结构与前端 mock 完全一致**（见 `common/api.js` 的 `getMockAnalytics()`）：

```json
{
  "code": 0,
  "data": {
    "updatedAt": "2026-05-20 10:00",
    "source": "python-analysis",
    "overview": {
      "list": [
        { "key": "visitors",     "label": "年游客量",   "value": "1286",   "unit": "万人次", "delta": "+12.4%", "trend": "up" },
        { "key": "avgStay",      "label": "平均停留",   "value": "2.8",    "unit": "天",     "delta": "+0.3",   "trend": "up" },
        { "key": "hotSpot",      "label": "最热景点",   "value": "梵净山",  "unit": "",       "delta": "+18.6%", "trend": "up" },
        { "key": "satisfaction", "label": "游客满意度", "value": "96.2",   "unit": "%",      "delta": "+1.8",   "trend": "up" }
      ]
    },
    "trend":    { "list": [{ "label": "1月", "value": 62 }], "unit": "万人次" },
    "district": { "list": [{ "label": "江口县", "value": 262 }], "unit": "万人次" },
    "category": { "list": [{ "label": "自然风光", "value": 38 }], "unit": "%" },
    "ranking":  { "list": [{ "rank": 1, "name": "梵净山", "score": 4.9, "visitors": 318 }] },
    "season":   { "list": [{ "label": "夏", "value": 95, "note": "避暑旺季" }], "unit": "指数" },
    "heat":     { "list": [{ "row": 0, "col": 0, "value": 12 }], "rows": 4, "cols": 4 },
    "prediction": {
      "list": [
        { "label": "未来 30 日客流预测", "value": "峰值 151 万人次", "advice": "7 月中旬建议增开 2 条运力" }
      ]
    }
  }
}
```

### 3.2 单项接口

前端同时提供细粒度接口，便于按需加载 / 单独缓存：

| 方法 | 路径 | 对应表 | 返回 |
|---|---|---|---|
| GET | `/api/v1/analytics/overview` | `t_analytics_overview` | `{ list:[{key,label,value,unit,delta,trend}] }` |
| GET | `/api/v1/analytics/trend` | `t_analytics_trend` | `{ list:[{label,value}], unit }` |
| GET | `/api/v1/analytics/district` | `t_analytics_district` | `{ list:[{label,value}], unit }` |
| GET | `/api/v1/analytics/category` | `t_analytics_category` | `{ list:[{label,value}], unit }` |
| GET | `/api/v1/analytics/ranking` | `t_analytics_ranking` | `{ list:[{rank,name,score,visitors}] }` |
| GET | `/api/v1/analytics/season` | `t_analytics_season` | `{ list:[{label,value,note}], unit }` |
| GET | `/api/v1/analytics/heat` | `t_analytics_heat` | `{ list:[{row,col,value}], rows, cols }` |
| GET | `/api/v1/analytics/prediction` | `t_analytics_prediction` | `{ list:[{label,value,advice}] }` |

公共查询参数：

| 参数 | 说明 |
|---|---|
| `startDate` | `YYYY-MM-DD` |
| `endDate` | `YYYY-MM-DD` |
| `district` | 区县过滤，可选 |
| `period` | `trend` 接口用：`day` / `month` / `quarter` |

> 每个接口都应返回**最新的一个 `stat_date`**（或按 `startDate/endDate` 区间聚合）。
> `updatedAt` 字段建议放在 `data` 根节点，前端用来显示「数据更新于 …」。

---

## 4. 用户接口

| 方法 | 路径 | 请求体 | 说明 |
|---|---|---|---|
| POST | `/api/v1/user/favorites` | `{ "type": "spot", "targetId": 1, "favorite": true }` | 收藏/取消收藏，`type` ∈ `spot`/`route` |
| GET | `/api/v1/user/favorites` | — | 返回 `{ spotIds:[], routeIds:[] }` |
| POST | `/api/v1/user/trips` | `{ "title":"…", "days":2, "spotIds":[1,4,6,8], "plan":{…} }` | 保存自定义行程 |
| GET | `/api/v1/user/trips` | — | 返回行程数组 |
| POST | `/api/v1/user/log` | `{ "event":"spot_view", "targetType":"spot", "targetId":1, "page":"pages/spot-detail/spot-detail" }` | 埋点上报（前端 `app.track()` 调用） |

> `t_user_log` 是 Python 分析的原始输入表，**建议前端埋点全部落库**。

---

## 5. 静态资源

图片目前打包在小程序 `static/img/` 内。后续如果迁到 OSS/CDN：

- 后端返回的仍是**文件名**；
- 前端通过 `common/config.js` 的 `imgBase` / `iconBase` / `decoBase` 决定前缀；
- 改配置即可，无需改页面代码。

若改为「后端直出完整 URL」，只需把 `api.toImageUrl()` 改成原样返回——前端页面不用动。

---

## 6. 数据导入（把 mock 灌进 MySQL）

`common/mock/*.js` 与下面的表结构同构，可用一段 Python 脚本直接导入：

```python
# tools/import_mock.py
import json, pymysql

conn = pymysql.connect(host="127.0.0.1", user="root", password="***",
                       database="tongren", charset="utf8mb4")
with conn.cursor() as cur:
    for s in json.load(open("spots.json", encoding="utf-8")):
        cur.execute(
            """INSERT INTO t_spot (name,level,cat,district,score,brief,slogan,img,
                                 ticket,open,traffic,duration,intro,tips,foods,sort)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (s["name"], s["level"], s["cat"], s["district"], s["score"], s["brief"],
             s["slogan"], s["img"], s["ticket"], s["open"], s["traffic"], s["duration"],
             json.dumps(s["intro"], ensure_ascii=False),
             json.dumps(s["tips"], ensure_ascii=False),
             json.dumps(s["foods"], ensure_ascii=False), s["id"]))
    conn.commit()
```

路线需要拆成 `t_route` / `t_route_plan` / `t_route_plan_item` / `t_route_stay` /
`t_route_avoid` / `t_route_spot` 六张表插入，逻辑同上。

---

## 7. 联调切换步骤

1. 后端跑起来，确认 `GET /api/v1/spots` 返回 `{"code":0,"data":{"list":[...],"total":12}}`。
2. 微信开发者工具 → 右上角「详情 → 本地设置 → 不校验合法域名」勾上（开发期）。
3. 改 `tongren-miniapp/common/config.js`：

```js
module.exports = {
  mode: 'api',                                  // 'mock' → 'api'
  baseUrl: 'http://127.0.0.1:8000',             // 你的服务地址
  apiPrefix: '/api/v1',
  // ...
};
```

4. 重新编译。页面代码 **不需要任何修改**。

> 小程序正式发布时 `baseUrl` 必须是 HTTPS 且在「开发管理 → 服务器域名 → request 合法域名」中配置。

---

## 8. 错误码与降级策略

| 场景 | 前端行为 |
|---|---|
| 网络超时 / 5xx | `app.toast('网络异常，请稍后再试')`，页面保留空态 |
| `code !== 0` | toast 显示后端 `message`，数据保持空 |
| `/analytics/*` 无数据 | 数据分析页显示「数据接入中」占位，**不影响其他页面** |
| 图片 404 | `<image>` 使用 `binderror` 兜底为 `deco` 底图 |

---

## 9. 附：接口与前端文件对应关系

| 接口 | 前端调用 | 页面 |
|---|---|---|
| `/banners` | `api.getBanners()` | 首页轮播 |
| `/spots` | `api.getSpots()` | 首页横滑、景点列表瀑布流、自定义路线选点 |
| `/spots/{id}` | `api.getSpot(id)` | 景点详情 |
| `/spots/{id}/related` | `api.getRelatedSpots(id)` | 景点详情「相关推荐」 |
| `/routes` | `api.getRoutes()` | 路线页列表 |
| `/routes/{id}` | `api.getRoute(id)` | 路线详情 |
| `/routes/custom` | `api.generateCustomRoute()` | 自定义路线 |
| `/foods` `/folk` `/festivals` | `api.getFoods()` 等 | 美食民俗页 |
| `/ethnic` | `api.getEthnic()` | 关于页民族风情 |
| `/seasons` | `api.getSeasons()` | 美食民俗页季节、贴士页季节网格 |
| `/notices` | `api.getNotices()` | 首页公告、关于页 |
| `/search` | `api.search()` | 搜索页 |
| `/analytics/*` | `api.getAnalytics*()` | 数据分析页 |
| `/user/favorites` | `api.syncFavorite()` | 景点/路线收藏 |
| `/user/trips` | `api.saveTrip()` | 自定义行程保存 |
