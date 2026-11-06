/**
 * 大美铜仁 · 微信小程序
 * 全局入口：配置、运行态、全局收藏、埋点上报钩子
 */
const config = require('./common/config');
const api = require('./common/api');

App({
  globalData: {
    // 运行模式：'mock' 使用本地模拟数据，'api' 走真实后端
    mode: config.mode,
    // 后端服务地址（切换到 api 模式后生效）
    baseUrl: config.baseUrl,
    // 系统信息（用于 rpx 之外的安全区适配）
    statusBarHeight: 20,
    windowHeight: 667,
    // 全局收藏（本地存储，后端接入后改为接口同步）
    spotFavorites: {},
    routeFavorites: {},
    // 埋点队列（flushTrack 批量上报 POST /user/log/batch）
    events: [],
    // 登录态（与 wx.storage 的 token / user 保持同步）
    token: '',
    user: null
  },

  onLaunch() {
    this.loadFavorites();
    this.initSystemInfo();
    this.restoreLoginState();
    // 预热统计数据分析接口，失败静默降级，不影响首屏
    this.warmupAnalytics();
  },

  onHide() {
    // 切后台冲刷埋点队列
    this.flushTrack();
  },

  restoreLoginState() {
    try {
      const token = wx.getStorageSync('token');
      const user = wx.getStorageSync('user');
      if (token) {
        this.globalData.token = token;
        this.globalData.user = user || null;
      }
    } catch (e) {
      // 读缓存失败按未登录处理
    }
  },

  /** 登录成功：写全局态 + 本地缓存 */
  setLoginState(token, user) {
    this.globalData.token = token;
    this.globalData.user = user || null;
    try {
      wx.setStorageSync('token', token);
      wx.setStorageSync('user', user || null);
    } catch (e) {}
  },

  /** 退出登录：清全局态 + 本地缓存 */
  clearLoginState() {
    this.globalData.token = '';
    this.globalData.user = null;
    try {
      wx.removeStorageSync('token');
      wx.removeStorageSync('user');
    } catch (e) {}
  },

  initSystemInfo() {
    try {
      const info = wx.getWindowInfo ? wx.getWindowInfo() : wx.getSystemInfoSync();
      this.globalData.statusBarHeight = info.statusBarHeight || 20;
      this.globalData.windowHeight = info.windowHeight || 667;
    } catch (e) {
      // 取不到系统信息时使用默认值，不阻塞启动
    }
  },

  loadFavorites() {
    try {
      const spot = wx.getStorageSync('tongren_fav_spots');
      const route = wx.getStorageSync('tongren_fav_routes');
      this.globalData.spotFavorites = spot || {};
      this.globalData.routeFavorites = route || {};
    } catch (e) {
      this.globalData.spotFavorites = {};
      this.globalData.routeFavorites = {};
    }
  },

  persistFavorites() {
    try {
      wx.setStorageSync('tongren_fav_spots', this.globalData.spotFavorites);
      wx.setStorageSync('tongren_fav_routes', this.globalData.routeFavorites);
    } catch (e) {
      // 存储失败时忽略，收藏状态仍保留在内存中
    }
  },

  toggleSpotFavorite(id) {
    const favs = this.globalData.spotFavorites;
    const on = !favs[id];
    if (on) {
      favs[id] = Date.now();
    } else {
      delete favs[id];
    }
    this.persistFavorites();
    // 登录态下同步后端（未登录仅本地收藏）
    if (this.globalData.token) {
      api.syncFavorite('spot', id, on).catch(() => {});
    }
    return on;
  },

  toggleRouteFavorite(id) {
    const favs = this.globalData.routeFavorites;
    const on = !favs[id];
    if (on) {
      favs[id] = Date.now();
    } else {
      delete favs[id];
    }
    this.persistFavorites();
    // 登录态下同步后端（未登录仅本地收藏）
    if (this.globalData.token) {
      api.syncFavorite('route', id, on).catch(() => {});
    }
    return on;
  },

  /**
   * 埋点：进入内存队列，由 flushTrack 批量上报 POST /user/log/batch
   * 字段与 t_user_log 对齐：event / targetType / targetId / keyword / page / channel / ts
   */
  track(event, payload) {
    const p = payload || {};
    const item = {
      event: event,
      targetType: p.targetType || '',
      targetId: p.targetId || 0,
      keyword: p.keyword || '',
      page:
        p.page ||
        (getCurrentPages().length
          ? getCurrentPages()[getCurrentPages().length - 1].route
          : ''),
      channel: 'miniapp',
      ts: Date.now()
    };
    this.globalData.events.push(item);
    if (this.globalData.events.length >= 20) {
      this.flushTrack();
    }
    return item;
  },

  /** 批量上报埋点：成功才出队，失败保留队列待重试（不丢事件） */
  flushTrack() {
    const queue = this.globalData.events;
    if (!queue.length || this._trackFlushing) return;
    const batch = queue.slice(0, 100);
    this._trackFlushing = true;
    api
      .reportEvents(batch)
      .then(() => {
        this.globalData.events = this.globalData.events.slice(batch.length);
      })
      .catch(() => {
        // 上报失败：保留队列下次冲刷；仅在积压过多时丢最旧的防内存膨胀
        if (this.globalData.events.length > 500) {
          this.globalData.events = this.globalData.events.slice(-500);
        }
      })
      .then(() => {
        this._trackFlushing = false;
      });
  },

  warmupAnalytics() {
    // 数据分析页所需的预聚合数据预热；失败时页面自行降级为占位图
    const api = require('./common/api');
    api.getAnalyticsOverview()
      .then((res) => {
        this.globalData.analyticsOverview = res;
      })
      .catch(() => {
        this.globalData.analyticsOverview = null;
      });
  },

  toast(title, icon) {
    wx.showToast({
      title: title || '',
      icon: icon || 'none',
      duration: 1900
    });
  }
});
