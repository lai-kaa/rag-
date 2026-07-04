-- ============================================================
-- 企业知识库 RAG 系统 - 数据库初始化脚本
-- 数据库: db  |  MySQL 8  |  端口: 3306
-- ============================================================

CREATE DATABASE IF NOT EXISTS `db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `db`;

-- 用户表
DROP TABLE IF EXISTS `chat_messages`;
DROP TABLE IF EXISTS `chat_sessions`;
DROP TABLE IF EXISTS `documents`;
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
    `id`          INT          NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `username`    VARCHAR(50)  NOT NULL COMMENT '用户名',
    `password`    VARCHAR(64)  NOT NULL COMMENT '密码(MD5加密)',
    `role`        ENUM('admin','user') NOT NULL DEFAULT 'user' COMMENT '角色: admin-管理员, user-普通用户',
    `status`      TINYINT      NOT NULL DEFAULT 1 COMMENT '状态: 1-启用, 0-禁用',
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 知识库文档表
CREATE TABLE `documents` (
    `id`              INT          NOT NULL AUTO_INCREMENT COMMENT '文档ID',
    `title`           VARCHAR(200) NOT NULL COMMENT '文档标题',
    `file_name`       VARCHAR(255) NOT NULL COMMENT '原始文件名',
    `file_path`       VARCHAR(500) NOT NULL COMMENT '存储路径',
    `file_type`       VARCHAR(20)  NOT NULL COMMENT '文件类型: pdf/txt/docx',
    `file_size`       INT          NOT NULL DEFAULT 0 COMMENT '文件大小(字节)',
    `chunk_count`     INT          NOT NULL DEFAULT 0 COMMENT '向量切片数量',
    `upload_user_id`  INT          NOT NULL COMMENT '上传用户ID',
    `status`          TINYINT      NOT NULL DEFAULT 1 COMMENT '状态: 1-正常, 0-已删除',
    `created_at`      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    PRIMARY KEY (`id`),
    KEY `idx_upload_user` (`upload_user_id`),
    CONSTRAINT `fk_doc_user` FOREIGN KEY (`upload_user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识库文档表';

-- 问答会话表
CREATE TABLE `chat_sessions` (
    `id`          INT          NOT NULL AUTO_INCREMENT COMMENT '会话ID',
    `user_id`     INT          NOT NULL COMMENT '用户ID',
    `title`       VARCHAR(200) NOT NULL DEFAULT '新对话' COMMENT '会话标题',
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    CONSTRAINT `fk_session_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='问答会话表';

-- 对话消息表
CREATE TABLE `chat_messages` (
    `id`          BIGINT       NOT NULL AUTO_INCREMENT COMMENT '消息ID',
    `session_id`  INT          NOT NULL COMMENT '会话ID',
    `role`        ENUM('user','assistant') NOT NULL COMMENT '角色: user-用户, assistant-助手',
    `content`     TEXT         NOT NULL COMMENT '消息内容',
    `sources`     JSON         DEFAULT NULL COMMENT '引用来源(JSON)',
    `created_at`  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_session_id` (`session_id`),
    CONSTRAINT `fk_msg_session` FOREIGN KEY (`session_id`) REFERENCES `chat_sessions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='对话消息表';
