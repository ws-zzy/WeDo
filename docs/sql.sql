-- table for user
-- 实现用户注册登录
-- TODO 增加字段
DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user`(
	`id` int(11) primary key auto_increment,
	`username` varchar(30) comment '用户名',
	`password` varchar(256) comment '加密后的密码',
	`type` int(11) NOT NULL comment '用户类型',
	`email`	varchar(20) comment '邮箱'
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 测试用户表
INSERT INTO `user` (`username`,`type`,`password`,`email`) VALUES ('李医生',0,'5549CD36CE93BF188AFC9370659E0AF2','123456789@qq.com');


-- table for uploadfile
-- 实现文件上传

DROP TABLE IF EXISTS `uploadedfile`;
CREATE TABLE IF NOT EXISTS `uploadedfile`(
	`id` int(11) primary key auto_increment comment '自增索引',
	`owner` int(11) DEFAULT NULL comment '上传者id',
	`time` timestamp comment '上传时间',
	`name` varchar(32) DEFAULT NULL comment '上传者上传的源文件名字，包括后缀名',
	`note` varchar(128) DEFAULT NULL comment '上传时用户填写的备注',
	`filename` varchar(128) DEFAULT NULL comment '哈希后的文件名',
	`input` varchar(128) DEFAULT NULL comment '输入文件绝对路径',
	`output` varchar(128) DEFAULT NULL comment '输出文件绝对路径'
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 测试数据
INSERT INTO `uploadedfile` (`owner`,`time`,`name`,`note`,`filename`,`input`,`output`)
VALUES (1,now(),'demo.xlsx','这是第一个测试文件','87eb8f294db1f9e4fa827f0526cd63bd.xlsx','/home/sunshine/AI-Care/data/input/JI96FV1S.xlsx','/home/sunshine/AI-Care/data/output/JI96FV1S.csv');


-- 返回结果
DROP TABLE IF EXISTS `predict_result`;
CREATE TABLE IF NOT EXISTS `predict_result`(
	id INT PRIMARY KEY auto_increment,
	`probability` DOUBLE(9,3),
	`filename` varchar(128) DEFAULT NULL comment '预测结果对应的[哈希后的文件名]'
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 测试
INSERT INTO `predict_result` (`probability`,`filename`) VALUES (0.01,'xxxx.xlsx');


-- 用户管理
CREATE USER 'yqm'@'localhost' IDENTIFIED BY '123456';
GRANT SELECT,INSERT,UPDATE ON aicare.uploadedfile TO 'yqm'@'localhost' IDENTIFIED BY '123456';
GRANT SELECT,INSERT,UPDATE ON aicare.predict_result TO 'yqm'@'localhost' IDENTIFIED BY '123456';


-- REFERENCE
-- https://www.cnblogs.com/gavin110-lgy/p/5773981.html
-- https://www.cnblogs.com/clsn/p/8047028.html#auto_id_4