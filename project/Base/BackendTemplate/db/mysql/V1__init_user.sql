-- V1__init_user.sql（MySQL 8.4 方言）
-- 与主库可插拔约定配套；结构由 db/parity_check.py 与 PostgreSQL 版做一致性校验
CREATE TABLE t_user (
    id          BIGINT       NOT NULL COMMENT '雪花 ID',
    username    VARCHAR(64)  NOT NULL COMMENT '登录名',
    mobile      VARCHAR(20)      NULL COMMENT '手机号',
    email       VARCHAR(128)     NULL COMMENT '邮箱',
    password    VARCHAR(100) NOT NULL COMMENT 'BCrypt 摘要',
    status      TINYINT      NOT NULL DEFAULT 1 COMMENT '1 启用 0 禁用',
    version     INT          NOT NULL DEFAULT 0 COMMENT '乐观锁版本',
    deleted     TINYINT      NOT NULL DEFAULT 0 COMMENT '逻辑删除 1 已删',
    deleted_at  BIGINT       NOT NULL DEFAULT 0 COMMENT '删除时间戳；未删为 0',
    create_time DATETIME     NOT NULL,
    create_by   BIGINT           NULL,
    update_time DATETIME     NOT NULL,
    update_by   BIGINT           NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_username_deleted (username, deleted_at),
    KEY idx_create_time (create_time)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT = '用户表';
