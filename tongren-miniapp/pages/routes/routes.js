/**
 * 路线列表 —— 对应原型 SCREEN routes
 * GET /api/v1/routes  →  t_route / t_route_plan / t_route_item
 */
const api = require('../../common/api');
const config = require('../../common/config');

const app = getApp();

Page({
  data: {
    statusBar: app.globalData.statusBarHeight,
    decoUrl: config.decoBase + 'deco-custom-hero.png',
    icons: {
      cta: api.toIconUrl('chevron', 'cta'),
      users: api.toIconUrl('users', 'green700'),
      utensils: api.toIconUrl('utensils', 'brown'),
      info: api.toIconUrl('info', 'brown')
    },
    routes: []
  },

  onLoad() {
    this.loadRoutes();
  },

  onShow() {
    if (this.getTabBar && this.getTabBar()) {
      this.getTabBar().setData({ selected: 2 });
    }
    app.track('routes_view');
  },

  loadRoutes() {
    api.getRoutes()
      .then((res) => {
        const list = (res && res.list) || [];
        this.setData({
          routes: list.map((r) => ({
            id: r.id,
            name: r.name,
            days: r.days,
            suitable: r.suitable,
            overview: r.overview,
            foods: r.foods,
            tip: r.tip,
            coverUrl: api.toImageUrl(r.cover)
          }))
        });
      })
      .catch(() => {
        this.setData({ routes: [] });
      });
  },

  onCustomTap() {
    app.track('routes_custom_click');
    wx.navigateTo({ url: '/pages/custom/custom' });
  },

  onDetail(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/route-detail/route-detail?id=' + id });
  },

  onAddCustom(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/custom/custom?routeId=' + id });
  }
});
