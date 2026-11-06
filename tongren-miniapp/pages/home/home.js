/**
 * 首页 —— 对应原型 SCREEN home
 * 结构顺序：品牌栏 / 主视觉轮播 / 搜索入口 / 快捷入口 / 热门精选 / 铜仁味道 & 民俗 / 出游公告 / 品牌口号
 */
const api = require('../../common/api');
const config = require('../../common/config');

const app = getApp();

Page({
  data: {
    statusBar: app.globalData.statusBarHeight,

    icons: {
      brand: api.toIconUrl('brand', 'white'),
      sun: api.toIconUrl('sun', 'muted'),
      search: api.toIconUrl('search', 'muted'),
      chevron: api.toIconUrl('chevron', 'green800'),
      pin: api.toIconUrl('pin', 'brown'),
      star: api.toIconUrl('star', 'brown'),
      speaker: api.toIconUrl('speaker', 'green900'),
      spark: api.toIconUrl('spark', 'green900'),
      seal: api.toIconUrl('seal', 'sandink'),
      user: api.toIconUrl('users', 'muted')
    },

    user: app.globalData.user || null,
    showSplash: true,

    weather: {
      temp: config.weather.temp,
      desc: config.weather.desc
    },

    banners: [],
    heroIndex: 0,
    heroAutoplay: true,
    videoIndex: 1,

    quick: [
      { key: 'spots', label: '精选景点', type: 'tab', target: '/pages/spots/spots', iconUrl: api.toIconUrl('mountain', 'green700') },
      { key: 'routes', label: '路线推荐', type: 'tab', target: '/pages/routes/routes', iconUrl: api.toIconUrl('route', 'green700') },
      { key: 'tips', label: '出游贴士', type: 'navigate', target: '/pages/tips/tips', iconUrl: api.toIconUrl('book', 'green700') },
      { key: 'data', label: '数据分析', type: 'navigate', target: '/pages/data/data', iconUrl: api.toIconUrl('chart', 'green700') }
    ],

    rail: [],

    food: {
      kicker: 'TONGREN TASTE',
      name: '锅巴粉',
      desc: '一口焦香，铜仁人的清晨',
      imgUrl: api.toImageUrl('food-noodle.jpg')
    },

    notice: {
      badge: config.noticeBadge,
      list: (config.notices || []).map((text, i) => ({ id: i + 1, text: text }))
    },

    sealImgUrl: config.decoBase + 'deco-slogan-seal.png'
  },

  onLoad() {
    this.loadBanners();
    this.loadRail();
    this.loadFood();
    this.loadNotice();
    // 入场动画：1.8 秒后自动隐藏
    setTimeout(() => {
      this.setData({ showSplash: false });
    }, 1800);
  },

  onShow() {
    // 同步登录态（从 login 页返回时刷新）
    this.setData({ user: app.globalData.user || null });
    if (this.getTabBar && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 });
    }
    app.track('home_view');
  },

  /* ---------------- 数据加载 ---------------- */

  loadBanners() {
    api.getBanners()
      .then((res) => {
        const list = (res && res.list) || [];
        // 按图片去重（后端种子数据可能重复写入同一张图）
        const seen = {};
        const slides = [];
        list.forEach((b) => {
          const key = b.file || b.id;
          if (seen[key]) return;
          seen[key] = true;
          slides.push({
            id: 'img-' + b.id,
            kind: 'image',
            imgUrl: api.toImageUrl(b.file),
            eyebrow: b.eyebrow,
            title: b.title,
            meta: b.meta,
            linkId: b.link_id || b.linkId
          });
        });

        // 在第二页插入宣传片
        const videoSlide = {
          id: 'video-promo',
          kind: 'video',
          src: config.baseUrl + '/static/video/tongren-promo.mp4',
          poster: '/static/img/fanjingshan.jpg',
          eyebrow: 'TONGREN · 宣传片',
          title: '一眼铜仁 · 山水相逢',
          meta: '梵净山 · 苗寨 · 温泉 · 古城'
        };
        slides.splice(1, 0, videoSlide);

        this.setData({ banners: slides, videoIndex: 1 });
      })
      .catch(() => {
        this.setData({ banners: [] });
      });
  },

  loadRail() {
    api.getSpots()
      .then((res) => {
        const list = ((res && res.list) || []).slice(0, 6);
        this.setData({
          rail: list.map((s) => ({
            id: s.id,
            name: s.name,
            district: s.district,
            score: Number(s.score).toFixed(1),
            level: s.level || '',
            levelClass: s.level === '5A' ? 'gold' : 'green',
            imgUrl: api.toImageUrl(s.img)
          }))
        });
      })
      .catch(() => {
        this.setData({ rail: [] });
      });
  },

  loadFood() {
    api.getFoods()
      .then((res) => {
        const first = (res && res.list && res.list[0]) || null;
        if (!first) return;
        this.setData({
          'food.name': first.name,
          'food.imgUrl': api.toImageUrl(first.file)
        });
      })
      .catch(() => {});
  },

  loadNotice() {
    api.getNotices()
      .then((res) => {
        const list = (res && res.list) || [];
        if (!list.length) return;
        this.setData({
          'notice.list': list.map((n, i) => ({
            id: n.id || i + 1,
            text: n.title || n.text || ''
          }))
        });
      })
      .catch(() => {});
  },

  /* ---------------- 交互 ---------------- */

  onHeroChange(e) {
    const index = e.detail.current;
    if (index === this.data.videoIndex) {
      // 停留在视频页时暂停自动轮播，避免视频被切走
      this.setData({ heroIndex: index, heroAutoplay: false });
    } else if (index !== this.data.heroIndex) {
      this.setData({ heroIndex: index, heroAutoplay: true });
    }
  },

  onVideoPlay() {
    this.setData({ heroAutoplay: false });
  },

  onVideoPause() {
    this.setData({ heroAutoplay: true });
  },

  onDotTap(e) {
    const index = Number(e.currentTarget.dataset.index);
    if (index !== this.data.heroIndex) {
      this.setData({ heroIndex: index, heroAutoplay: index !== this.data.videoIndex });
    }
  },

  onBannerTap(e) {
    this.openSpot(e.currentTarget.dataset.id);
  },

  onSpotTap(e) {
    this.openSpot(e.currentTarget.dataset.id);
  },

  openSpot(id) {
    if (id === undefined || id === null || id === '') return;
    app.track('home_open_spot', { id: id });
    wx.navigateTo({ url: '/pages/spot-detail/spot-detail?id=' + id });
  },

  onSearchTap() {
    app.track('home_search_click');
    wx.navigateTo({ url: '/pages/search/search' });
  },

  onQuickTap(e) {
    const key = e.currentTarget.dataset.type;
    const item = this.data.quick.filter((q) => q.key === key)[0];
    if (!item) return;
    if (item.type === 'tab') {
      wx.switchTab({ url: item.target });
    } else {
      wx.navigateTo({ url: item.target });
    }
  },

  onSpotsTab() {
    wx.switchTab({ url: '/pages/spots/spots' });
  },

  onFoodTap() {
    wx.navigateTo({ url: '/pages/food/food' });
  },

  onTipsTap() {
    wx.navigateTo({ url: '/pages/tips/tips' });
  },

  onNoticeTap() {
    wx.navigateTo({ url: '/pages/tips/tips' });
  },

  onLoginTap() {
    app.track('home_login_click', { page: 'pages/home/home' });
    wx.navigateTo({ url: '/pages/login/login' });
  }
});
