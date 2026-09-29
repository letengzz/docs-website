-- V1__blog_init.sql · PostgreSQL 17
-- 全栈博客平台 · 第 92 天按基座模板七条翻译规则从 MySQL 版转换
-- 结构一致性由 db/parity_check.py 门禁保证（类型归一化比对）

CREATE TABLE users (
    id            BIGINT       NOT NULL,
    username      VARCHAR(32)  NOT NULL,
    password_hash VARCHAR(100) NOT NULL,
    nickname      VARCHAR(32)  NOT NULL,
    role          VARCHAR(16)  NOT NULL DEFAULT 'READER',
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    -- 方言差异：MySQL 的 ON UPDATE CURRENT_TIMESTAMP 由应用层在更新时显式写入 updated_at
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_users PRIMARY KEY (id),
    CONSTRAINT uk_users_username UNIQUE (username)
);
COMMENT ON TABLE users IS '用户';
COMMENT ON COLUMN users.id IS '雪花 ID';
COMMENT ON COLUMN users.username IS '登录名';
COMMENT ON COLUMN users.password_hash IS 'BCrypt 哈希';
COMMENT ON COLUMN users.nickname IS '展示昵称';
COMMENT ON COLUMN users.role IS 'ADMIN/AUTHOR/READER';

CREATE TABLE categories (
    id         BIGINT      NOT NULL,
    name       VARCHAR(32) NOT NULL,
    slug       VARCHAR(64) NOT NULL,
    created_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_categories PRIMARY KEY (id),
    CONSTRAINT uk_categories_name UNIQUE (name),
    CONSTRAINT uk_categories_slug UNIQUE (slug)
);
COMMENT ON TABLE categories IS '分类';
COMMENT ON COLUMN categories.id IS '雪花 ID';
COMMENT ON COLUMN categories.name IS '分类名';
COMMENT ON COLUMN categories.slug IS 'URL 标识';

CREATE TABLE tags (
    id         BIGINT      NOT NULL,
    name       VARCHAR(32) NOT NULL,
    slug       VARCHAR(64) NOT NULL,
    created_at TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_tags PRIMARY KEY (id),
    CONSTRAINT uk_tags_name UNIQUE (name),
    CONSTRAINT uk_tags_slug UNIQUE (slug)
);
COMMENT ON TABLE tags IS '标签';
COMMENT ON COLUMN tags.id IS '雪花 ID';
COMMENT ON COLUMN tags.name IS '标签名';
COMMENT ON COLUMN tags.slug IS 'URL 标识';

CREATE TABLE posts (
    id            BIGINT       NOT NULL,
    author_id     BIGINT       NOT NULL,
    category_id   BIGINT       NOT NULL,
    slug          VARCHAR(128) NOT NULL,
    title         VARCHAR(128) NOT NULL,
    status        VARCHAR(16)  NOT NULL DEFAULT 'DRAFT',
    content_md    TEXT         NOT NULL,
    content_html  TEXT         NULL,
    search_text   TEXT         NULL,
    view_count    BIGINT       NOT NULL DEFAULT 0,
    published_at  TIMESTAMP    NULL,
    deleted_at    TIMESTAMP    NULL,
    created_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_posts PRIMARY KEY (id),
    CONSTRAINT uk_posts_slug UNIQUE (slug)
);
COMMENT ON TABLE posts IS '文章';
COMMENT ON COLUMN posts.id IS '雪花 ID';
COMMENT ON COLUMN posts.author_id IS '作者 → users.id';
COMMENT ON COLUMN posts.category_id IS '分类 → categories.id';
COMMENT ON COLUMN posts.slug IS 'URL 标识';
COMMENT ON COLUMN posts.title IS '标题';
COMMENT ON COLUMN posts.status IS 'DRAFT/PUBLISHED/OFFLINE';
COMMENT ON COLUMN posts.content_md IS 'Markdown 原文';
COMMENT ON COLUMN posts.content_html IS '渲染并消毒后的 HTML，发布时生成';
COMMENT ON COLUMN posts.search_text IS '纯文本检索字段（全文检索专用，不对外展示）';
COMMENT ON COLUMN posts.view_count IS '累计浏览（Redis 回写）';
COMMENT ON COLUMN posts.published_at IS '首发时间';
COMMENT ON COLUMN posts.deleted_at IS '软删除';

CREATE INDEX idx_posts_status_published ON posts (status, published_at);
CREATE INDEX idx_posts_category ON posts (category_id, status);
CREATE INDEX idx_posts_author ON posts (author_id);
-- 方言差异：MySQL FULLTEXT(ngram) → PG GIN + to_tsvector（名称对齐，索引列形态不参与 parity 比对）
CREATE INDEX ft_posts_search ON posts
    USING gin (to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(search_text, '')));

CREATE TABLE post_tags (
    post_id BIGINT NOT NULL,
    tag_id  BIGINT NOT NULL,
    CONSTRAINT pk_post_tags PRIMARY KEY (post_id, tag_id)
);
COMMENT ON TABLE post_tags IS '文章-标签关联';
CREATE INDEX idx_post_tags_tag ON post_tags (tag_id);

CREATE TABLE comments (
    id         BIGINT       NOT NULL,
    post_id    BIGINT       NOT NULL,
    user_id    BIGINT       NOT NULL,
    parent_id  BIGINT       NULL,
    root_id    BIGINT       NULL,
    content    VARCHAR(500) NOT NULL,
    deleted_at TIMESTAMP    NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_comments PRIMARY KEY (id)
);
COMMENT ON TABLE comments IS '评论';
COMMENT ON COLUMN comments.id IS '雪花 ID';
COMMENT ON COLUMN comments.post_id IS '文章 → posts.id';
COMMENT ON COLUMN comments.user_id IS '评论人 → users.id';
COMMENT ON COLUMN comments.parent_id IS '父评论，NULL 为楼层根';
COMMENT ON COLUMN comments.root_id IS '楼层根冗余，取整层回复用';
COMMENT ON COLUMN comments.content IS '内容 1~500';
COMMENT ON COLUMN comments.deleted_at IS '软删除';
CREATE INDEX idx_comments_post_root ON comments (post_id, root_id, created_at);
CREATE INDEX idx_comments_parent ON comments (parent_id);

CREATE TABLE view_count_daily (
    post_id    BIGINT      NOT NULL,
    stat_date  DATE        NOT NULL,
    view_count BIGINT      NOT NULL DEFAULT 0,
    CONSTRAINT pk_view_count_daily PRIMARY KEY (post_id, stat_date)
);
COMMENT ON TABLE view_count_daily IS '浏览量日回写';
