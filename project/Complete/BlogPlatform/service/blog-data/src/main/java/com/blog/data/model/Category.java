package com.blog.data.model;

/** 分类：一个最简的字典表，`slug` 唯一且是读者端可见的稳定标识（`id` 只在内部与后台流转）。 */
public record Category(long id, String name, String slug) {
}
