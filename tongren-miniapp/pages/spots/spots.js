/**
 * 景点列表 —— 对应原型 SCREEN spots
 * 分类筛选 chips + 双列瀑布流（按贪心最短列分配，模拟原型 CSS columns）
 */
const api = require('../../common/api');

const app = getApp();

const CATS = ['全部', '自然风光', '古镇人文', '红色景点', '温泉休闲'];

/** 估算卡片高度：封面按 3:4 比例 + 文字块，用于瀑布流分列 */
function estimateHeight(spot) {
  return 300 + String(spot.brief || '').length * 6;
}

Page({
  data: {
    statusBar: app.globalData.statusBarHeight,
    cats: CATS,
    activeCat: '全部',
    colLeft: [],
    colRight: [],

    icons: {
      pin: api.toIconUrl('pin', 'brown'),
      star: api.toIconUrl('star', 'brown')
    }
  },

  onLoad() {
    this.allSpots = [];
    this.loadSpots();
  },

  onShow() {
    if (this.getTabBar && this.getTabBar()) {
      this.getTabBar().setData({ selected: 1 });
    }
    app.track('spots_view', { cat: this.data.activeCat });
  },

  loadSpots() {
    api.getSpots()
      .then((res) => {
        const list = (res && res.list) || [];
        this.allSpots = list.map((s) => ({
          id: s.id,
          name: s.name,
          brief: s.brief,
          district: s.district,
          cat: s.cat,
          score: Number(s.score).toFixed(1),
          imgUrl: api.toImageUrl(s.img),
          badgeText: s.level || '红色',
          badgeCls: s.level === '5A' ? 'gold' : (s.level ? 'green' : 'red')
        }));
        this.applyFilter(this.data.activeCat);
      })
      .catch(() => {
        this.allSpots = [];
        this.setData({ colLeft: [], colRight: [] });
      });
  },

  /** 过滤 + 贪心分两列（模拟 CSS multi-column 的视觉平衡） */
  applyFilter(cat) {
    const list = cat === '全部'
      ? this.allSpots.slice()
      : this.allSpots.filter((s) => s.cat === cat);

    const left = [];
    const right = [];
    let hLeft = 0;
    let hRight = 0;
    list.forEach((item) => {
      const h = estimateHeight(item);
      if (hLeft <= hRight) {
        left.push(item);
        hLeft += h;
      } else {
        right.push(item);
        hRight += h;
      }
    });

    this.setData({ colLeft: left, colRight: right });
  },

  onCatTap(e) {
    const cat = e.currentTarget.dataset.cat;
    if (cat === this.data.activeCat) return;
    this.setData({ activeCat: cat });
    this.applyFilter(cat);
    app.track('spots_filter', { cat: cat });
  },

  onSpotTap(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/spot-detail/spot-detail?id=' + id });
  }
});
