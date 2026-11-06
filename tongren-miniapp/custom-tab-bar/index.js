/**
 * 自定义 tabBar —— 对应原型 index.html 的 .tabbar
 * 4 个 tab：首页 / 景点 / 路线 / 我们
 * 页面在 onShow 里调用 getTabBar().setData({ selected: N }) 高亮当前项
 */
const config = require('../common/config');

const LIST = [
  { key: 'home', text: '首页', url: '/pages/home/home', icon: 'home' },
  { key: 'spots', text: '景点', url: '/pages/spots/spots', icon: 'mountain' },
  { key: 'routes', text: '路线', url: '/pages/routes/routes', icon: 'flag' },
  { key: 'about', text: '我们', url: '/pages/about/about', icon: 'seal' }
];

Component({
  options: {
    styleIsolation: 'apply-shared'
  },
  data: {
    selected: 0,
    list: LIST.map((it, index) => ({
      key: it.key,
      index: index,
      text: it.text,
      url: it.url,
      off: config.iconBase + it.icon + '-gray.png',
      on: config.iconBase + it.icon + '-green800.png'
    }))
  },
  attached() {
    const pages = getCurrentPages();
    if (!pages.length) return;
    const current = pages[pages.length - 1].route;
    const idx = LIST.findIndex((it) => it.url.replace(/^\//, '') === current);
    if (idx > -1 && idx !== this.data.selected) {
      this.setData({ selected: idx });
    }
  },
  methods: {
    onTap(e) {
      const { index, url } = e.currentTarget.dataset;
      const idx = Number(index);
      if (idx === this.data.selected) return;
      wx.switchTab({
        url: url,
        fail() {
          wx.navigateTo({ url: url });
        }
      });
    }
  }
});
