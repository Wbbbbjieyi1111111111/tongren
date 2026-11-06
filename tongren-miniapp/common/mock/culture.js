/**
 * 文化 / 美食 / 民俗 / 节庆 / 民族 / 季节 — 对应原型 index.html
 * 后端映射：
 *   GET /api/v1/foods        → t_food
 *   GET /api/v1/folk         → t_folk
 *   GET /api/v1/festivals    → t_festival
 *   GET /api/v1/ethnic       → t_ethnic
 *   GET /api/v1/seasons      → t_season
 */

const FOODS = [
  { name: '锅巴粉', tag: '小吃', file: 'food-noodle.jpg', desc: '米浆烙出焦香锅巴，切条下汤，软糯里带一点脆。' },
  { name: '酸汤牛肉', tag: '正餐', file: 'food-beef.jpg', desc: '番茄与米汤发酵的酸汤，牛肉现涮，酸得开胃。' },
  { name: '社饭', tag: '主食', file: 'food-rice.jpg', desc: '春社日的糯米饭，拌野蒿、腊肉与花生，香气很野。' },
  { name: '江口米豆腐', tag: '小吃', file: 'food-rice.jpg', desc: '米浆点成豆腐，凉拌酸辣，是梵净山脚的日常。' },
  { name: '米虾', tag: '小吃', file: 'food-noodle.jpg', desc: '米浆漏成小虾状，配酸汤与葱花，滑溜爽口。' },
  { name: '甜酒粑', tag: '甜品', file: 'food-rice.jpg', desc: '糯米甜酒煮糍粑，冬天来一碗，从胃里暖到手心。' }
];

const FOLK = [
  { name: '土家摆手舞', level: '国家级非遗', desc: '祭祀与农耕动作化成的集体舞，围圈摆手，鼓点领舞。' },
  { name: '苗族赶秋', level: '省级非遗', desc: '立秋日苗族盛装集会，对歌、吹芦笙、荡秋千，热闹一整天。' },
  { name: '仡佬毛龙节', level: '国家级非遗', desc: '石阡元宵，竹篾扎龙、草把龙巡游，祈愿五谷丰登。' },
  { name: '傩戏', level: '国家级非遗', desc: '戴面具演出的古老戏剧，被称为“中国戏剧活化石”。' },
  { name: '花灯戏', level: '省级非遗', desc: '灯舞与说唱结合，诙谐热闹，多在节庆上演。' },
  { name: '西兰卡普', level: '国家级非遗', desc: '土家织锦，通经断纬，几何纹样色彩浓烈。' }
];

const FESTIVALS = [
  { month: '农历', day: '十月', name: '苗年', place: '松桃 · 苗王城', desc: '盛装巡游、长桌宴与芦笙会，是苗族最隆重的年节。' },
  { month: '春季', day: '社日', name: '土家过社', place: '碧江 / 江口村寨', desc: '做社饭、跳摆手舞，向土地讨一年的好收成。' },
  { month: '正月', day: '十五', name: '石阡毛龙节', place: '石阡县城', desc: '毛龙巡游、花灯与傩戏，元宵夜最热闹。' },
  { month: '六月', day: '十九', name: '梵净山佛诞', place: '梵净山', desc: '登山祈福，云海与香火一起升起。' }
];

const ETHNIC = [
  { name: '土家族', keys: '摆手舞 · 西兰卡普 · 过社', desc: '能歌善舞，把农耕与祭祀跳成一支摆手舞。', file: 'tujia-dance.jpg', mono: false },
  { name: '苗族', keys: '银饰 · 赶秋 · 苗年', desc: '松桃苗乡银光闪烁，苗王城是文化的重要载体。', file: 'miao-silver.jpg', mono: false },
  // 仡佬族：原型用 filter:grayscale + 绿色蒙层，WXSS 不支持 filter，
  // 已由静态资源侧预烘焙为灰度+绿罩的单图，页面直接用 file 即可。
  { name: '仡佬族', keys: '敬山祭 · 毛龙节 · 傩戏', desc: '石阡仡佬族的毛龙节，已列入国家级非遗名录。', file: 'gelao-festival-mono.jpg', mono: true }
];

const SEASONS = [
  { name: '春', months: '3–5 月', temp: '12–22°C', note: '温暖湿润，备一件薄外套', icon: 'leaf' },
  { name: '夏', months: '6–8 月', temp: '20–28°C', note: '多雨凉爽，梵净山适合避暑', icon: 'sun' },
  { name: '秋', months: '9–11 月', temp: '14–24°C', note: '秋高气爽，最适合徒步', icon: 'leaf' },
  { name: '冬', months: '12–2 月', temp: '3–10°C', note: '湿冷，正是泡温泉的时候', icon: 'cloud' }
];

const BANNERS = [
  { id: 1, file: 'fanjingshan.jpg', eyebrow: '世界自然遗产', title: '云海之上，天空之城', meta: '梵净山 · 江口县 · 5A' },
  { id: 5, file: 'zhongnanmen.jpg', eyebrow: '千年铜仁城', title: '一街灯火，半城烟火', meta: '中南门 · 碧江区' },
  { id: 4, file: 'miaowangcheng.jpg', eyebrow: '苗疆边墙', title: '银饰叮当，苗歌未歇', meta: '苗王城 · 松桃县 · 4A' },
  { id: 6, file: 'shiqian-spring.jpg', eyebrow: '中国温泉之乡', title: '山林深处，汤泉养心', meta: '石阡温泉 · 石阡县 · 4A' },
  { id: 10, file: 'zhaisha.jpg', eyebrow: '梵净山下', title: '鼓楼夜色，侗寨人家', meta: '寨沙侗寨 · 江口县' }
];

module.exports = { FOODS, FOLK, FESTIVALS, ETHNIC, SEASONS, BANNERS };
