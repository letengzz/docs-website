package com.blog.data.model;

/** 标签：结构与分类一致，独立成表是因为它们是两条生命周期不同的字典（标签天然更易膨胀）。 */
public record Tag(long id, String name, String slug) {
}
