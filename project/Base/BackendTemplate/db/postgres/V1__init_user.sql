-- V1__init_user.sql（PostgreSQL 17 方言）
-- 结构与 MySQL 版严格对齐（由 db/parity_check.py 校验）：
--   TINYINT → SMALLINT；DATETIME → TIMESTAMP；COMMENT 语法 → COMMENT ON；
--   内联索引 → CREATE INDEX；ENGINE/CHARSET 子句删除。
CREATE TABLE t_user (
    id          BIGINT       NOT NULL,
    username    VARCHAR(64)  NOT NULL,
    mobile      VARCHAR(20)      NULL,
    email       VARCHAR(128)     NULL,
    password    VARCHAR(100) NOT NULL,
    status      SMALLINT     NOT NULL DEFAULT 1,
    version     INTEGER      NOT NULL DEFAULT 0,
    deleted     SMALLINT     NOT NULL DEFAULT 0,
    deleted_at  BIGINT       NOT NULL DEFAULT 0,
    create_time TIMESTAMP    NOT NULL,
    create_by   BIGINT           NULL,
    update_time TIMESTAMP    NOT NULL,
    update_by   BIGINT           NULL,
    CONSTRAINT pk_t_user PRIMARY KEY (id),
    CONSTRAINT uk_username_deleted UNIQUE (username, deleted_at)
);

COMMENT ON TABLE t_user IS '用户表';
COMMENT ON COLUMN t_user.id IS '雪花 ID';
COMMENT ON COLUMN t_user.username IS '登录名';
COMMENT ON COLUMN t_user.mobile IS '手机号';
COMMENT ON COLUMN t_user.email IS '邮箱';
COMMENT ON COLUMN t_user.password IS 'BCrypt 摘要';
COMMENT ON COLUMN t_user.status IS '1 启用 0 禁用';
COMMENT ON COLUMN t_user.version IS '乐观锁版本';
COMMENT ON COLUMN t_user.deleted IS '逻辑删除 1 已删';
COMMENT ON COLUMN t_user.deleted_at IS '删除时间戳；未删为 0';

CREATE INDEX idx_create_time ON t_user (create_time);
