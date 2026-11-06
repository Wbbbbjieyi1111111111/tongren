/**
 * 路线详情 —— 对应原型 SCREEN route-detail
 * GET /api/v1/routes/{id}  →  t_route / t_route_plan / t_route_item / t_route_stay / t_route_avoid
 */
const api = require('../../common/api');

const app = getApp();

Page({
  data: {
    statusBar: app.globalData.statusBarHeight,
    icons: {
      back: api.toIconUrl('arrow-left', 'ink'),
      heart: api.toIconUrl('heart', 'ink'),
      heartOn: api.toIconUrl('heart', 'red'),
      home: api.toIconUrl('home', 'green700'),
      info: api.toIconUrl('info', 'warn')
    },
    routeId: null,
    route: {
      name: '',
      days: 0,
      suitable: '',
      coverUrl: '',
      plan: [],
      stays: [],
      avoid: [],
      spotIds: []
    },
    stats: [],
    spots: [],
    isFav: false
  },

  onLoad(options) {
    const id = Number(options && options.id) || 2;
    this.setData({ routeId: id });
    this.loadRoute(id);
  },

  loadRoute(id) {
    api.getRoute(id)
      .then((r) => {
        if (!r) return;
        this.setData({
          route: {
            name: r.name,
            days: r.days,
            suitable: r.suitable,
            suitShort: r.suitShort,
            difficulty: r.difficulty,
            coverUrl: api.toImageUrl(r.cover),
            plan: r.plan || [],
            stays: r.stays || [],
            avoid: r.avoid || [],
            spotIds: r.spotIds || []
          },
          stats: [
            { value: r.days + ' 天', label: '行程天数' },
            { value: (r.spotIds || []).length + ' 个', label: '打卡点' },
            { value: r.suitShort, label: '适合' },
            { value: r.difficulty, label: '难度' }
          ],
          isFav: !!app.globalData.routeFavorites[id]
        });
        this.loadSpots(r.spotIds || []);
      })
      .catch(() => {
        app.toast('路线信息加载失败');
      });
  },

  loadSpots(ids) {
    api.getSpots()
      .then((res) => {
        const all = (res && res.list) || [];
        const list = ids
          .map((sid) => all.filter((s) => s.id === sid)[0])
          .filter(Boolean)
          .map((s) => ({
            id: s.id,
            name: s.name,
            district: s.district,
            imgUrl: api.toImageUrl(s.img)
          }));
        this.setData({ spots: list });
      })
      .catch(() => {
        this.setData({ spots: [] });
      });
  },

  onFavTap() {
    const id = this.data.routeId;
    const on = app.toggleRouteFavorite(id);
    api.syncFavorite('route', id, on).catch(() => {});
    this.setData({ isFav: on });
    app.toast(on ? '已收藏路线' : '已取消收藏');
    app.track('route_favorite', { id: id, favorite: on });
  },

  onSpotTap(e) {
    wx.navigateTo({ url: '/pages/spot-detail/spot-detail?id=' + e.currentTarget.dataset.id });
  },

  /** 把本路线的打卡点带入自定义页 */
  onAddCustom() {
    wx.navigateTo({ url: '/pages/custom/custom?routeId=' + this.data.routeId });
  },

  onBack() {
    wx.navigateBack();
  }
});
