/**
 * 景点详情 —— 对应原型 SCREEN spot-detail
 * GET /api/v1/spots/{id}  →  t_spot / t_spot_image / t_spot_tip / t_spot_food
 */
const api = require('../../common/api');

const app = getApp();

const INFO_META = [
  { key: 'ticket', label: '参考门票', icon: 'ticket-muted' },
  { key: 'open', label: '开放时间', icon: 'clock-muted' },
  { key: 'traffic', label: '交通指南', icon: 'car-muted' },
  { key: 'duration', label: '游玩时长', icon: 'calendar-muted' }
];

Page({
  data: {
    statusBar: app.globalData.statusBarHeight,
    icons: {
      back: api.toIconUrl('arrow-left', 'ink'),
      heart: api.toIconUrl('heart', 'brown'),
      heartOn: api.toIconUrl('heart', 'red'),
      pin: api.toIconUrl('pin', 'brown'),
      star: api.toIconUrl('star', 'brown')
    },
    spotId: null,
    spot: { name: '', slogan: '', intro: [], tips: [] },
    images: [],
    slide: 0,
    levelText: '',
    levelCls: 'green',
    infoCells: [],
    foods: [],
    isFav: false
  },

  onLoad(options) {
    const id = Number(options && options.id) || 1;
    this.setData({ spotId: id });
    this.loadSpot(id);
  },

  loadSpot(id) {
    api.getSpot(id)
      .then((s) => {
        if (!s) {
          app.toast('景点信息不存在');
          return;
        }
        // 防御性兜底：后端字段若为字符串/null，统一转数组，避免渲染报错
        const images = Array.isArray(s.images) ? s.images : (s.images ? String(s.images).split(/\s+/) : (s.img ? [s.img] : []));
        const intro = Array.isArray(s.intro) ? s.intro : (s.intro ? [String(s.intro)] : []);
        const tips = Array.isArray(s.tips) ? s.tips : (s.tips ? [String(s.tips)] : []);
        const foods = Array.isArray(s.foods) ? s.foods : (s.foods ? [String(s.foods)] : []);
        this.setData({
          spot: {
            name: s.name || '',
            slogan: s.slogan || '',
            cat: s.cat || '',
            district: s.district || '',
            score: s.score != null ? Number(s.score).toFixed(1) : '0.0',
            level: s.level || '',
            intro: intro,
            tips: tips
          },
          images: images.map((f) => api.toImageUrl(f)).filter(Boolean),
          slide: 0,
          levelText: s.level || '红色',
          levelCls: s.level === '5A' ? 'gold' : (s.level ? 'green' : 'red'),
          infoCells: INFO_META.map((m) => {
            const parts = m.icon.split('-');
            return {
              key: m.key,
              label: m.label,
              value: s[m.key] || '',
              iconUrl: api.toIconUrl(parts[0], parts[1] || 'muted')
            };
          }),
          isFav: !!app.globalData.spotFavorites[id]
        });
        this.loadFoods(foods);
      })
      .catch((err) => {
        console.error('loadSpot error:', err);
        app.toast('景点信息加载失败');
      });
  },

  loadFoods(names) {
    api.getFoods()
      .then((res) => {
        const all = (res && res.list) || [];
        const picked = names.map((n) => all.filter((f) => f.name === n)[0] || all[0]).filter(Boolean);
        this.setData({
          foods: picked.map((f) => ({
            name: f.name,
            tag: f.tag,
            imgUrl: api.toImageUrl(f.file)
          }))
        });
      })
      .catch(() => {
        this.setData({ foods: [] });
      });
  },

  onSlideChange(e) {
    this.setData({ slide: e.detail.current });
  },

  onDotTap(e) {
    const index = Number(e.currentTarget.dataset.index);
    if (index !== this.data.slide) {
      this.setData({ slide: index });
    }
  },

  onFavTap() {
    const id = this.data.spotId;
    const on = app.toggleSpotFavorite(id);
    api.syncFavorite('spot', id, on).catch(() => {});
    this.setData({ isFav: on });
    app.toast(on ? '已收藏，稍后可在“我们”中查看' : '已取消收藏');
    app.track('spot_favorite', { id: id, favorite: on });
  },

  onFoodTap() {
    wx.navigateTo({ url: '/pages/food/food' });
  },

  onConsultTap() {
    app.toast('交通咨询功能筹备中');
  },

  /** 找到包含该景点的推荐路线，否则回落到第 2 条 */
  onRouteTap() {
    const spotId = this.data.spotId;
    api.getRoutes()
      .then((res) => {
        const list = (res && res.list) || [];
        const match = list.filter((r) => (r.spotIds || []).indexOf(spotId) !== -1)[0];
        wx.navigateTo({ url: '/pages/route-detail/route-detail?id=' + (match ? match.id : 2) });
      })
      .catch(() => {
        wx.navigateTo({ url: '/pages/route-detail/route-detail?id=2' });
      });
  },

  onBack() {
    wx.navigateBack();
  }
});
