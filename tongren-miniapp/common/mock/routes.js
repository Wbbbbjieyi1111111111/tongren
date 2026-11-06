/**
 * 路线数据 — 严格对应原型 index.html 的 ROUTES 数组
 * 后端映射：GET /api/v1/routes  →  MySQL 表 t_route / t_route_plan / t_route_stay
 */

const ROUTES = [
  {
    id: 1, name: '一日游 · 城市精华', days: 1, suitable: '时间紧凑的游客', suitShort: '紧凑',
    difficulty: '★☆☆', overview: '中南门 → 锦江边 → 云舍村', foods: '社饭、米豆腐',
    tip: '市区交通便利，步行 + 打车即可', cover: 'zhongnanmen.jpg', spotIds: [5, 9],
    plan: [{
      day: 'Day 1', title: '老城与河岸',
      items: [
        { time: '09:00', name: '中南门历史街区', desc: '从青石板路开始，逛封火墙与老码头。' },
        { time: '11:30', name: '锦江边散步', desc: '沿江走到码头，看本地人钓鱼、晒太阳。' },
        { time: '12:30', name: '老城午餐', desc: '一碗锅巴粉，配一份社饭。' },
        { time: '14:30', name: '云舍村', desc: '龙塘河穿村而过，找一座石桥坐一会儿。' },
        { time: '17:30', name: '返回市区', desc: '傍晚回城，正好赶上中南门亮灯。' }
      ]
    }],
    stays: [
      { name: '中南门附近精品酒店', type: '市区酒店', price: '¥280 起', desc: '步行可达老街与江边，适合一晚短住' },
      { name: '锦江边民宿', type: '城市民宿', price: '¥220 起', desc: '临江房间，夜里能看见两岸灯火' }
    ],
    avoid: ['周末老街人多，贵重物品随身放好', '云舍村返回市区的班车较少，提前确认末班时间', '江边夜间湿滑，拍照注意脚下']
  },
  {
    id: 2, name: '两日游 · 梵净山朝圣', days: 2, suitable: '徒步 / 摄影爱好者', suitShort: '徒步',
    difficulty: '★★☆', overview: '梵净山 → 苗王城 → 亚木沟', foods: '酸汤牛肉、江口米豆腐',
    tip: '需提前预约，备雨具与防滑鞋', cover: 'fanjingshan.jpg', spotIds: [1, 2, 10],
    plan: [
      {
        day: 'Day 1', title: '梵净山朝圣',
        items: [
          { time: '08:30', name: '出发前往江口', desc: '铜仁市区出发，车程约 1 小时。' },
          { time: '09:30', name: '梵净山入园', desc: '换乘景区交通，索道上山直奔红云金顶。' },
          { time: '12:00', name: '山下午餐', desc: '江口米豆腐与酸汤牛肉，补充体力。' },
          { time: '14:00', name: '蘑菇石 · 万卷书', desc: '沿栈道慢走，等一阵云海。' },
          { time: '17:00', name: '入住寨沙侗寨', desc: '下山后住进侗寨，晚上有篝火晚会。' }
        ]
      },
      {
        day: 'Day 2', title: '苗疆与峡谷',
        items: [
          { time: '08:30', name: '苗王城', desc: '石头古堡与苗歌表演，预留 3 小时。' },
          { time: '11:30', name: '苗家午餐', desc: '酸汤牛肉配糯米饭。' },
          { time: '14:00', name: '亚木沟', desc: '沿溪栈道走一段，把两天慢下来。' },
          { time: '17:00', name: '返程', desc: '返回铜仁市区或江口县城。' }
        ]
      }
    ],
    stays: [
      { name: '寨沙侗寨临溪民宿', type: '侗寨民宿', price: '¥320 起', desc: '离梵净山游客中心约 10 分钟，方便赶早' },
      { name: '江口县城酒店', type: '舒适酒店', price: '¥260 起', desc: '餐饮选择多，适合自驾家庭' }
    ],
    avoid: ['梵净山节假日索道排队久，建议 8 点前入园', '山顶租大衣约 20 元，也可自带轻羽绒', '温泉区需自备泳衣，公共池注意防滑']
  },
  {
    id: 3, name: '三日深度游 · 全域铜仁', days: 3, suitable: '首次深度游', suitShort: '深度',
    difficulty: '★★★', overview: '梵净山 → 苗王城 → 石阡温泉 → 朱砂古镇', foods: '锅巴粉、石阡苔茶',
    tip: '日程较满，建议自驾或包车', cover: 'miaowangcheng.jpg', spotIds: [1, 4, 6, 8],
    plan: [
      {
        day: 'Day 1', title: '梵净山',
        items: [
          { time: '08:00', name: '江口出发', desc: '早一点进山，避开人流。' },
          { time: '09:00', name: '梵净山金顶', desc: '索道 + 步道，预留一整天。' },
          { time: '16:30', name: '寨沙侗寨', desc: '下山后休息，晚上参加篝火。' }
        ]
      },
      {
        day: 'Day 2', title: '苗王城与亚木沟',
        items: [
          { time: '08:30', name: '苗王城', desc: '古堡、苗歌与银饰。' },
          { time: '13:30', name: '亚木沟', desc: '峡谷徒步，感受清凉。' },
          { time: '18:00', name: '前往石阡', desc: '车程较长，建议包车。' }
        ]
      },
      {
        day: 'Day 3', title: '温泉与矿都',
        items: [
          { time: '10:00', name: '石阡温泉', desc: '山林泡池，把疲惫泡掉。' },
          { time: '14:00', name: '朱砂古镇', desc: '矿洞、老街与玻璃栈道。' },
          { time: '17:30', name: '返程', desc: '从万山返回铜仁市区。' }
        ]
      }
    ],
    stays: [
      { name: '石阡温泉度假酒店', type: '温泉酒店', price: '¥480 起', desc: '含泡汤，适合行程中段休整' },
      { name: '朱砂古镇主题客栈', type: '主题客栈', price: '¥300 起', desc: '工业风改造，夜景安静' }
    ],
    avoid: ['三天横跨多个县区，自驾或包车更从容', '石阡温泉旺季需提前订房', '朱砂古镇部分项目单独收费，入园前确认']
  },
  {
    id: 4, name: '亲子游 · 慢享铜仁', days: 2, suitable: '亲子家庭', suitShort: '亲子',
    difficulty: '★☆☆', overview: '云舍村 → 寨沙侗寨 → 温泉', foods: '米豆腐、甜酒粑',
    tip: '民宿提前订，温泉注意时长', cover: 'zhaisha.jpg', spotIds: [9, 10, 6],
    plan: [
      {
        day: 'Day 1', title: '村庄与侗寨',
        items: [
          { time: '09:30', name: '云舍村', desc: '沿龙塘河散步，看水车与石桥。' },
          { time: '12:00', name: '农家午餐', desc: '社饭、米豆腐，口味温和。' },
          { time: '15:00', name: '寨沙侗寨', desc: '鼓楼、风雨桥，孩子可以喂鱼。' },
          { time: '19:00', name: '篝火晚会', desc: '跟着侗歌围圈跳舞。' }
        ]
      },
      {
        day: 'Day 2', title: '温泉慢时光',
        items: [
          { time: '10:00', name: '石阡温泉', desc: '选择温度较低的池子，控制时长。' },
          { time: '12:30', name: '温泉午餐', desc: '清淡农家菜，饭后休息。' },
          { time: '15:00', name: '返程', desc: '不赶路，途中可停服务区休息。' }
        ]
      }
    ],
    stays: [
      { name: '寨沙侗寨亲子民宿', type: '侗寨民宿', price: '¥360 起', desc: '有院子和溪边活动空间' },
      { name: '石阡温泉家庭房', type: '温泉酒店', price: '¥520 起', desc: '含双早与泡汤，适合带娃' }
    ],
    avoid: ['温泉单次不超过 20 分钟，孩子需大人陪同', '村寨溪边石头湿滑，注意看护', '行程不要排太满，预留午休时间']
  },
  {
    id: 5, name: '自驾路线 · 环线打卡', days: 3, suitable: '自驾游客', suitShort: '自驾',
    difficulty: '★★☆', overview: '碧江 → 江口 → 松桃 → 石阡 环线', foods: '沿途农家乐',
    tip: '山区弯道多，注意车速', cover: 'taiping-river.jpg', spotIds: [5, 1, 4, 8],
    plan: [
      {
        day: 'Day 1', title: '碧江 → 江口',
        items: [
          { time: '09:00', name: '中南门', desc: '出发前逛一圈老城，吃碗锅巴粉。' },
          { time: '11:30', name: '太平河', desc: '沿河慢开，找一处浅滩停车。' },
          { time: '15:00', name: '梵净山脚', desc: '入住寨沙侗寨，傍晚散步。' }
        ]
      },
      {
        day: 'Day 2', title: '江口 → 松桃',
        items: [
          { time: '08:00', name: '梵净山', desc: '早起上山，午后下山。' },
          { time: '14:30', name: '苗王城', desc: '走古巷、看苗歌表演。' },
          { time: '18:00', name: '松桃县城', desc: '住一晚，尝苗家菜。' }
        ]
      },
      {
        day: 'Day 3', title: '松桃 → 石阡',
        items: [
          { time: '09:00', name: '朱砂古镇', desc: '矿都工业风，走玻璃栈道。' },
          { time: '13:00', name: '石阡温泉', desc: '泡汤放松，准备返程。' },
          { time: '17:00', name: '返程', desc: '沿高速返回铜仁或直接返家。' }
        ]
      }
    ],
    stays: [
      { name: '寨沙侗寨民宿', type: '侗寨民宿', price: '¥320 起', desc: '停车方便，适合自驾' },
      { name: '松桃县城酒店', type: '舒适酒店', price: '¥240 起', desc: '补给方便，次日上高速快捷' }
    ],
    avoid: ['山区弯道多，雨天减速慢行', '部分村寨停车位有限，旺季早到', '出发前检查油量与轮胎，山区加油站间距较大']
  }
];

function getRouteById(id) {
  const key = Number(id);
  return ROUTES.find((r) => r.id === key) || null;
}

module.exports = { ROUTES, getRouteById };
