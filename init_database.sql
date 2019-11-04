CREATE TABLE `policy_data_analysis_rules` (
  `id_` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID自增',
  `task_id` int(11) NOT NULL COMMENT '任务编号',
  `meaning` varchar(512) DEFAULT '',
  `rule_name` varchar(512) DEFAULT '' COMMENT '规则名',
  `rule_type` varchar(512) DEFAULT '' COMMENT '规则类型：1,xpath 2,正则',
  `rule` varchar(512) DEFAULT '' COMMENT '规则',
  `insert_time` datetime DEFAULT NULL COMMENT '插入时间',
  PRIMARY KEY (`id_`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;

CREATE TABLE `policy_spider_data_info` (
  `id_` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID自增',
  `task_id` int(11) NOT NULL COMMENT '任务编号',
  `title` varchar(1024) DEFAULT NULL COMMENT '标题',
  `content` mediumtext COMMENT '正文',
  `author` varchar(1024) DEFAULT NULL,
  `index_number` varchar(1024) DEFAULT NULL COMMENT '索引号',
  `organization` varchar(1024) DEFAULT NULL COMMENT '发文机关',
  `file_number` varchar(1024) DEFAULT NULL COMMENT '发文号',
  `keywords` varchar(1024) DEFAULT NULL COMMENT '主题词',
  `subject` varchar(1024) DEFAULT NULL COMMENT '主题分类',
  `create_date` varchar(1024) DEFAULT NULL COMMENT '成文日期',
  `release_date` varchar(1024) DEFAULT NULL COMMENT '发布日期',
  `enforcement_date` varchar(1024) DEFAULT NULL COMMENT '实施时间',
  `invalid_date` varchar(1024) DEFAULT NULL COMMENT '失效时间',
  `image_path` varchar(1024) DEFAULT NULL COMMENT '图片路径',
  `attachment` varchar(1024) DEFAULT NULL COMMENT '附件',
  `is_attachment_image` varchar(255) DEFAULT NULL COMMENT '是否有附件或图片',
  `url` varchar(300) NOT NULL COMMENT 'url',
  `type1` varchar(64) DEFAULT NULL COMMENT '一级分类名字',
  `type2` varchar(64) DEFAULT NULL COMMENT '二级分类名字',
  `type3` varchar(64) DEFAULT NULL COMMENT '三级分类名字',
  `type4` varchar(64) DEFAULT NULL COMMENT '四级分类名字',
  `type5` varchar(64) DEFAULT NULL COMMENT '五级分类名字',
  `insert_time` datetime NOT NULL COMMENT '插入时间',
  PRIMARY KEY (`id_`)
) ENGINE=InnoDB AUTO_INCREMENT=990 DEFAULT CHARSET=utf8;

CREATE TABLE `policy_spider_log` (
  `id_` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID自增',
  `task_id` int(11) NOT NULL COMMENT '任务编号',
  `state` int(11) NOT NULL COMMENT '状态：0表示成功，1表示失败',
  `spider_stage` int(11) NOT NULL DEFAULT '0' COMMENT '爬虫阶段',
  `http_code` int(11) NOT NULL COMMENT 'http状态码',
  `msg` varchar(1000) DEFAULT NULL COMMENT '错误信息',
  `url` varchar(300) NOT NULL COMMENT 'url',
  `type1` varchar(64) DEFAULT NULL COMMENT '一级分类名字',
  `type2` varchar(64) DEFAULT NULL COMMENT '二级分类名字',
  `type3` varchar(64) DEFAULT NULL COMMENT '三级分类名字',
  `type4` varchar(64) DEFAULT NULL COMMENT '四级分类名字',
  `type5` varchar(64) DEFAULT NULL COMMENT '五级分类名字',
  `insert_time` datetime NOT NULL COMMENT '插入时间',
  `proxy` varchar(255) DEFAULT NULL COMMENT '使用的代理',
  PRIMARY KEY (`id_`)
) ENGINE=InnoDB AUTO_INCREMENT=144 DEFAULT CHARSET=utf8;

CREATE TABLE `policy_spider_task_info` (
  `id_` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID自增',
  `task_id` int(11) NOT NULL COMMENT '任务编号',
  `home_url` varchar(300) NOT NULL DEFAULT '' COMMENT '主页地址',
  `start_url` varchar(255) DEFAULT NULL,
  `spider_type` int(11) DEFAULT NULL COMMENT '爬虫种类：0，直接输入url；1，点击下一页；2，ajax',
  `state` int(11) DEFAULT NULL COMMENT '-3:正在执行spider2重试，-2:正在执行spider1重试，-1:尚未准备就绪，0:准备就绪，1：正在执行spider1，2 正在执行spider2，3:spider1执行完成，4:spider2执行完成，5:正在进行数据处理，6:数据处理完毕',
  `type1` varchar(64) DEFAULT '' COMMENT '直属',
  `type2` varchar(64) DEFAULT '' COMMENT '组织机构',
  `type3` varchar(64) DEFAULT '' COMMENT '部门（网站）名称',
  `type4` varchar(64) DEFAULT '' COMMENT '模块名称',
  `type5` varchar(64) DEFAULT '' COMMENT '数据类型',
  `urls` mediumtext COMMENT '直接输入的列表页url',
  `url_head` varchar(255) DEFAULT '' COMMENT '详情页url头部',
  `rules_url` varchar(512) DEFAULT '' COMMENT '提取详情页url的规则',
  `rules_next_page` varchar(512) DEFAULT '' COMMENT '提取下一页按钮的规则',
  `ajax_url` text COMMENT '输入的ajax请求的地址',
  `ajax_data` text COMMENT '输入的ajax请求的数据',
  `rules_time` varchar(512) DEFAULT '' COMMENT '提取时间的规则',
  `rules_organization` varchar(512) DEFAULT '' COMMENT '发文机关',
  `rules_subject` varchar(512) DEFAULT '' COMMENT '主题分类',
  `rules_keywords` varchar(512) DEFAULT '' COMMENT '主题词',
  `rules_file_number` varchar(512) DEFAULT '' COMMENT '发文号',
  `rules_create_date` varchar(512) DEFAULT '' COMMENT '成文日期',
  `rules_release_date` varchar(512) DEFAULT '' COMMENT '发布时间',
  `rules_enforcement_date` varchar(512) DEFAULT '' COMMENT '实施日期',
  `rules_invalid_date` varchar(512) DEFAULT '' COMMENT '失效日期',
  `rules_index_number` varchar(512) DEFAULT '' COMMENT '索引号',
  `rules_author` varchar(512) DEFAULT '' COMMENT '作者',
  `insert_time` datetime DEFAULT NULL COMMENT '插入时间',
  PRIMARY KEY (`id_`)
) ENGINE=InnoDB AUTO_INCREMENT=391 DEFAULT CHARSET=utf8;

CREATE TABLE `policy_spider_url_info` (
  `id_` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID自增',
  `task_id` int(11) NOT NULL COMMENT '任务编号',
  `type1` varchar(64) DEFAULT NULL COMMENT '一级分类名字',
  `type2` varchar(64) DEFAULT NULL COMMENT '二级分类名字',
  `type3` varchar(64) DEFAULT NULL COMMENT '三级分类名字',
  `type4` varchar(64) DEFAULT NULL COMMENT '四级分类名字',
  `type5` varchar(64) DEFAULT NULL COMMENT '五级分类名字',
  `url` text NOT NULL COMMENT 'url',
  `insert_time` datetime NOT NULL COMMENT '插入时间',
  `from_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_`)
) ENGINE=InnoDB AUTO_INCREMENT=65157 DEFAULT CHARSET=utf8;

