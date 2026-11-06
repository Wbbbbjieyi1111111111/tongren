/**
 * 景点数据 — 严格对应原型 index.html 的 SPOTS 数组
 * 后端映射：GET /api/v1/spots  →  MySQL 表 t_spot
 */

const SPOTS = [
  {
    id: 1, name: '梵净山', level: '5A', cat: '自然风光', district: '江口县', score: 4.9,
    brief: '世界自然遗产，云海之上的天空之城', slogan: '云海翻涌处，山是一尊佛',
    img: 'fanjingshan.jpg', images: ['fanjingshan.jpg', 'yamugou.jpg', 'taiping-river.jpg'],
    ticket: '旺季 100 元 / 淡季 50 元', open: '08:00–18:00（旺季）',
    traffic: '铜仁站 → 江口客运站 → 游客中心', duration: '建议 4–6 小时',
    intro: [
      '梵净山是武陵山脉主峰，也是世界自然遗产地。红云金顶拔地而起，蘑菇石与万卷书崖在云雾里若隐若现，山风一过，云海便从脚下铺开。',
      '上山的路有索道也有步道。若想看日出，建议住在山脚或寨沙侗寨，第二天赶早入园；若只安排半日，乘索道直上金顶，也能遇见最经典的铜仁画面。'
    ],
    tips: ['旺季需提前 1–3 天在官方渠道实名预约', '尽量 8 点前入园，避开索道排队高峰', '山顶温差大，夏天也建议带一件薄外套'],
    foods: ['锅巴粉', '江口米豆腐']
  },
  {
    id: 2, name: '亚木沟', level: '4A', cat: '自然风光', district: '江口县', score: 4.7,
    brief: '峡谷幽深，一沟清凉，负氧离子满格', slogan: '沿溪而行，把夏天走凉',
    img: 'yamugou.jpg', images: ['yamugou.jpg', 'taiping-river.jpg', 'fanjingshan.jpg'],
    ticket: '旺季 80 元 / 淡季 50 元', open: '08:30–17:30',
    traffic: '江口县城乘车约 30 分钟', duration: '建议 3–4 小时',
    intro: [
      '亚木沟藏在梵净山南麓，是一条被原始森林包裹的峡谷。溪水从石缝间跌下来，栈道贴着岩壁往前，抬头是密密的树冠，低头是清得发绿的水。',
      '这里适合慢走。不必赶路，走到水声最响的地方停一停，深呼吸几次，再把手机收起来听一会儿山。'
    ],
    tips: ['雨后石阶湿滑，务必穿防滑鞋', '峡谷内温差明显，备一件薄外套', '夏季蚊虫较多，提前做好防蚊'],
    foods: ['江口米豆腐', '锅巴粉']
  },
  {
    id: 3, name: '太平河', level: '4A', cat: '自然风光', district: '江口县', score: 4.6,
    brief: '梵净山下的清澈河谷，适合慢骑与发呆', slogan: '一条河，把山色送到村口',
    img: 'taiping-river.jpg', images: ['taiping-river.jpg', 'yamugou.jpg', 'fanjingshan.jpg'],
    ticket: '免费开放', open: '全天开放',
    traffic: '江口县城沿河自驾或骑行', duration: '建议 2–3 小时',
    intro: [
      '太平河从梵净山流下来，水清、滩浅、弯多。沿岸是村庄和稻田，清晨常有薄雾，傍晚光线落在水面上，像一条慢慢发亮的带子。',
      '不赶时间的话，租一辆自行车沿河骑一段。遇到喜欢的浅滩就停下来，脱鞋踩水，或者只是坐在岸边看山。'
    ],
    tips: ['清晨与傍晚光线最好，适合拍照', '夏季可体验漂流，注意防晒', '保护水源，不要随手丢垃圾'],
    foods: ['社饭', '江口米豆腐']
  },
  {
    id: 4, name: '苗王城', level: '4A', cat: '古镇人文', district: '松桃县', score: 4.5,
    brief: '苗疆边墙上的古堡，银饰与苗歌未歇', slogan: '石头城还在，苗歌也还在',
    img: 'miaowangcheng.jpg', images: ['miaowangcheng.jpg', 'miao-silver.jpg', 'zhaisha.jpg'],
    ticket: '80 元', open: '08:30–17:30',
    traffic: '铜仁市区乘车约 1 小时', duration: '建议 3 小时',
    intro: [
      '苗王城是一座用石头垒起来的古军事城堡，巷道窄而深，吊脚楼沿山势层层叠起。这里曾是苗疆边墙的重要据点，如今仍住着人家，炊烟和游客擦肩而过。',
      '下午的苗族绝技与歌舞表演值得留出时间。看完演出，沿着古巷慢慢走，银饰铺、蜡染坊和卖米豆腐的小摊都藏在转角。'
    ],
    tips: ['提前确认演出场次，预留 40 分钟', '拍摄苗族同胞前请先征得同意', '银饰购买建议到正规店铺并索要凭证'],
    foods: ['酸汤牛肉', '江口米豆腐']
  },
  {
    id: 5, name: '中南门历史街区', level: '3A', cat: '古镇人文', district: '碧江区', score: 4.6,
    brief: '千年铜仁城的老街，一街灯火半城烟火', slogan: '青石板路尽头，是锦江的夜',
    img: 'zhongnanmen.jpg', images: ['zhongnanmen.jpg', 'zhusha.jpg', 'yunshe.jpg'],
    ticket: '免费开放', open: '全天开放',
    traffic: '铜仁市区步行或打车直达', duration: '建议 2 小时',
    intro: [
      '中南门是铜仁老城的原点。明清街巷沿锦江铺开，封火墙、木格窗、老码头都还在，白天安静，入夜后灯一盏盏亮起来，整条街就有了烟火气。',
      '建议傍晚来。先逛周逸群故居和几条支巷，再回到主街吃一碗锅巴粉，等天色完全暗下来，去江边看灯火落在水里。'
    ],
    tips: ['傍晚亮灯后氛围最好', '小吃集中在主街与江边', '周末与节假日人流较多，注意随身物品'],
    foods: ['锅巴粉', '社饭']
  },
  {
    id: 6, name: '石阡温泉', level: '4A', cat: '温泉休闲', district: '石阡县', score: 4.7,
    brief: '中国温泉之乡，山林里的热汤与慢时光', slogan: '把疲惫交给一池热汤',
    img: 'shiqian-spring.jpg', images: ['shiqian-spring.jpg', 'yunshe.jpg', 'taiping-river.jpg'],
    ticket: '128 元起', open: '10:00–23:00',
    traffic: '铜仁市区自驾约 2 小时', duration: '建议半天',
    intro: [
      '石阡的地热资源自古有名，温泉从地下深处涌出，沿山势做成大小不一的泡池。夜里水汽升起来，树影和灯影一起落在水面上，很适合把行程放慢。',
      '泡汤之外，也可以去老城走走。石阡的苔茶、绿豆粉和木偶戏，都值得留一点时间。'
    ],
    tips: ['自备泳衣，景区购买选择较少', '单次泡汤建议不超过 20 分钟，及时补水', '饭后一小时内不宜泡温泉'],
    foods: ['社饭', '江口米豆腐']
  },
  {
    id: 7, name: '佛顶山温泉', level: '4A', cat: '温泉休闲', district: '石阡县', score: 4.5,
    brief: '佛顶山脚的山林汤池，安静得只剩水声', slogan: '山深一点，水暖一点',
    img: 'shiqian-spring.jpg', images: ['shiqian-spring.jpg', 'zhaisha.jpg', 'taiping-river.jpg'],
    ticket: '108 元起', open: '10:00–22:30',
    traffic: '石阡县城乘车约 40 分钟', duration: '建议半天',
    intro: [
      '佛顶山温泉依山而建，池子散在林间，彼此隔开。相比城里的温泉，这里更安静，适合住一晚，把节奏彻底慢下来。',
      '清晨山里有雾，泡池边只有鸟声。若时间充裕，可以顺路去佛顶山徒步，再回来吃一顿热乎的农家饭。'
    ],
    tips: ['建议提前订房，周末房源紧张', '夜间泡汤注意保暖，备好浴袍', '山路弯多，自驾注意车速'],
    foods: ['社饭', '甜酒粑']
  },
  {
    id: 8, name: '朱砂古镇', level: '4A', cat: '古镇人文', district: '万山区', score: 4.4,
    brief: '千年汞矿遗址，工业风与玻璃栈道', slogan: '矿灯熄灭后，山城开始讲故事',
    img: 'zhusha.jpg', images: ['zhusha.jpg', 'zhongnanmen.jpg', 'yunshe.jpg'],
    ticket: '90 元', open: '09:00–17:30',
    traffic: '铜仁市区乘车约 50 分钟', duration: '建议 3 小时',
    intro: [
      '朱砂古镇建在万山汞矿遗址上。矿洞、老厂房、苏式宿舍和窄轨铁路被保留下来，工业时代的痕迹与山城生活叠在一起，有一种粗粝的好看。',
      '玻璃栈道悬在矿坑之上，走上去需要一点勇气。不想挑战的话，就在老街上逛逛矿工食堂和旧商店，听当地人讲一段“汞都”往事。'
    ],
    tips: ['穿舒适防滑的鞋，矿区步道较长', '矿洞内温度偏低，备一件外套', '玻璃栈道等项目可能单独收费'],
    foods: ['锅巴粉', '酸汤牛肉']
  },
  {
    id: 9, name: '云舍村', level: '3A', cat: '古镇人文', district: '江口县', score: 4.5,
    brief: '云中仙舍，土家村落与一条龙塘河', slogan: '云落下来，就成了村庄',
    img: 'yunshe.jpg', images: ['yunshe.jpg', 'zhaisha.jpg', 'taiping-river.jpg'],
    ticket: '免费开放', open: '全天开放',
    traffic: '江口县城乘车约 20 分钟', duration: '建议 2–3 小时',
    intro: [
      '云舍村在太平镇，是一个土家族聚居的古老村落。龙塘河从村中穿过，石桥、水车、老屋和菜地挨在一起，清晨有雾的时候，整座村子像浮在云里。',
      '这里没有太多商业化的店铺，适合慢慢走。找一家农家小院吃饭，饭后沿河散步，看村民在门口择菜、聊天，时间会变得很具体。'
    ],
    tips: ['清晨与雨后最容易遇到云雾', '农家饭建议提前问清价格', '村内道路较窄，自驾请慢行'],
    foods: ['社饭', '江口米豆腐']
  },
  {
    id: 10, name: '寨沙侗寨', level: '3A', cat: '古镇人文', district: '江口县', score: 4.6,
    brief: '梵净山脚的侗寨，鼓楼、风雨桥与篝火', slogan: '鼓楼灯亮，侗歌唱到夜深',
    img: 'zhaisha.jpg', images: ['zhaisha.jpg', 'miaowangcheng.jpg', 'yunshe.jpg'],
    ticket: '免费开放', open: '全天开放',
    traffic: '梵净山游客中心乘车约 10 分钟', duration: '建议 2 小时',
    intro: [
      '寨沙侗寨就在梵净山脚下，是很多人上山前或下山后的落脚点。鼓楼立在寨子中央，风雨桥横跨溪上，傍晚有篝火晚会，侗歌一起，游客也会被拉进圈里。',
      '如果想看梵净山日出，住在这里很方便。选一家临溪的民宿，晚上听着水声睡，第二天清早出发。'
    ],
    tips: ['篝火晚会时间以寨内公告为准', '旺季民宿紧俏，建议提前预订', '夜间温差大，备一件外套'],
    foods: ['酸汤牛肉', '甜酒粑']
  },
  {
    id: 11, name: '周逸群故居', level: '', cat: '红色景点', district: '碧江区', score: 4.3,
    brief: '老城里的红色记忆，晚清民居与革命故事', slogan: '一条老街，走出一位先行者',
    img: 'zhongnanmen.jpg', images: ['zhongnanmen.jpg', 'yunshe.jpg', 'zhusha.jpg'],
    ticket: '免费开放', open: '09:00–17:00（周一闭馆）',
    traffic: '中南门历史街区内步行可达', duration: '建议 1 小时',
    intro: [
      '周逸群故居藏在中南门的老巷里，是一座晚清风格的木结构民居。展陈讲述这位革命先驱的生平，也保留了老铜仁的生活痕迹。',
      '参观完可以顺着老街继续走，把红色历史与市井日常连在一起看，会对这座城多一层理解。'
    ],
    tips: ['周一闭馆，出发前确认开放时间', '馆内请保持安静，遵守参观秩序', '团队讲解建议提前预约'],
    foods: ['社饭', '锅巴粉']
  },
  {
    id: 12, name: '木黄会师纪念地', level: '', cat: '红色景点', district: '印江县', score: 4.4,
    brief: '红二、红六军团会师地，武陵山间的红色坐标', slogan: '山路会合处，历史转了一个弯',
    img: 'taiping-river.jpg', images: ['taiping-river.jpg', 'fanjingshan.jpg', 'zhaisha.jpg'],
    ticket: '免费开放', open: '09:00–17:00',
    traffic: '印江县城乘车约 1 小时', duration: '建议 1.5 小时',
    intro: [
      '木黄镇在印江东部，是红二、红六军团会师的地方。纪念地依山而建，展馆里保存着当年的文件、照片与实物，山风吹过，历史感很具体。',
      '这里适合与梵净山西线串联。看完展馆，再往山里走一段，能更直观地理解当年行军的路有多难。'
    ],
    tips: ['建议提前预约讲解', '山路弯多，自驾注意车速', '可结合梵净山西线安排一日行程'],
    foods: ['江口米豆腐', '社饭']
  }
];

function getSpotById(id) {
  const key = Number(id);
  return SPOTS.find((s) => s.id === key) || null;
}

module.exports = { SPOTS, getSpotById };
