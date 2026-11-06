/**
 * 全局配置
 *
 * 【后端接入方式】
 * 1. 把 mode 改为 'api'；
 * 2. 把 baseUrl 改成你的 Python 服务地址（需在微信公众平台配置 request 合法域名）；
 * 3. 所有页面会自动走 common/api.js 里的真实接口，不再读取 common/mock 下的数据。
 *
 * 后端技术栈约定：Python + MySQL，接口前缀统一 /api/v1，
 * 详细契约见 docs/API-CONTRACT.md，库表见 docs/schema.sql。
 */
module.exports = {
  // 'mock' = 本地模拟数据（当前默认，无需后端即可跑通全部界面）
  // 'api'  = 调用真实 Python 后端
  mode: 'api',

  // Python 后端服务地址（部署后替换）
  baseUrl: 'http://127.0.0.1:8000',

  // 请求超时（毫秒）
  timeout: 12000,

  // 接口版本前缀
  apiPrefix: '/api/v1',

  // 静态资源根目录
  imgBase: '/static/img/',
  iconBase: '/static/icons/',
  decoBase: '/static/deco/',

  // 首页天气（原型为静态占位，后端可改为 GET /api/v1/weather）
  weather: {
    temp: '22°',
    desc: '多云',
    aqi: '32 优'
  },

  // 公告（后端可替换为 GET /api/v1/notices）
  noticeBadge: '出游公告',
  notices: [
    '梵净山旺季需提前 1–3 天在官方渠道实名预约',
    '雨季山路湿滑，请携带防滑鞋与雨具'
  ],

  // 搜索热词
  hotKeywords: ['梵净山', '石阡温泉', '中南门', '苗王城', '亚木沟']
};
