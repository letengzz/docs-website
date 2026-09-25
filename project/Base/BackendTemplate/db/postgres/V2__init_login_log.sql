-- V2__init_login_log.sql（PostgreSQL 17 方言）
-- success 保持 SMALLINT 与实体 Integer 映射一致；如需布尔语义可改 BOOLEAN（需同步实体）
CREATE TABLE t_login_log (
    id            BIGINT       NOT NULL,
    username      VARCHAR(64)  NOT NULL,
    user_id       BIGINT       NULL,
    login_type    VARCHAR(16)  NOT NULL,
    success       SMALLINT     NOT NULL,
    fail_reason   VARCHAR(64)  NULL,
    ip            VARCHAR(45)  NULL,
    user_agent    VARCHAR(255) NULL,
    create_time   TIMESTAMP(3) NOT NULL,
    CONSTRAINT pk_t_login_log PRIMARY KEY (id)
);

COMMENT ON TABLE t_login_log IS '登录审计日志';
COMMENT ON COLUMN t_login_log.id IS '雪花 ID';
COMMENT ON COLUMN t_login_log.username IS '登录账号';
COMMENT ON COLUMN t_login_log.user_id IS '成功时记录用户 ID';
COMMENT ON COLUMN t_login_log.login_type IS 'LOGIN / LOGOUT / REFRESH';
COMMENT ON COLUMN t_login_log.success IS '1=成功 0=失败';
COMMENT ON COLUMN t_login_log.fail_reason IS '失败原因：BAD_CREDENTIAL / LOCKED / DISABLED';
COMMENT ON COLUMN t_login_log.ip IS '客户端 IP（兼容 IPv6）';
COMMENT ON COLUMN t_login_log.user_agent IS 'UA 摘要';
COMMENT ON COLUMN t_login_log.create_time IS '发生时间';

CREATE INDEX idx_username_time ON t_login_log (username, create_time);
CREATE INDEX idx_success ON t_login_log (success, create_time);
