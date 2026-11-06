/**
 * 从 tongren-miniapp/common/{mock,config} 提取种子数据为 JSON（stdout）
 * 用法：node tools/extract_mock.js <tongren-miniapp 目录>
 */
const path = require('path');

const base = process.argv[2];
if (!base) {
  console.error('用法：node tools/extract_mock.js <tongren-miniapp 目录>');
  process.exit(1);
}

const spots = require(path.join(base, 'common/mock/spots.js'));
const routes = require(path.join(base, 'common/mock/routes.js'));
const culture = require(path.join(base, 'common/mock/culture.js'));
const config = require(path.join(base, 'common/config.js'));

const out = {
  spots: spots.SPOTS,
  routes: routes.ROUTES,
  foods: culture.FOODS,
  folk: culture.FOLK,
  festivals: culture.FESTIVALS,
  ethnic: culture.ETHNIC,
  seasons: culture.SEASONS,
  banners: culture.BANNERS,
  notices: (config.notices || []).map((title, i) => ({
    id: i + 1,
    title,
    content: title,
    publish_date: '2026-01-01',
  })),
};

console.log(JSON.stringify(out));
