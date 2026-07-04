-- ============================================================
-- 企业知识库 RAG 系统 - 测试数据
-- 密码均为 123456，MD5: e10adc3949ba59abbe56e057f20f883e
-- ============================================================

USE `db`;

-- 测试用户
INSERT INTO `users` (`username`, `password`, `role`, `status`) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', 'admin', 1),
('user1', 'e10adc3949ba59abbe56e057f20f883e', 'user', 1),
('user2', 'e10adc3949ba59abbe56e057f20f883e', 'user', 1);

-- 示例会话
INSERT INTO `chat_sessions` (`user_id`, `title`, `created_at`) VALUES
(2, '关于公司考勤制度的咨询', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(2, '报销流程相关问题', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(3, '新员工入职指南', DATE_SUB(NOW(), INTERVAL 1 DAY)),
(2, '今日问答测试', NOW());

-- 示例消息
INSERT INTO `chat_messages` (`session_id`, `role`, `content`, `sources`, `created_at`) VALUES
(1, 'user', '公司的考勤制度是怎样的？', NULL, DATE_SUB(NOW(), INTERVAL 6 DAY)),
(1, 'assistant', '根据公司考勤制度，员工应按时上下班，迟到超过30分钟按旷工半天处理。', '[{"title":"员工手册","content":"考勤制度相关内容..."}]', DATE_SUB(NOW(), INTERVAL 6 DAY)),
(2, 'user', '报销需要哪些材料？', NULL, DATE_SUB(NOW(), INTERVAL 3 DAY)),
(2, 'assistant', '报销需提供发票原件、费用明细单及审批单。', '[{"title":"财务制度","content":"报销流程..."}]', DATE_SUB(NOW(), INTERVAL 3 DAY)),
(3, 'user', '新员工入职第一天需要做什么？', NULL, DATE_SUB(NOW(), INTERVAL 1 DAY)),
(3, 'assistant', '新员工入职第一天需到人事部办理入职手续，领取工牌和办公用品。', NULL, DATE_SUB(NOW(), INTERVAL 1 DAY)),
(4, 'user', '你好', NULL, NOW()),
(4, 'assistant', '您好！我是企业知识库助手，有什么可以帮您的？', NULL, NOW());
