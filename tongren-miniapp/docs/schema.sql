-- ============================================================================
--  大美铜仁 · 文旅小程序 —— MySQL 建库脚本
--  字符集 utf8mb4 / 排序规则 utf8mb4_0900_ai_ci（MySQL 8.0+）
--  用法：mysql -u root -p < docs/schema.sql
-- ============================================================================

CREATE DATABASE IF NOT EXISTS `tongren`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE `tongren`;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
--  一、内容主数据
-- ============================================================================

-- 景点 -----------------------------------------------------------------
DROP TABLE IF EXISTS `t_spot`;
CREATE TABLE `t_spot` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name`        VARCHAR(64)     NOT NULL                COMMENT '景点名称',
  `level`       VARCHAR(8)      NOT NULL DEFAULT ''     COMMENT '景区等级 5A/4A/3A',
  `cat`         VARCHAR(32)     NOT NULL DEFAULT ''     COMMENT '品类 自然风光/古镇人文/温泉休闲/红色景点',
  `district`    VARCHAR(32)     NOT NULL DEFAULT ''     COMMENT '所属区县',
  `score`       DECIMAL(2,1)    NOT NULL DEFAULT 0.0    COMMENT '评分',
  `brief`       VARCHAR(255)    NOT NULL DEFAULT ''     COMMENT '一句话简介',
  `slogan`      VARCHAR(255)    NOT NULL DEFAULT ''     COMMENT '主题短句',
  `img`         VARCHAR(128)    NOT NULL DEFAULT ''     COMMENT '封面图文件名，对应 static/img/',
  `ticket`      VARCHAR(64)     NOT NULL DEFAULT ''     COMMENT '票价',
  `open`        VARCHAR(64)     NOT NULL DEFAULT ''     COMMENT '开放时间',
  `traffic`     VARCHAR(128)    NOT NULL DEFAULT ''     COMMENT '交通方式',
  `duration`    VARCHAR(64)     NOT NULL DEFAULT ''     COMMENT '建议游玩时长',
  `intro`       JSON                     DEFAULT NULL    COMMENT '景区介绍段落数组',
  `tips`        JSON                     DEFAULT NULL    COMMENT '温馨提示数组',
  `foods`       JSON                     DEFAULT NULL    COMMENT '周边美食数组',
  `sort`        INT             NOT NULL DEFAULT 0     COMMENT '排序权重，越小越靠前',
  `status`      TINYINT         NOT NULL DEFAULT 1     COMMENT '1 上架 0 下架',
  `created_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_spot_cat` (`cat`),
  KEY `idx_spot_district` (`district`),
  KEY `idx_spot_level` (`level`),
  KEY `idx_spot_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='景点';

-- 景点图片 -------------------------------------------------------------
DROP TABLE IF EXISTS `t_spot_image`;
CREATE TABLE `t_spot_image` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `spot_id`     BIGINT UNSIGNED NOT NULL,
  `file`        VARCHAR(128)    NOT NULL DEFAULT ''     COMMENT '图片文件名',
  `sort`        INT             NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_spot_image_spot` (`spot_id`, `sort`),
  CONSTRAINT `fk_spot_image_spot` FOREIGN KEY (`spot_id`) REFERENCES `t_spot` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='景点图片';

-- 路线 -----------------------------------------------------------------
DROP TABLE IF EXISTS `t_route`;
CREATE TABLE `t_route` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name`        VARCHAR(64)     NOT NULL,
  `days`        TINYINT UNSIGNED NOT NULL DEFAULT 1    COMMENT '行程天数',
  `suitable`    VARCHAR(64)     NOT NULL DEFAULT ''    COMMENT '适合人群',
  `suit_short`  VARCHAR(32)     NOT NULL DEFAULT ''    COMMENT '适合人群（短标签）',
  `difficulty`  VARCHAR(16)     NOT NULL DEFAULT ''    COMMENT '难度 ★☆☆',
  `overview`    VARCHAR(255)    NOT NULL DEFAULT ''    COMMENT '路线概要',
  `foods`       VARCHAR(255)    NOT NULL DEFAULT ''    COMMENT '沿途美食',
  `tip`         VARCHAR(255)    NOT NULL DEFAULT ''    COMMENT '贴士',
  `cover`       VARCHAR(128)    NOT NULL DEFAULT ''    COMMENT '封面图文件名',
  `sort`        INT             NOT NULL DEFAULT 0,
  `status`      TINYINT         NOT NULL DEFAULT 1,
  `created_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_route_days` (`days`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路线';

-- 路线行程（每天一段） -------------------------------------------------
DROP TABLE IF EXISTS `t_route_plan`;
CREATE TABLE `t_route_plan` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `route_id`    BIGINT UNSIGNED NOT NULL,
  `day_index`   TINYINT UNSIGNED NOT NULL DEFAULT 1    COMMENT '第几天',
  `day_label`   VARCHAR(32)     NOT NULL DEFAULT ''    COMMENT 'Day 1',
  `title`       VARCHAR(64)     NOT NULL DEFAULT ''    COMMENT '当天标题',
  PRIMARY KEY (`id`),
  KEY `idx_plan_route` (`route_id`, `day_index`),
  CONSTRAINT `fk_plan_route` FOREIGN KEY (`route_id`) REFERENCES `t_route` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路线行程安排';

-- 行程明细 -------------------------------------------------------------
DROP TABLE IF EXISTS `t_route_plan_item`;
CREATE TABLE `t_route_plan_item` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `plan_id`     BIGINT UNSIGNED NOT NULL,
  `time`        VARCHAR(8)      NOT NULL DEFAULT ''    COMMENT '09:00',
  `name`        VARCHAR(64)     NOT NULL DEFAULT '',
  `desc`        VARCHAR(255)    NOT NULL DEFAULT '',
  `sort`        INT             NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_item_plan` (`plan_id`, `sort`),
  CONSTRAINT `fk_item_plan` FOREIGN KEY (`plan_id`) REFERENCES `t_route_plan` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路线行程明细';

-- 路线住宿 -------------------------------------------------------------
DROP TABLE IF EXISTS `t_route_stay`;
CREATE TABLE `t_route_stay` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `route_id`    BIGINT UNSIGNED NOT NULL,
  `name`        VARCHAR(128)    NOT NULL DEFAULT '',
  `type`        VARCHAR(64)     NOT NULL DEFAULT ''    COMMENT '市区酒店/城市民宿…',
  `price`       VARCHAR(32)     NOT NULL DEFAULT ''    COMMENT '¥280 起',
  `desc`        VARCHAR(255)    NOT NULL DEFAULT '',
  `sort`        INT             NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_stay_route` (`route_id`, `sort`),
  CONSTRAINT `fk_stay_route` FOREIGN KEY (`route_id`) REFERENCES `t_route` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路线住宿';

-- 路线避坑 -------------------------------------------------------------
DROP TABLE IF EXISTS `t_route_avoid`;
CREATE TABLE `t_route_avoid` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `route_id`    BIGINT UNSIGNED NOT NULL,
  `content`     VARCHAR(255)    NOT NULL DEFAULT '',
  `sort`        INT             NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_avoid_route` (`route_id`, `sort`),
  CONSTRAINT `fk_avoid_route` FOREIGN KEY (`route_id`) REFERENCES `t_route` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路线避坑提示';

-- 路线-景点关联 ---------------------------------------------------------
DROP TABLE IF EXISTS `t_route_spot`;
CREATE TABLE `t_route_spot` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `route_id`    BIGINT UNSIGNED NOT NULL,
  `spot_id`     BIGINT UNSIGNED NOT NULL,
  `sort`        INT             NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_route_spot_route` (`route_id`, `sort`),
  KEY `idx_route_spot_spot` (`spot_id`),
  CONSTRAINT `fk_route_spot_route` FOREIGN KEY (`route_id`) REFERENCES `t_route` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_route_spot_spot`  FOREIGN KEY (`spot_id`)  REFERENCES `t_spot` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='路线与景点关联';

-- 美食 -----------------------------------------------------------------
DROP TABLE IF EXISTS `t_food`;
CREATE TABLE `t_food` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name`        VARCHAR(64)     NOT NULL,
  `tag`         VARCHAR(32)     NOT NULL DEFAULT ''    COMMENT '小吃/正餐/主食/甜品',
  `file`        VARCHAR(128)    NOT NULL DEFAULT '',
  `desc`        VARCHAR(255)    NOT NULL DEFAULT '',
  `sort`        INT             NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='美食';

-- 民俗 -----------------------------------------------------------------
DROP TABLE IF EXISTS `t_folk`;
CREATE TABLE `t_folk` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name`        VARCHAR(64)     NOT NULL,
  `level`       VARCHAR(64)     NOT NULL DEFAULT ''    COMMENT '国家级非遗/省级非遗',
  `desc`        VARCHAR(255)    NOT NULL DEFAULT '',
  `sort`        INT             NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='民俗非遗';

-- 节庆 -----------------------------------------------------------------
DROP TABLE IF EXISTS `t_festival`;
CREATE TABLE `t_festival` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `month`       VARCHAR(32)     NOT NULL DEFAULT ''    COMMENT '农历/春季/正月/六月',
  `day`         VARCHAR(32)     NOT NULL DEFAULT ''    COMMENT '十月/社日/十五/十九',
  `name`        VARCHAR(64)     NOT NULL,
  `place`       VARCHAR(64)     NOT NULL DEFAULT '',
  `desc`        VARCHAR(255)    NOT NULL DEFAULT '',
  `sort`        INT             NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='节庆';

-- 民族 -----------------------------------------------------------------
DROP TABLE IF EXISTS `t_ethnic`;
CREATE TABLE `t_ethnic` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name`        VARCHAR(64)     NOT NULL,
  `keys`        VARCHAR(128)    NOT NULL DEFAULT ''    COMMENT '摆手舞 · 西兰卡普 · 过社',
  `desc`        VARCHAR(255)    NOT NULL DEFAULT '',
  `file`        VARCHAR(128)    NOT NULL DEFAULT '',
  `mono`        TINYINT         NOT NULL DEFAULT 0     COMMENT '1 灰度绿罩样式',
  `sort`        INT             NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='民族风情';

-- 季节 -----------------------------------------------------------------
DROP TABLE IF EXISTS `t_season`;
CREATE TABLE `t_season` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name`        VARCHAR(16)     NOT NULL                COMMENT '春/夏/秋/冬',
  `months`      VARCHAR(32)     NOT NULL DEFAULT '',
  `temp`        VARCHAR(32)     NOT NULL DEFAULT '',
  `note`        VARCHAR(128)    NOT NULL DEFAULT '',
  `icon`        VARCHAR(32)     NOT NULL DEFAULT 'leaf',
  `sort`        INT             NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='四季气候';

-- 首页轮播 -------------------------------------------------------------
DROP TABLE IF EXISTS `t_banner`;
CREATE TABLE `t_banner` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `file`        VARCHAR(128)    NOT NULL DEFAULT '',
  `eyebrow`     VARCHAR(64)     NOT NULL DEFAULT ''    COMMENT '世界自然遗产',
  `title`       VARCHAR(128)    NOT NULL DEFAULT ''    COMMENT '云海之上，天空之城',
  `meta`        VARCHAR(128)    NOT NULL DEFAULT ''    COMMENT '梵净山 · 江口县 · 5A',
  `link_type`   VARCHAR(16)     NOT NULL DEFAULT ''    COMMENT 'spot/route/none',
  `link_id`     BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `sort`        INT             NOT NULL DEFAULT 0,
  `status`      TINYINT         NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='首页轮播';

-- 公告 -----------------------------------------------------------------
DROP TABLE IF EXISTS `t_notice`;
CREATE TABLE `t_notice` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `title`       VARCHAR(128)    NOT NULL DEFAULT '',
  `content`     VARCHAR(512)    NOT NULL DEFAULT '',
  `publish_date` DATE           NOT NULL,
  `sort`        INT             NOT NULL DEFAULT 0,
  `status`      TINYINT         NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `idx_notice_date` (`publish_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='公告';

-- ============================================================================
--  二、用户行为（同时作为 Python 数据分析的原始输入）
-- ============================================================================

DROP TABLE IF EXISTS `t_user`;
CREATE TABLE `t_user` (
  `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `openid`        VARCHAR(64)     NOT NULL DEFAULT ''     COMMENT '微信 openid；账号注册用户写 phone:<手机号> 满足唯一约束',
  `unionid`       VARCHAR(64)     NOT NULL DEFAULT '',
  `nickname`      VARCHAR(64)     NOT NULL DEFAULT '',
  `avatar`        VARCHAR(255)    NOT NULL DEFAULT '',
  `phone`         VARCHAR(20)     NOT NULL DEFAULT ''     COMMENT '手机号（账号密码登录）',
  `password_hash` VARCHAR(255)    NOT NULL DEFAULT ''     COMMENT '密码哈希 pbkdf2$迭代次数$盐$摘要',
  `created_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`    DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_openid` (`openid`),
  UNIQUE KEY `uk_user_phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户';

DROP TABLE IF EXISTS `t_user_favorite`;
CREATE TABLE `t_user_favorite` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id`     BIGINT UNSIGNED NOT NULL DEFAULT 0    COMMENT '0 表示未登录游客',
  `target_type` VARCHAR(16)     NOT NULL                COMMENT 'spot/route',
  `target_id`   BIGINT UNSIGNED NOT NULL,
  `favorite`    TINYINT         NOT NULL DEFAULT 1     COMMENT '1 收藏 0 取消',
  `created_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_fav` (`user_id`, `target_type`, `target_id`),
  KEY `idx_fav_target` (`target_type`, `target_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏';

DROP TABLE IF EXISTS `t_user_trip`;
CREATE TABLE `t_user_trip` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id`     BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `title`       VARCHAR(128)    NOT NULL DEFAULT '',
  `days`        TINYINT UNSIGNED NOT NULL DEFAULT 1,
  `spot_ids`    JSON                     DEFAULT NULL  COMMENT '[1,4,6,8]',
  `plan`        JSON                     DEFAULT NULL  COMMENT '生成后的行程结构',
  `source`      VARCHAR(16)     NOT NULL DEFAULT 'custom' COMMENT 'custom/recommended',
  `created_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_trip_user` (`user_id`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户自定义行程';

-- 浏览/搜索行为日志：Python 分析的原始事实表 --------------------------
DROP TABLE IF EXISTS `t_user_log`;
CREATE TABLE `t_user_log` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id`     BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `event`       VARCHAR(32)     NOT NULL                COMMENT 'page_view/spot_view/search/favorite/trip_generate',
  `target_type` VARCHAR(16)     NOT NULL DEFAULT ''     COMMENT 'spot/route/null',
  `target_id`   BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `keyword`     VARCHAR(64)     NOT NULL DEFAULT '',
  `page`        VARCHAR(64)     NOT NULL DEFAULT '',
  `channel`     VARCHAR(32)     NOT NULL DEFAULT ''     COMMENT '来源渠道',
  `created_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_log_event` (`event`, `created_at`),
  KEY `idx_log_target` (`target_type`, `target_id`),
  KEY `idx_log_kw` (`keyword`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户行为日志（分析原料）';

-- ============================================================================
--  三、Python 数据分析结果表（前端 /analytics/* 只读这些表）
--  命名与前端 common/api.js 注释一一对应
-- ============================================================================

-- 概览 KPI -------------------------------------------------------------
DROP TABLE IF EXISTS `t_analytics_overview`;
CREATE TABLE `t_analytics_overview` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `stat_date`   DATE            NOT NULL                COMMENT '数据日期',
  `metric_key`  VARCHAR(32)     NOT NULL                COMMENT 'visitors/avgStay/hotSpot/satisfaction',
  `label`       VARCHAR(32)     NOT NULL DEFAULT '',
  `value`       VARCHAR(32)     NOT NULL DEFAULT '0'    COMMENT '展示值（含单位）',
  `unit`        VARCHAR(16)     NOT NULL DEFAULT '',
  `delta`       VARCHAR(16)     NOT NULL DEFAULT '',
  `trend`       VARCHAR(8)      NOT NULL DEFAULT 'up'   COMMENT 'up/down/flat',
  `updated_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_overview` (`stat_date`, `metric_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析-概览KPI';

-- 趋势序列 -------------------------------------------------------------
DROP TABLE IF EXISTS `t_analytics_trend`;
CREATE TABLE `t_analytics_trend` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `stat_date`   DATE            NOT NULL,
  `period`      VARCHAR(16)     NOT NULL DEFAULT 'month' COMMENT 'day/month/quarter',
  `label`       VARCHAR(16)     NOT NULL                COMMENT '1月',
  `value`       DECIMAL(12,2)   NOT NULL DEFAULT 0,
  `unit`        VARCHAR(16)     NOT NULL DEFAULT '',
  `updated_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_trend_date` (`stat_date`, `period`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析-趋势';

-- 区县分布 -------------------------------------------------------------
DROP TABLE IF EXISTS `t_analytics_district`;
CREATE TABLE `t_analytics_district` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `stat_date`   DATE            NOT NULL,
  `district`    VARCHAR(32)     NOT NULL,
  `value`       DECIMAL(12,2)   NOT NULL DEFAULT 0,
  `unit`        VARCHAR(16)     NOT NULL DEFAULT '',
  `updated_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_district_date` (`stat_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析-区县分布';

-- 品类占比 -------------------------------------------------------------
DROP TABLE IF EXISTS `t_analytics_category`;
CREATE TABLE `t_analytics_category` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `stat_date`   DATE            NOT NULL,
  `category`    VARCHAR(32)     NOT NULL,
  `value`       DECIMAL(8,2)    NOT NULL DEFAULT 0      COMMENT '百分比',
  `unit`        VARCHAR(16)     NOT NULL DEFAULT '%',
  `updated_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_category_date` (`stat_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析-品类占比';

-- 景点排行 -------------------------------------------------------------
DROP TABLE IF EXISTS `t_analytics_ranking`;
CREATE TABLE `t_analytics_ranking` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `stat_date`   DATE            NOT NULL,
  `target_type` VARCHAR(16)     NOT NULL DEFAULT 'spot',
  `target_id`   BIGINT UNSIGNED NOT NULL DEFAULT 0,
  `name`        VARCHAR(64)     NOT NULL DEFAULT '',
  `rank`        INT             NOT NULL DEFAULT 0,
  `score`       DECIMAL(4,2)    NOT NULL DEFAULT 0      COMMENT '评分',
  `visitors`    DECIMAL(12,2)   NOT NULL DEFAULT 0      COMMENT '客流量（万人次）',
  `updated_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_ranking_date` (`stat_date`, `target_type`, `rank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析-景点排行';

-- 季节性指数 -----------------------------------------------------------
DROP TABLE IF EXISTS `t_analytics_season`;
CREATE TABLE `t_analytics_season` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `stat_date`   DATE            NOT NULL,
  `season`      VARCHAR(8)      NOT NULL                COMMENT '春/夏/秋/冬',
  `value`       DECIMAL(10,2)   NOT NULL DEFAULT 0,
  `note`        VARCHAR(128)    NOT NULL DEFAULT '',
  `unit`        VARCHAR(16)     NOT NULL DEFAULT '指数',
  `updated_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_season_date` (`stat_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析-季节性指数';

-- 热力网格 -------------------------------------------------------------
DROP TABLE IF EXISTS `t_analytics_heat`;
CREATE TABLE `t_analytics_heat` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `stat_date`   DATE            NOT NULL,
  `grid_row`    INT             NOT NULL DEFAULT 0,
  `grid_col`    INT             NOT NULL DEFAULT 0,
  `value`       DECIMAL(12,2)   NOT NULL DEFAULT 0,
  `updated_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_heat_date` (`stat_date`, `grid_row`, `grid_col`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析-热力网格';

-- 模型预测 -------------------------------------------------------------
DROP TABLE IF EXISTS `t_analytics_prediction`;
CREATE TABLE `t_analytics_prediction` (
  `id`           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `stat_date`    DATE            NOT NULL,
  `model_name`   VARCHAR(64)     NOT NULL DEFAULT ''   COMMENT '模型名，如 xgb_visitors',
  `label`        VARCHAR(64)     NOT NULL,
  `value`        VARCHAR(128)    NOT NULL DEFAULT '',
  `advice`       VARCHAR(255)    NOT NULL DEFAULT '',
  `confidence`   DECIMAL(5,4)    NOT NULL DEFAULT 0,
  `updated_at`   DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_prediction_date` (`stat_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析-预测结果';

-- 分析任务执行日志 -----------------------------------------------------
DROP TABLE IF EXISTS `t_analysis_task`;
CREATE TABLE `t_analysis_task` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `task_name`   VARCHAR(64)     NOT NULL,
  `status`      VARCHAR(16)     NOT NULL DEFAULT 'running' COMMENT 'running/success/failed',
  `started_at`  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `finished_at` DATETIME     NULL DEFAULT NULL,
  `rows_written` INT            NOT NULL DEFAULT 0,
  `message`     VARCHAR(512)    NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  KEY `idx_task_time` (`started_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='分析任务执行记录';

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================================
--  四、初始化数据（与小程序 common/mock/*.js 完全同构）
-- ============================================================================
-- 说明：mock 数据可直接由后端导入（见 docs/API-CONTRACT.md 的「数据导入」一节）。
-- 这里给出最小可跑通的一条示例，其余请用 Python 脚本从 JSON 导入：
--   INSERT INTO t_spot (name, level, cat, district, score, brief, slogan, img,
--                        ticket, open, traffic, duration, intro, tips, foods, sort)
--   VALUES ('梵净山','5A','自然风光','江口县',4.9,'世界自然遗产，云海之上的天空之城',
--           '云海翻涌处，山是一尊佛','fanjingshan.jpg','旺季 100 元 / 淡季 50 元',
--           '08:00–18:00（旺季）','铜仁站 → 江口客运站 → 游客中心','建议 4–6 小时',
--           JSON_ARRAY('…'), JSON_ARRAY('…'), JSON_ARRAY('锅巴粉','江口米豆腐'), 1);
