/**
 * 铜仁味道 · 民俗 —— 对应原型 SCREEN food
 * GET /api/v1/foods / folk / festivals  →  t_food / t_folk / t_festival
 */
const api = require('../../common/api');

const app = getApp();

Page({
  data: {
    statusBar: app.globalData.statusBarHeight,
    icons: {
      back: api.toIconUrl('arrow-left', 'ink'),
      pin: api.toIconUrl('pin', 'brown')
    },
    activeTab: 'food',
    foods: [],
    folk: [],
    fests: []
  },

  onLoad() {
    this.loadFoods();
    this.loadFolk();
    this.loadFests();
  },

  loadFoods() {
    api.getFoods()
      .then((res) => {
        const list = (res && res.list) || [];
        this.setData({
          foods: list.map((f) => ({
            name: f.name,
            tag: f.tag,
            desc: f.desc,
            imgUrl: api.toImageUrl(f.file)
          }))
        });
      })
      .catch(() => {
        this.setData({ foods: [] });
      });
  },

  loadFolk() {
    api.getFolk()
      .then((res) => {
        const list = (res && res.list) || [];
        this.setData({
          folk: list.map((f, i) => ({
            name: f.name,
            level: f.level,
            desc: f.desc,
            num: ('0' + (i + 1)).slice(-2),
            levelClass: f.level.indexOf('国家') === 0 ? 'tag-green' : 'tag-soft'
          }))
        });
      })
      .catch(() => {
        this.setData({ folk: [] });
      });
  },

  loadFests() {
    api.getFestivals()
      .then((res) => {
        const list = (res && res.list) || [];
        this.setData({
          fests: list.map((f) => ({
            month: f.month,
            day: f.day,
            name: f.name,
            place: f.place,
            desc: f.desc
          }))
        });
      })
      .catch(() => {
        this.setData({ fests: [] });
      });
  },

  onTabTap(e) {
    const tab = e.currentTarget.dataset.tab;
    if (tab === this.data.activeTab) return;
    this.setData({ activeTab: tab });
    app.track('food_tab', { tab: tab });
  },

  onBack() {
    wx.navigateBack();
  }
});
