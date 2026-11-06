/**
 * 搜索页 —— 对应原型 SEARCH LAYER
 * 三种态：default（热门搜索 + 历史搜索 + 为你推荐）/ result（结果列表）/ empty（空态）
 */
const api = require('../../common/api');
const config = require('../../common/config');

const app = getApp();

const HISTORY_KEY = 'tongren_search_history';
const HISTORY_MAX = 10;

Page({
  data: {
    statusBar: app.globalData.statusBarHeight,

    icons: {
      back: api.toIconUrl('arrow-left', 'ink'),
      search: api.toIconUrl('search', 'ink'),
      clear: api.toIconUrl('x', 'muted'),
      chevron: api.toIconUrl('chevron', 'ink')
    },

    keyword: '',
    mode: 'default',
    hot: (config.hotKeywords || []).slice(),
    history: [],
    recommend: [],
    results: [],
    total: 0
  },

  onLoad() {
    this.setData({ history: this.readHistory() });
    this.loadRecommend();
  },

  /* ---------------- 历史记录 ---------------- */

  readHistory() {
    try {
      const list = wx.getStorageSync(HISTORY_KEY);
      return Array.isArray(list) ? list : [];
    } catch (e) {
      return [];
    }
  },

  writeHistory(list) {
    try {
      wx.setStorageSync(HISTORY_KEY, list);
    } catch (e) {
      // 存储失败时忽略，历史记录仅保留在内存中
    }
  },

  pushHistory(keyword) {
    const list = this.readHistory().filter((x) => x !== keyword);
    list.unshift(keyword);
    const next = list.slice(0, HISTORY_MAX);
    this.writeHistory(next);
    this.setData({ history: next });
  },

  /* ---------------- 数据加载 ---------------- */

  loadRecommend() {
    api.getSpots()
      .then((res) => {
        const list = ((res && res.list) || []).slice(0, 3);
        this.setData({ recommend: list.map((s) => this.toRow(s)) });
      })
      .catch(() => {
        this.setData({ recommend: [] });
      });
  },

  toRow(spot) {
    return {
      id: spot.id,
      name: spot.name,
      imgUrl: api.toImageUrl(spot.img),
      meta: spot.district + ' · ' + spot.cat + ' · ' + Number(spot.score).toFixed(1) + ' 分'
    };
  },

  /* ---------------- 交互 ---------------- */

  onInput(e) {
    const value = e.detail.value || '';
    this.setData({ keyword: value });
    if (!value.trim()) {
      this.resetToDefault();
      return;
    }
    this.doSearch(value);
  },

  onConfirm(e) {
    const value = (e.detail.value || this.data.keyword || '').trim();
    if (!value) {
      this.resetToDefault();
      return;
    }
    this.setData({ keyword: value });
    this.doSearch(value);
  },

  onClear() {
    this.setData({ keyword: '' });
    this.resetToDefault();
  },

  onChipTap(e) {
    const q = e.currentTarget.dataset.q;
    if (!q) return;
    this.setData({ keyword: q });
    this.doSearch(q);
  },

  onClearHistory() {
    this.writeHistory([]);
    this.setData({ history: [] });
  },

  onSpotTap(e) {
    const id = e.currentTarget.dataset.id;
    if (id === undefined || id === null || id === '') return;
    app.track('search_open_spot', { id: id });
    wx.navigateTo({ url: '/pages/spot-detail/spot-detail?id=' + id });
  },

  onBack() {
    wx.navigateBack({ delta: 1 });
  },

  /* ---------------- 状态切换 ---------------- */

  resetToDefault() {
    this.setData({ mode: 'default', results: [], total: 0 });
  },

  doSearch(keyword) {
    const q = String(keyword || '').trim();
    if (!q) {
      this.resetToDefault();
      return;
    }
    api.search(q)
      .then((res) => {
        const list = (res && res.list) || [];
        this.setData({
          results: list.map((s) => this.toRow(s)),
          total: list.length,
          mode: list.length ? 'result' : 'empty'
        });
        this.pushHistory(q);
      })
      .catch(() => {
        // 接口失败兜底为空态，不白屏
        this.setData({ results: [], total: 0, mode: 'empty' });
      });
  }
});
