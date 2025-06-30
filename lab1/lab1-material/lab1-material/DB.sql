-- Active: 1744278957744@@127.0.0.1@3306@db
# 如果DB数据库不存在，就创建数据库DB：
CREATE DATABASE IF NOT EXISTS DB;

# 切换到DB数据库
USE DB;

# 删除classes表（如果存在）：
DROP TABLE IF EXISTS classes;

-- 创建classes表：
CREATE TABLE classes (
id BIGINT NOT NULL AUTO_INCREMENT,
name VARCHAR(100) NOT NULL,
PRIMARY KEY (id)
) DEFAULT CHARSET=utf8;

-- 插入classes记录：
INSERT INTO classes(id, name) VALUES (1, '一班');
INSERT INTO classes(id, name) VALUES (2, '二班');
INSERT INTO classes(id, name) VALUES (3, '三班');
INSERT INTO classes(id, name) VALUES (4, '四班');

select * from classes;