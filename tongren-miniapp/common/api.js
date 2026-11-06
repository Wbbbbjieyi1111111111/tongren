/**
 * 数据访问层（REST）
 * =============================================================================
 * 后端契约：Python (Flask/FastAPI) + MySQL
 * 接口前缀：/api/v1            统一返回 { code: 0, data: <payload> }
 * 完整契约：docs/API-CONTRACT.md    库表：docs/schema.sql
 *
 * 设计约定
 *  - 当前 mode='mock'：直接返回 common/mock 下的本地数据，字段结构与后端
 *    返回体完全一致，因此切换 mode='api' 时页面代码无需任何改动。
 *  - mock 数据文件里逐条标注了对应的 MySQL 表名，方便后端对齐。
 * =============================================================================
 */
const config = require('./config');
const mockSpots = require('./mock/spots');
const mockRoutes = require('./mock/routes');
const mockCulture = require('./mock/culture');

/** 登录态请求头：token 存于 wx.storage（登录成功后写入） */
function authHeader() {
  try {
    const token = wx.getStorageSync('token');
    return token ? { Authorization: 'Bearer ' + token } : {};
  } catch (e) {
    return {};
  }
}

/** 统一的请求封装 */
function request(path, options) {
  const opts = options || {};
  const url = config.baseUrl + config.apiPrefix + path;
  return new Promise((resolve, reject) => {
    wx.request({
      url: url,
      method: opts.method || 'GET',
      data: opts.data || {},
      header: Object.assign(
        {
          'Content-Type': 'application/json'
        },
        authHeader(),
        opts.header || {}
      ),
      timeout: opts.timeout || config.timeout,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300 && res.data && res.data.code === 0) {
          resolve(res.data.data);
        } else {
          const msg =
            (res.data && res.data.message) || `请求失败 (${res.statusCode})`;
          reject(new Error(msg));
        }
      },
      fail(err) {
        reject(new Error(err.errMsg || '网络异常'));
      }
    });
  });
}

/** mock 模式下模拟网络延迟，保证加载态表现与真实环境一致 */
function mock(payload, delay) {
  return new Promise((resolve) => {
    setTimeout(() => resolve(payload), delay === undefined ? 120 : delay);
  });
}

const isMock = () => config.mode === 'mock';

function toImageUrl(name) {
  if (!name) return '';
  if (/^https?:|^data:/.test(name)) return name;
  return config.imgBase + name;
}

function toIconUrl(name, color) {
  if (!name) return '';
  const file = color ? `${name}-${color}.png` : `${name}.png`;
  return config.iconBase + file;
}

/* ===========================================================================
 * 景点
 * GET  /api/v1/spots              列表（keyword / level / district / cat / page / pageSize）
 * GET  /api/v1/spots/{id}         详情
 * GET  /api/v1/spots/{id}/related  相关推荐
 * 对应表：t_spot, t_spot_image, t_spot_intro, t_spot_tip, t_spot_food
 * ========================================================================= */
function getSpots(params) {
  if (isMock()) {
    const p = params || {};
    let list = mockSpots.SPOTS.slice();
    if (p.keyword) {
      const k = String(p.keyword).trim();
      list = list.filter((s) =>
        (s.name + s.cat + s.district + s.brief).indexOf(k) !== -1
      );
    }
    if (p.level) list = list.filter((s) => s.level === p.level);
    if (p.district) list = list.filter((s) => s.district === p.district);
    if (p.cat) list = list.filter((s) => s.cat === p.cat);
    return mock({ list: list, total: list.length });
  }
  return request('/spots', { data: params });
}

function getSpot(id) {
  if (isMock()) {
    const s = mockSpots.getSpotById(id);
    return mock(s || null);
  }
  return request('/spots/' + id);
}

function getRelatedSpots(id, limit) {
  if (isMock()) {
    const s = mockSpots.getSpotById(id);
    if (!s) return mock([]);
    const sameCat = mockSpots.SPOTS.filter(
      (x) => x.id !== id && x.cat === s.cat
    );
    const rest = mockSpots.SPOTS.filter(
      (x) => x.id !== id && x.cat !== s.cat
    );
    return mock(sameCat.concat(rest).slice(0, limit || 4));
  }
  return request(`/spots/${id}/related`, { data: { limit: limit || 4 } });
}

/* ===========================================================================
 * 路线
 * GET  /api/v1/routes             列表
 * GET  /api/v1/routes/{id}        详情（含 plan / stays / avoid）
 * POST /api/v1/routes/custom      自定义行程生成
 * 对应表：t_route, t_route_plan, t_route_item, t_route_stay, t_route_avoid, t_route_spot
 * ========================================================================= */
function getRoutes(params) {
  if (isMock()) {
    const p = params || {};
    let list = mockRoutes.ROUTES.slice();
    if (p.days) list = list.filter((r) => r.days === Number(p.days));
    if (p.suit) list = list.filter((r) => r.suitShort === p.suit);
    if (p.keyword) {
      const k = String(p.keyword).trim();
      list = list.filter((r) =>
        (r.name + r.overview + r.suitable + r.foods).indexOf(k) !== -1
      );
    }
    return mock({ list: list, total: list.length });
  }
  return request('/routes', { data: params });
}

function getRoute(id) {
  if (isMock()) {
    const r = mockRoutes.getRouteById(id);
    return mock(r || null);
  }
  return request('/routes/' + id);
}

/**
 * 自定义路线生成
 * @param {Object} payload { title, spotIds: [], pace: 'relaxed'|'standard'|'packed' }
 * @returns {Promise<{title:string, days:Array, plan:Array, dayCount:number}>}
 *          days/plan 为同构数组：[{ day:'DAY 1', title:'DAY 1', items:[{time,name,desc}] }]
 */
function generateCustomRoute(payload) {
  if (isMock()) {
    const spotIds = (payload && payload.spotIds) || [];
    const groups = [];
    for (let i = 0; i < spotIds.length; i += 3) {
      groups.push(spotIds.slice(i, i + 3));
    }
    const times = ['09:00', '11:30', '14:30'];
    const plan = groups.map((g, gi) => ({
      day: 'DAY ' + (gi + 1),
      title: 'DAY ' + (gi + 1),
      items: g.map((sid, si) => {
        const s = mockSpots.getSpotById(sid);
        return {
          time: times[si],
          name: s ? s.name : sid,
          desc: s ? s.district + ' · ' + s.cat : ''
        };
      })
    }));
    return mock({
      title: (payload && payload.title) || '我的铜仁 ' + groups.length + ' 日游',
      dayCount: groups.length,
      days: plan,
      plan: plan
    });
  }
  return request('/routes/custom', { method: 'POST', data: payload });
}

/* ===========================================================================
 * 文化 / 美食 / 民俗 / 节庆 / 民族 / 季节
 * GET  /api/v1/foods              -> t_food
 * GET  /api/v1/folk               -> t_folk
 * GET  /api/v1/festivals          -> t_festival
 * GET  /api/v1/ethnic             -> t_ethnic
 * GET  /api/v1/seasons            -> t_season
 * GET  /api/v1/banners            -> t_banner
 * GET  /api/v1/notices            -> t_notice
 * ========================================================================= */
function getFoods() {
  if (isMock()) return mock({ list: mockCulture.FOODS });
  return request('/foods');
}

function getFolk() {
  if (isMock()) return mock({ list: mockCulture.FOLK });
  return request('/folk');
}

function getFestivals() {
  if (isMock()) return mock({ list: mockCulture.FESTIVALS });
  return request('/festivals');
}

function getEthnic() {
  if (isMock()) return mock({ list: mockCulture.ETHNIC });
  return request('/ethnic');
}

function getSeasons() {
  if (isMock()) return mock({ list: mockCulture.SEASONS });
  return request('/seasons');
}

function getBanners() {
  if (isMock()) return mock({ list: mockCulture.BANNERS });
  return request('/banners');
}

function getNotices() {
  if (isMock()) {
    return mock({
      list: (config.notices || []).map((text, i) => ({
        id: i + 1,
        title: text,
        publishedAt: ''
      }))
    });
  }
  return request('/notices');
}

/* ===========================================================================
 * 搜索
 * GET  /api/v1/search?q=&type=
 * 对应表：跨 t_spot / t_food / t_folk 模糊匹配（后端可用 MySQL 全文索引或 LIKE）
 * ========================================================================= */
function search(keyword, type) {
  if (isMock()) {
    const k = String(keyword || '').trim();
    if (!k) {
      return mock({ list: [], total: 0, keyword: '' });
    }
    const list = mockSpots.SPOTS.filter((s) =>
      (s.name + s.cat + s.district + s.brief).indexOf(k) !== -1
    );
    return mock({ list: list, total: list.length, keyword: k });
  }
  return request('/search', { data: { q: keyword, type: type || 'all' } });
}

/* ===========================================================================
 * 数据分析（预留接口 —— 由后端 Python 分析模块产出）
 * -----------------------------------------------------------------------------
 * 对应 MySQL 表：
 *   t_analytics_overview   概览 KPI（游客量/客单价/转化率等）
 *   t_analytics_trend      按日/月的趋势序列
 *   t_analytics_district   区县分布
 *   t_analytics_category   品类占比
 *   t_analytics_ranking    景点排行
 *   t_analytics_season     季节性指数
 *   t_analytics_heat       热力网格
 *   t_analytics_prediction 模型预测结果
 *
 * 说明：前端只消费「已聚合的结构化结果」，Python 侧负责训练/推理并落库，
 *       前端无需关心模型细节。接口未就绪时前端自动降级为占位图。
 * ========================================================================= */

/** 概览 KPI —— P10 页顶部四个指标卡 */
function getAnalyticsOverview(params) {
  if (isMock()) return mock(getMockAnalytics().overview, 160);
  return request('/analytics/overview', { data: params });
}

/** 趋势折线 —— P10 页折线图 */
function getAnalyticsTrend(params) {
  if (isMock()) return mock(getMockAnalytics().trend, 160);
  return request('/analytics/trend', { data: params });
}

/** 区县分布 —— P10 页分布图 */
function getAnalyticsDistrict(params) {
  if (isMock()) return mock(getMockAnalytics().district, 160);
  return request('/analytics/district', { data: params });
}

/** 品类占比 —— P10 页环形图 */
function getAnalyticsCategory(params) {
  if (isMock()) return mock(getMockAnalytics().category, 160);
  return request('/analytics/category', { data: params });
}

/** 景点排行 —— P10 页榜单 */
function getAnalyticsRanking(params) {
  if (isMock()) return mock(getMockAnalytics().ranking, 160);
  return request('/analytics/ranking', { data: params });
}

/** 季节性指数 —— P10 页季节图 */
function getAnalyticsSeason(params) {
  if (isMock()) return mock(getMockAnalytics().season, 160);
  return request('/analytics/season', { data: params });
}

/** 热力网格 —— P10 页热力图 */
function getAnalyticsHeat(params) {
  if (isMock()) return mock(getMockAnalytics().heat, 160);
  return request('/analytics/heat', { data: params });
}

/** 模型预测 —— P10 页预测卡片 */
function getAnalyticsPrediction(params) {
  if (isMock()) return mock(getMockAnalytics().prediction, 160);
  return request('/analytics/prediction', { data: params });
}

/** 一次性拉取 P10 全部数据 */
function getAnalyticsAll(params) {
  if (isMock()) return mock(getMockAnalytics(), 180);
  return request('/analytics/all', { data: params });
}

/* ===========================================================================
 * 用户
 * POST /api/v1/user/favorites     { type:'spot'|'route', targetId, favorite }
 * POST /api/v1/user/trips          保存自定义行程
 * GET  /api/v1/user/favorites
 * 对应表：t_user, t_user_favorite, t_user_trip
 * ========================================================================= */
function syncFavorite(type, targetId, favorite) {
  if (isMock()) return mock({ ok: true });
  return request('/user/favorites', {
    method: 'POST',
    data: { type: type, targetId: targetId, favorite: favorite }
  });
}

function saveTrip(payload) {
  if (isMock()) return mock({ ok: true, tripId: 'mock_' + Date.now() });
  return request('/user/trips', { method: 'POST', data: payload });
}

function getTrips() {
  if (isMock()) return mock({ list: [], total: 0 });
  return request('/user/trips');
}

function getFavorites() {
  if (isMock()) return mock({ spotIds: [], routeIds: [] });
  return request('/user/favorites');
}

/* ===========================================================================
 * 登录注册 + 埋点
 * POST /api/v1/user/login       { phone, password } → { token, user }
 * POST /api/v1/user/register    { phone, password, nickname } → { token, user }
 * POST /api/v1/user/log         单条埋点
 * POST /api/v1/user/log/batch   批量埋点 { list: [...] }
 * ========================================================================= */
function login(phone, password) {
  if (isMock()) {
    return mock({
      token: 'mock_token',
      user: { id: 1, phone: phone, nickname: '游客' + String(phone).slice(-4), avatar: '' }
    });
  }
  return request('/user/login', { method: 'POST', data: { phone: phone, password: password } });
}

function register(phone, password, nickname) {
  if (isMock()) {
    return mock({
      token: 'mock_token',
      user: { id: 1, phone: phone, nickname: nickname || '游客' + String(phone).slice(-4), avatar: '' }
    });
  }
  return request('/user/register', {
    method: 'POST',
    data: { phone: phone, password: password, nickname: nickname || '' }
  });
}

function reportLog(item) {
  if (isMock()) return mock({ ok: true });
  return request('/user/log', { method: 'POST', data: item });
}

function reportEvents(list) {
  const items = list || [];
  if (isMock()) return mock({ ok: true, count: items.length });
  return request('/user/log/batch', { method: 'POST', data: { list: items } });
}

/* ===========================================================================
 * 数据分析页的本地占位数据（仅 mock 模式使用）
 * 字段结构与后端接口返回体严格一致，后端上线后直接被真实数据替换。
 * ========================================================================= */
function getMockAnalytics() {
  return {
    updatedAt: '2026-05-20 10:00',
    source: 'mock',
    overview: {
      list: [
        { key: 'visitors', label: '年游客量', value: '1286', unit: '万人次', delta: '+12.4%', trend: 'up' },
        { key: 'avgStay', label: '平均停留', value: '2.8', unit: '天', delta: '+0.3', trend: 'up' },
        { key: 'hotSpot', label: '最热景点', value: '梵净山', unit: '', delta: '+18.6%', trend: 'up' },
        { key: 'satisfaction', label: '游客满意度', value: '96.2', unit: '%', delta: '+1.8', trend: 'up' }
      ]
    },
    trend: {
      list: [
        { label: '1月', value: 62 },
        { label: '2月', value: 78 },
        { label: '3月', value: 88 },
        { label: '4月', value: 104 },
        { label: '5月', value: 128 },
        { label: '6月', value: 116 },
        { label: '7月', value: 142 },
        { label: '8月', value: 151 },
        { label: '9月', value: 119 },
        { label: '10月', value: 96 },
        { label: '11月', value: 74 },
        { label: '12月', value: 88 }
      ],
      unit: '万人次'
    },
    district: {
      list: [
        { label: '梵净山', value: 318 },
        { label: '江口县', value: 262 },
        { label: '石阡县', value: 176 },
        { label: '玉屏县', value: 154 },
        { label: '万山区', value: 121 },
        { label: '德江县', value: 96 },
        { label: '沿河县', value: 88 },
        { label: '思南县', value: 71 }
      ],
      unit: '万人次'
    },
    category: {
      list: [
        { label: '自然风光', value: 38 },
        { label: '民族村寨', value: 24 },
        { label: '温泉康养', value: 18 },
        { label: '古镇人文', value: 12 },
        { label: '美食街区', value: 8 }
      ],
      unit: '%'
    },
    ranking: {
      list: [
        { rank: 1, name: '梵净山', score: 4.9, visitors: 318 },
        { rank: 2, name: '中南门古城', score: 4.8, visitors: 262 },
        { rank: 3, name: '苗王城', score: 4.7, visitors: 218 },
        { rank: 4, name: '石阡温泉', score: 4.6, visitors: 176 },
        { rank: 5, name: '亚木沟', score: 4.6, visitors: 154 }
      ]
    },
    season: {
      list: [
        { label: '春', value: 78, note: '杜鹃花期' },
        { label: '夏', value: 95, note: '避暑旺季' },
        { label: '秋', value: 88, note: '彩林最佳' },
        { label: '冬', value: 46, note: '雪景温泉' }
      ],
      unit: '指数'
    },
    heat: {
      list: [
        { row: 0, col: 0, value: 12 },
        { row: 0, col: 1, value: 26 },
        { row: 0, col: 2, value: 38 },
        { row: 0, col: 3, value: 31 },
        { row: 1, col: 0, value: 18 },
        { row: 1, col: 1, value: 44 },
        { row: 1, col: 2, value: 92 },
        { row: 1, col: 3, value: 57 },
        { row: 2, col: 0, value: 9 },
        { row: 2, col: 1, value: 33 },
        { row: 2, col: 2, value: 76 },
        { row: 2, col: 3, value: 41 },
        { row: 3, col: 0, value: 7 },
        { row: 3, col: 1, value: 21 },
        { row: 3, col: 2, value: 48 },
        { row: 3, col: 3, value: 22 }
      ],
      rows: 4,
      cols: 4
    },
    prediction: {
      list: [
        { label: '未来 30 日客流预测', value: '峰值 151 万人次', advice: '7 月中旬建议增开 2 条运力' },
        { label: '推荐加码景区', value: '亚木沟 · 石阡温泉', advice: '搜索热度环比 +26%' },
        { label: '淡季营销建议', value: '11 月 — 12 月', advice: '温泉 + 雪景主题投放' }
      ]
    }
  };
}

/** AI 管家「咪噜」：预设提示词 */
function getMiluPrompts() {
  if (isMock()) {
    return mock({
      list: [
        { icon: 'sun', text: '铜仁今天天气适合玩什么项目？' },
        { icon: 'mountain', text: '梵净山今天人多不多？' },
        { icon: 'route', text: '梵净山哪条路好爬一些？' }
      ]
    });
  }
  return request('/ai/prompts');
}

/** AI 管家「咪噜」：对话（DeepSeek / 小米 MiMo，后端自动选择） */
function chatWithMilu(payload) {
  if (isMock()) {
    return mock({
      reply: '咪噜来啦～现在是本地演示模式，接入后端后咪噜就能回答你啦。',
      provider: '本地演示',
      model: 'mock'
    });
  }
  return request('/ai/chat', { method: 'POST', data: payload, timeout: 60000 });
}

module.exports = {
  // 基础
  request,
  isMock,
  toImageUrl,
  toIconUrl,
  // 景点
  getSpots,
  getSpot,
  getRelatedSpots,
  // 路线
  getRoutes,
  getRoute,
  generateCustomRoute,
  // 文化
  getFoods,
  getFolk,
  getFestivals,
  getEthnic,
  getSeasons,
  getBanners,
  getNotices,
  // 搜索
  search,
  // 数据分析（后端 Python 分析模块）
  getAnalyticsOverview,
  getAnalyticsTrend,
  getAnalyticsDistrict,
  getAnalyticsCategory,
  getAnalyticsRanking,
  getAnalyticsSeason,
  getAnalyticsHeat,
  getAnalyticsPrediction,
  getAnalyticsAll,
  // 用户
  syncFavorite,
  saveTrip,
  getTrips,
  getFavorites,
  // 登录注册 + 埋点
  login,
  register,
  reportLog,
  reportEvents,
  // AI 管家「咪噜」
  getMiluPrompts,
  chatWithMilu
};
