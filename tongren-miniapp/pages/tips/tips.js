/**
 * 出游贴士 —— 对应原型 SCREEN tips
 * GET /api/v1/seasons  →  t_season
 * 交通/预约/注意事项为固定文案，后端可改为 GET /api/v1/tips → t_travel_tip
 */
const api = require('../../common/api');
const config = require('../../common/config');

const app = getApp();

const DRESS = ['防滑徒步鞋', '防风外套', '轻便雨具', '温泉泳衣', '浅色拍照服'];

const TRANSPORT = [
  { label: '飞机', value: '铜仁凤凰机场 → 市区约 40 分钟车程', icon: 'plane' },
  { label: '高铁 / 火车', value: '铜仁站、铜仁南站，均可接驳市区与江口', icon: 'train' },
  { label: '客运', value: '各县城班线，江口方向班次较密', icon: 'bus' },
  { label: '自驾', value: '杭瑞高速、铜大高速，山区弯道注意车速', icon: 'car' }
];

const RESERVE = [
  { num: '1', label: '关注官方渠道', value: '认准景区公众号或官方小程序，勿信黄牛' },
  { num: '2', label: '实名预约', value: '填写身份证信息，旺季建议提前 1–3 天' },
  { num: '3', label: '凭码入园', value: '按预约时段抵达，梵净山需换乘景区交通' }
];

const NOTES = [
  '山区部分区域信号较弱，建议提前下载离线地图',
  '随身带些现金，村寨小店偶尔只收现金',
  '尊重民族习俗，拍摄人物前先征得同意',
  '夏季注意防晒防蚊，冬季湿冷注意保暖',
  '正规渠道购票，拒绝低价揽客与野导'
];

Page({
  data: {
    statusBar: app.globalData.statusBarHeight,
    icons: {
      back: api.toIconUrl('arrow-left', 'ink'),
      sun: api.toIconUrl('sun', 'green900'),
      check: api.toIconUrl('check', 'grayink')
    },
    seasons: [],
    dress: DRESS,
    transport: TRANSPORT.map((t) => ({
      label: t.label,
      value: t.value,
      iconUrl: api.toIconUrl(t.icon, 'green700')
    })),
    reserve: RESERVE,
    notes: NOTES
  },

  onLoad() {
    this.loadSeasons();
  },

  loadSeasons() {
    api.getSeasons()
      .then((res) => {
        const list = (res && res.list) || [];
        this.setData({
          seasons: list.map((s) => ({
            name: s.name,
            months: s.months,
            temp: s.temp,
            note: s.note
          }))
        });
      })
      .catch(() => {
        this.setData({ seasons: [] });
      });
  },

  onWeatherTap() {
    app.toast(config.weather.temp + ' ' + config.weather.desc + ' · 空气质量 ' + config.weather.aqi);
  },

  onHomeTap() {
    wx.switchTab({ url: '/pages/home/home' });
  },

  onBack() {
    wx.navigateBack();
  }
});
