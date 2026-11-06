/**
 * 数据分析页
 * 图表由后端 pandas + matplotlib 生成 PNG，进入页面时动态加载并以错峰动画依次呈现
 * KPI 数据来自 GET /api/v1/analytics/overview
 */
const api = require('../../common/api');
const config = require('../../common/config');

const app = getApp();

const CHART_BASE = config.baseUrl + '/static/charts/';

const CHART_DEFS = [
    { key: 'ranking', title: '景点热度排行', sub: 'Top 10 · 真实浏览量', file: 'ranking.png' },
    { key: 'trend', title: '游客访问趋势', sub: '近 30 天走势', file: 'trend.png' },
    { key: 'category', title: '游客偏好统计', sub: '景点品类占比', file: 'category.png' }
];

Page({
  data: {
    statusBar: app.globalData.statusBarHeight,
    decoUrl: config.decoBase + 'deco-data-banner.png',
    icons: {
      back: api.toIconUrl('arrow-left', 'ink'),
      chart: api.toIconUrl('chart', 'green700')
    },
    kpis: [
      { label: '今日访问量', value: '--', unit: '' },
      { label: '累计游客关注', value: '--', unit: '' },
      { label: '景点热度均值', value: '--', unit: '' },
      { label: '路线浏览量', value: '--', unit: '' }
    ],
    charts: CHART_DEFS.map((c) => ({
      key: c.key,
      title: c.title,
      sub: c.sub,
      url: '',
      loaded: false
    })),
    updatedAt: '',
    refreshing: false
  },

  onLoad() {
    this.loadKpis();
  },

  onShow() {
    // 每次进入页面都重新加载，保证图表是最新生成的
    this.loadCharts();
  },

  /** KPI 概览 */
  loadKpis() {
    api.getAnalyticsOverview()
      .then((res) => {
        const list = (res && (res.list || res.stats)) || [];
        if (!list.length) return;
        this.setData({
          kpis: list.slice(0, 4).map((s) => ({
            label: s.label || '',
            value: s.value != null ? String(s.value) : '--',
            unit: s.unit || ''
          }))
        });
      })
      .catch(() => {});
  },

  /** 图表：带时间戳强制刷新，先把 loaded 置 false 触发骨架屏 */
  loadCharts() {
    const ts = Date.now();
    const charts = this.data.charts.map((c) => {
      const def = CHART_DEFS.find((d) => d.key === c.key);
      return Object.assign({}, c, {
        url: CHART_BASE + def.file + '?t=' + ts,
        loaded: false
      });
    });
    this.setData({ charts: charts, updatedAt: this._now() });
  },

  onChartLoad(e) {
    const index = Number(e.currentTarget.dataset.index);
    const key = 'charts[' + index + '].loaded';
    this.setData({ [key]: true });
  },

  onChartTap(e) {
    const url = e.currentTarget.dataset.url;
    if (!url) return;
    wx.previewImage({ current: url, urls: [url] });
  },

  _now() {
    const d = new Date();
    const pad = (n) => (n < 10 ? '0' + n : '' + n);
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate())
      + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes());
  },

  onRefresh() {
    if (this.data.refreshing) return;
    this.setData({ refreshing: true });
    wx.showLoading({ title: '正在拉取最新数据', mask: true });
    this.loadKpis();
    this.loadCharts();
    setTimeout(() => {
      wx.hideLoading();
      this.setData({ refreshing: false });
      app.toast('数据已刷新');
    }, 900);
  },

  onBack() {
    wx.navigateBack();
  }
});
