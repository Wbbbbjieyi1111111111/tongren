/**
 * 关于我们 —— 对应原型 SCREEN about
 * GET /api/v1/ethnic  →  t_ethnic
 */
const api = require('../../common/api');
const config = require('../../common/config');

const app = getApp();

/** 出游须知（后端可改为 GET /api/v1/about/notices → t_about_notice） */
const INFOS = [
  { label: '景区实名预约', value: '出发前确认景区官方预约渠道，凭码入园', icon: 'shield-green700' },
  { label: '山区气候多变', value: '四季皆需备一件外套，雨季带好雨具', icon: 'leaf-green700' },
  { label: '尊重民族习俗', value: '拍摄人物前请先征得同意，入寨随俗', icon: 'users-green700' },
  { label: '文旅咨询热线', value: '0856-XXXXXXX（占位）· 09:00–17:30', icon: 'phone-green700' }
];

Page({
  data: {
    statusBar: app.globalData.statusBarHeight,
    decoBrand: config.decoBase + 'deco-about-brand.png',
    icons: {
      brand: api.toIconUrl('brand', 'white'),
      message: api.toIconUrl('message', 'green700'),
      chevron: api.toIconUrl('chevron', 'ink'),
      chart: api.toIconUrl('chart', 'green800')
    },
    infos: INFOS.map((it) => ({
      label: it.label,
      value: it.value,
      iconUrl: api.toIconUrl(it.icon.split('-')[0], it.icon.split('-')[1])
    })),
    ethnic: []
  },

  onLoad() {
    this.loadEthnic();
  },

  onShow() {
    if (this.getTabBar && this.getTabBar()) {
      this.getTabBar().setData({ selected: 3 });
    }
    app.track('about_view');
  },

  loadEthnic() {
    api.getEthnic()
      .then((res) => {
        const list = (res && res.list) || [];
        this.setData({
          ethnic: list.map((e) => ({
            name: e.name,
            keys: e.keys,
            desc: e.desc,
            imgUrl: api.toImageUrl(e.file)
          }))
        });
      })
      .catch(() => {
        this.setData({ ethnic: [] });
      });
  },

  onEthnicTap() {
    wx.navigateTo({ url: '/pages/food/food' });
  },

  onFeedbackTap() {
    app.toast('留言功能筹备中');
  },

  onTipsTap() {
    wx.navigateTo({ url: '/pages/tips/tips' });
  },

  onDataTap() {
    wx.navigateTo({ url: '/pages/data/data' });
  }
});
