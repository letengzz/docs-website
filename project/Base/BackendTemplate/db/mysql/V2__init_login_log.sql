-- V2__init_login_log.sql（MySQL 8.4 方言）
CREATE TABLE t_login_log (
    id            BIGINT       NOT NULL COMMENT '雪花 ID',
    username      VARCHAR(64)  NOT NULL COMMENT '登录账号',
    user_id       BIGINT       NULL     COMMENT '成功时记录用户 ID',
    login_type    VARCHAR(16)  NOT NULL COMMENT 'LOGIN / LOGOUT / REFRESH',
    success       TINYINT(1)   NOT NULL COMMENT '1=成功 0=失败',
    fail_reason   VARCHAR(64)  NULL     COMMENT '失败原因：BAD_CREDENTIAL / LOCKED / DISABLED',
    ip            VARCHAR(45)  NULL     COMMENT '客户端 IP（兼容 IPv6）',
    user_agent    VARCHAR(255) NULL     COMMENT 'UA 摘要',
    create_time   DATETIME(3)  NOT NULL COMMENT '发生时间',
    PRIMARY KEY (id),
    KEY idx_username_time (username, create_time),
    KEY idx_success (success, create_time)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '登录审计日志';
