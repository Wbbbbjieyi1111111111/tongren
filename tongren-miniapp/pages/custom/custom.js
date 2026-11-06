/**
 * 自定义路线 —— 对应原型 SCREEN custom
 * 勾选景点 → 调整顺序 → POST /api/v1/routes/custom 生成行程 → 导出清单
 * 对应表：t_route(自定义) / t_route_item / t_user_trip
 */
const api = require('../../common/api');
const config = require('../../common/config');

const app = getApp();

const DEFAULT_PLACEHOLDER = '我的铜仁 N 日游';

// 铜仁市景点真实坐标（GCJ-02），用于地图标记
const SPOT_COORDS = {
  1: { latitude: 27.9239, longitude: 108.7096 },   // 梵净山
  2: { latitude: 27.8667, longitude: 108.7500 },   // 亚木沟
  3: { latitude: 27.8000, longitude: 108.8000 },   // 太平河
  4: { latitude: 28.0500, longitude: 109.2000 },   // 苗王城
  5: { latitude: 27.7256, longitude: 109.1898 },   // 中南门
  6: { latitude: 27.5167, longitude: 108.2333 },   // 石阡温泉
  7: { latitude: 27.4833, longitude: 108.2167 },   // 佛顶山温泉
  8: { latitude: 27.5167, longitude: 109.2000 },   // 朱砂古镇
  9: { latitude: 27.8500, longitude: 108.7333 },   // 云舍村
  10: { latitude: 27.8833, longitude: 108.7167 },  // 寨沙侗寨
  11: { latitude: 27.7250, longitude: 109.1900 },  // 周逸群故居
  12: { latitude: 27.9833, longitude: 108.6667 }   // 木黄会师
};

// 铜仁市中心坐标（地图初始中心）
const TONGREN_CENTER = { latitude: 27.7256, longitude: 109.1898 };

Page({
  data: {
    statusBar: app.globalData.statusBarHeight,
    decoUrl: config.decoBase + 'deco-map-card.png',
    icons: {
      back: api.toIconUrl('arrow-left', 'ink'),
      pin: api.toIconUrl('pin', 'green700'),
      check: api.toIconUrl('check', 'white'),
      route: api.toIconUrl('route', 'green600'),
      up: api.toIconUrl('up', 'muted'),
      down: api.toIconUrl('down', 'muted'),
      x: api.toIconUrl('x', 'red'),
      copy: api.toIconUrl('copy', 'green900'),
      spark: api.toIconUrl('spark', 'white')
    },
    spots: [],
    selected: [1, 4, 6, 8],
    selectList: [],
    orderList: [],
    generated: false,
    plan: [],
    title: '',
    titlePlaceholder: DEFAULT_PLACEHOLDER,
    // 地图配置
    mapCenter: TONGREN_CENTER,
    mapMarkers: [],
    polyline: [],
    mapScale: 9
  },

  onLoad(options) {
    this.spotMap = {};
    this.loadSpots().then(() => {
      const routeId = options && options.routeId;
      if (routeId) {
        this.prefillFromRoute(Number(routeId));
      } else {
        this.render();
      }
    });
  },

  loadSpots() {
    return api.getSpots()
      .then((res) => {
        const list = (res && res.list) || [];
        this.spotMap = {};
        list.forEach((s) => {
          this.spotMap[s.id] = s;
        });
        this.setData({ spots: list });
      })
      .catch(() => {
        this.spotMap = {};
      });
  },

  /** 从路线详情「加入自定义」带入打卡点 */
  prefillFromRoute(routeId) {
    api.getRoute(routeId)
      .then((r) => {
        if (!r) {
          this.render();
          return;
        }
        this.setData({
          selected: (r.spotIds || []).slice(),
          titlePlaceholder: r.name + ' · 我的行程'
        });
        this.render();
        app.toast('已加入 ' + (r.spotIds || []).length + ' 个景点，可调整顺序');
      })
      .catch(() => {
        this.render();
      });
  },

  /** 根据 selected 重新渲染勾选态与顺序列表 */
  render() {
    const spots = this.data.spots || [];
    const selected = this.data.selected;
    const selectList = spots.map((s) => ({
      id: s.id,
      name: s.name,
      district: s.district,
      cat: s.cat,
      level: s.level || '',
      levelText: s.level || '红',
      on: selected.indexOf(s.id) !== -1
    }));
    const orderList = selected
      .map((id) => this.spotMap[id])
      .filter(Boolean)
      .map((s) => ({ id: s.id, name: s.name, district: s.district }));
    this.setData({ selectList: selectList, orderList: orderList });
    this.updateMap();
  },

  /** 更新地图标记与路线折线 */
  updateMap() {
    const spots = this.data.spots || [];
    const selected = this.data.selected;
    const markers = [];
    const points = [];

    spots.forEach((s) => {
      const coord = SPOT_COORDS[s.id];
      if (!coord) return;
      const isOn = selected.indexOf(s.id) !== -1;
      markers.push({
        id: s.id,
        latitude: coord.latitude,
        longitude: coord.longitude,
        title: s.name,
        width: isOn ? 32 : 24,
        height: isOn ? 32 : 24,
        iconPath: isOn ? api.toIconUrl('pin', 'green700') : api.toIconUrl('pin', 'taggray'),
        callout: {
          content: s.name,
          color: '#FFFFFF',
          fontSize: 12,
          borderRadius: 6,
          bgColor: isOn ? '#3A5B42' : '#98988E',
          padding: 4,
          display: 'BYCLICK'
        }
      });
      if (isOn) points.push(coord);
    });

    // 选中的点按顺序连线
    const polyline = points.length >= 2 ? [{
      points: points,
      color: '#6B966F',
      width: 3,
      dottedLine: false,
      arrowLine: true
    }] : [];

    this.setData({ mapMarkers: markers, polyline: polyline });
  },

  /** 点击地图标记：切换选中状态 */
  onMarkerTap(e) {
    const id = e.detail.markerId;
    const selected = this.data.selected.slice();
    const pos = selected.indexOf(id);
    if (pos === -1) selected.push(id);
    else selected.splice(pos, 1);
    this.setData({ selected: selected, generated: false, plan: [] });
    this.render();
  },

  onToggle(e) {
    const id = Number(e.currentTarget.dataset.id);
    const selected = this.data.selected.slice();
    const pos = selected.indexOf(id);
    if (pos === -1) {
      selected.push(id);
    } else {
      selected.splice(pos, 1);
    }
    this.setData({ selected: selected, generated: false, plan: [] });
    this.render();
  },

  onMove(e) {
    const id = Number(e.currentTarget.dataset.id);
    const dir = Number(e.currentTarget.dataset.dir);
    const selected = this.data.selected.slice();
    const idx = selected.indexOf(id);
    const next = idx + dir;
    if (idx === -1 || next < 0 || next >= selected.length) return;
    selected.splice(idx, 1);
    selected.splice(next, 0, id);
    this.setData({ selected: selected, generated: false, plan: [] });
    this.render();
  },

  onRemove(e) {
    const id = Number(e.currentTarget.dataset.id);
    const selected = this.data.selected.filter((x) => x !== id);
    this.setData({ selected: selected, generated: false, plan: [] });
    this.render();
  },

  onReset() {
    this.setData({
      selected: [],
      generated: false,
      plan: [],
      title: '',
      titlePlaceholder: DEFAULT_PLACEHOLDER
    });
    this.render();
    app.toast('已重置，重新挑几个地方吧');
  },

  onTitleInput(e) {
    this.setData({ title: e.detail.value });
  },

  onGenerate() {
    if (!this.data.selected.length) {
      app.toast('先勾选几个心动景点吧');
      return;
    }
    const payload = {
      title: this.data.title,
      spotIds: this.data.selected,
      pace: 'standard'
    };
    api.generateCustomRoute(payload)
      .then((res) => {
        const plan = (res && (res.plan || res.days)) || [];
        const dayCount = (res && res.dayCount) || plan.length;
        const title = (res && res.title) || this.data.title || ('我的铜仁 ' + dayCount + ' 日游');
        this.setData({ plan: plan, generated: true, title: title });
        app.toast('行程已生成，共 ' + dayCount + ' 天');
        app.track('custom_generate', { count: plan.length, spotIds: this.data.selected });
        // 预留：保存行程到后端 t_user_trip
        api.saveTrip({ title: title, spotIds: this.data.selected, plan: plan }).catch(() => {});
      })
      .catch(() => {
        app.toast('行程生成失败，请稍后重试');
      });
  },

  onCopy() {
    if (!this.data.generated) {
      app.toast('请先生成行程');
      return;
    }
    const plan = this.data.plan || [];
    const text = (this.data.title || '我的铜仁行程') + '\n\n' + plan.map((d) =>
      d.day + '\n' + (d.items || []).map((it) => '  ' + it.time + '  ' + it.name).join('\n')
    ).join('\n\n');
    wx.setClipboardData({
      data: text,
      success: () => app.toast('已复制，可分享给同行伙伴')
    });
  },

  onBack() {
    wx.navigateBack();
  }
});
