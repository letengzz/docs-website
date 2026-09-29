-- V1__blog_init.sql · MySQL 8.4
-- 全栈博客平台 · 第 91 天数据库设计定稿（与 project/Complete/BlogPlatform/DatabaseDesign/index.md 同步）
-- 双方言约定见 db/parity_check.py：结构必须与 postgres/V1__blog_init.sql 一致（parity 门禁）

CREATE TABLE users (
    id            BIGINT       NOT NULL COMMENT '雪花 ID',
    username      VARCHAR(32)  NOT NULL COMMENT '登录名',
    password_hash VARCHAR(100) NOT NULL COMMENT 'BCrypt 哈希',
    nickname      VARCHAR(32)  NOT NULL COMMENT '展示昵称',
    role          VARCHAR(16)  NOT NULL DEFAULT 'READER' COMMENT 'ADMIN/AUTHOR/READER',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_users_username (username)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT '用户';

CREATE TABLE categories (
    id         BIGINT      NOT NULL COMMENT '雪花 ID',
    name       VARCHAR(32) NOT NULL COMMENT '分类名',
    slug       VARCHAR(64) NOT NULL COMMENT 'URL 标识',
    created_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_categories_name (name),
    UNIQUE KEY uk_categories_slug (slug)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT '分类';

CREATE TABLE tags (
    id         BIGINT      NOT NULL COMMENT '雪花 ID',
    name       VARCHAR(32) NOT NULL COMMENT '标签名',
    slug       VARCHAR(64) NOT NULL COMMENT 'URL 标识',
    created_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_tags_name (name),
    UNIQUE KEY uk_tags_slug (slug)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT '标签';

CREATE TABLE posts (
    id            BIGINT       NOT NULL COMMENT '雪花 ID',
    author_id     BIGINT       NOT NULL COMMENT '作者 → users.id',
    category_id   BIGINT       NOT NULL COMMENT '分类 → categories.id',
    slug          VARCHAR(128) NOT NULL COMMENT 'URL 标识',
    title         VARCHAR(128) NOT NULL COMMENT '标题',
    status        VARCHAR(16)  NOT NULL DEFAULT 'DRAFT' COMMENT 'DRAFT/PUBLISHED/OFFLINE',
    content_md    MEDIUMTEXT   NOT NULL COMMENT 'Markdown 原文',
    content_html  MEDIUMTEXT   NULL COMMENT '渲染并消毒后的 HTML，发布时生成',
    search_text   TEXT         NULL COMMENT '纯文本检索字段（FULLTEXT 专用，不对外展示）',
    view_count    BIGINT       NOT NULL DEFAULT 0 COMMENT '累计浏览（Redis 回写）',
    published_at  DATETIME     NULL COMMENT '首发时间',
    deleted_at    DATETIME     NULL COMMENT '软删除',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_posts_slug (slug),
    KEY idx_posts_status_published (status, published_at),
    KEY idx_posts_category (category_id, status),
    KEY idx_posts_author (author_id),
    FULLTEXT KEY ft_posts_search (title, search_text) WITH PARSER ngram
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT '文章';

CREATE TABLE post_tags (
    post_id BIGINT NOT NULL,
    tag_id  BIGINT NOT NULL,
    PRIMARY KEY (post_id, tag_id),
    KEY idx_post_tags_tag (tag_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT '文章-标签关联';

CREATE TABLE comments (
    id         BIGINT       NOT NULL COMMENT '雪花 ID',
    post_id    BIGINT       NOT NULL COMMENT '文章 → posts.id',
    user_id    BIGINT       NOT NULL COMMENT '评论人 → users.id',
    parent_id  BIGINT       NULL COMMENT '父评论，NULL 为楼层根',
    root_id    BIGINT       NULL COMMENT '楼层根冗余，取整层回复用',
    content    VARCHAR(500) NOT NULL COMMENT '内容 1~500',
    deleted_at DATETIME     NULL COMMENT '软删除',
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY idx_comments_post_root (post_id, root_id, created_at),
    KEY idx_comments_parent (parent_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT '评论';

CREATE TABLE view_count_daily (
    post_id    BIGINT      NOT NULL,
    stat_date  DATE        NOT NULL,
    view_count BIGINT      NOT NULL DEFAULT 0,
    PRIMARY KEY (post_id, stat_date)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT '浏览量日回写';
