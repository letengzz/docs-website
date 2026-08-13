# 开源软件许可证

开源软件许可证是开源软件的开发者与使用者之间的法律协议。它规定了使用者在获取、使用、修改和分发开源软件时的权利和限制。

## 什么是开源软件许可证

开源软件许可证（Open Source License）是一份具有法律效力的文档，它授予任何人使用、修改和共享该软件的权限，同时也规定了使用时必须遵守的条件。

::: tip 说明
开源不等于免费，也不等于没有任何限制。不同的开源许可证有不同的条件和限制，选择合适的许可证对你的项目至关重要。
:::

## 常见开源许可证

### MIT 许可证

MIT 许可证是最宽松的开源许可证之一，允许使用者自由使用、复制、修改、合并、出版发行、再授权和销售软件及其副本。

```text [LICENSE]
MIT License

Copyright (c) [year] [fullname]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

**特点**：

| 维度 | 说明 |
|------|------|
| 商业使用 | ✅ 允许 |
| 修改分发 | ✅ 允许 |
| 私有使用 | ✅ 允许 |
| 责任免除 | ✅ 包含 |
| 专利授权 | ❌ 不包含（明示） |
| 版权声明保留 | ✅ 需要 |

### Apache License 2.0

Apache 2.0 是最常用的企业级开源许可证，由 Apache 软件基金会发布。比 MIT 更完善，明确授予专利权和商标权。

```text [LICENSE]
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
...
```

**特点**：

| 维度 | 说明 |
|------|------|
| 商业使用 | ✅ 允许 |
| 修改分发 | ✅ 允许（需声明修改） |
| 私有使用 | ✅ 允许 |
| 专利授权 | ✅ 明确授予 |
| 商标授权 | ❌ 不授予 |
| 责任免除 | ✅ 包含 |
| 版权通知保留 | ✅ 需要 |
| 状态变更通知 | ✅ 需要 |

### GNU General Public License (GPL)

GPL 是最著名的"传染性"开源许可证，要求任何基于 GPL 代码的衍生作品也必须以 GPL 许可证开源。

**GPL v2 特点**：

| 维度 | 说明 |
|------|------|
| 商业使用 | ✅ 允许 |
| 修改分发 | ✅ 允许（但必须开源） |
| 私有使用 | ✅ 允许 |
| 传染性 | ⚠️ 衍生作品必须以 GPL 开源 |
| 专利授权 | ❌ 不包含（明示） |
| 责任免除 | ✅ 包含 |

**GPL v3 新增特性**：

| 特性 | 说明 |
|------|------|
| 专利授权 | ✅ 明确授予专利权 |
| 反 TiVo 化 | 禁止硬件锁定 |
| 兼容性 | 增加与其他许可证的兼容性 |
| 国际化 | 更好的国际法律适用 |

### GNU Lesser General Public License (LGPL)

LGPL 是 GPL 的宽松版本，主要用于程序库。允许专有软件通过链接方式使用 LGPL 库，而不需要开源自身代码。

**特点**：

| 维度 | 说明 |
|------|------|
| 商业使用 | ✅ 允许 |
| 动态链接 | ✅ 不需要开源 |
| 静态链接 | ⚠️ 需要开源或提供目标文件 |
| 库修改 | ⚠️ 修改库本身需要开源 |
| 传染性 | 较弱（仅限库本身） |

::: tip 适用场景
如果你开发的是一个库/框架，并希望它被广泛使用（包括商业项目），LGPL 是一个不错的选择。
:::

### BSD 许可证

BSD 许可证是另一类宽松许可证，主要有两个版本：

**2-Clause（简化版）**：

```text [LICENSE]
Copyright (c) [year] [fullname]
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
```

**3-Clause（修订版）**：

在 2-Clause 基础上增加第 3 条：未经特别书面许可，不得使用版权所有者的名称或其贡献者的名称来认可或推广从本软件派生的产品。

| 维度 | 2-Clause | 3-Clause |
|------|----------|----------|
| 商业使用 | ✅ | ✅ |
| 修改分发 | ✅ | ✅ |
| 版权声明 | ✅ 保留 | ✅ 保留 |
| 署名限制 | ❌ 无 | ✅ 禁止用作者名推广 |

### Mozilla Public License 2.0 (MPL)

MPL 是 Mozilla 创建的许可证，介于宽松许可证和 GPL 之间的"中间道路"。文件级别的 copyleft，而非项目级别。

| 维度 | 说明 |
|------|------|
| 商业使用 | ✅ 允许 |
| 修改分发 | ✅ 允许 |
| 专利授权 | ✅ 明确授予 |
| 传染性 | ⚠️ 文件级别（修改的文件需开源） |
| 兼容 GPL | ✅ 兼容 |
| 商标授权 | ❌ 不授予 |

### Creative Commons (CC) 许可证

CC 许可证主要用于文档、图片、音乐等创作作品，不推荐用于软件代码。

**CC 协议组合**：

| 元素 | 标识 | 说明 |
|------|------|------|
| BY（署名） | CC BY | 必须署名 |
| NC（非商业） | CC BY-NC | 禁止商业用途 |
| SA（相同方式共享） | CC BY-SA | 衍生作品需相同协议 |
| ND（禁止演绎） | CC BY-ND | 禁止修改原作品 |

**常见组合**：

| 协议 | 自由度 | 说明 |
|------|--------|------|
| CC0 | 最高 | 放弃版权，进入公共领域 |
| CC BY | 高 | 需署名，其余自由 |
| CC BY-SA | 中 | 需署名 + 相同协议 |
| CC BY-NC | 中 | 需署名 + 非商业 |
| CC BY-NC-SA | 低 | 需署名 + 非商业 + 相同协议 |
| CC BY-ND | 低 | 需署名 + 禁止修改 |
| CC BY-NC-ND | 最低 | 最严格的 CC 协议 |

## 许可证对比

### 核心维度对比

| 许可证 | 商业使用 | 修改分发 | 私有使用 | 传染性 | 专利授权 | 责任免除 |
|--------|----------|----------|----------|--------|----------|----------|
| MIT | ✅ | ✅ | ✅ | 无 | 无 | ✅ |
| Apache 2.0 | ✅ | ✅ | ✅ | 无 | ✅ | ✅ |
| GPL v2 | ✅ | ✅ | ✅ | 强 | 无 | ✅ |
| GPL v3 | ✅ | ✅ | ✅ | 强 | ✅ | ✅ |
| LGPL | ✅ | ✅ | ✅ | 弱 | 无 | ✅ |
| BSD 2-Clause | ✅ | ✅ | ✅ | 无 | 无 | ✅ |
| BSD 3-Clause | ✅ | ✅ | ✅ | 无 | 无 | ✅ |
| MPL 2.0 | ✅ | ✅ | ✅ | 中 | ✅ | ✅ |

### 宽松度排序（从高到低）

1. MIT — 最宽松
2. BSD 2-Clause — 极宽松
3. BSD 3-Clause — 宽松（加了署名限制）
4. Apache 2.0 — 宽松（最完善的法律保护）
5. MPL 2.0 — 中等（文件级 copyleft）
6. LGPL — 中等偏严格（库级 copyleft）
7. GPL — 严格（项目级 copyleft）

### 一些著名项目使用的许可证

| 项目 | 许可证 |
|------|--------|
| React | MIT |
| Vue.js | MIT |
| Angular | MIT |
| Node.js | MIT |
| jQuery | MIT |
| Bootstrap | MIT |
| Kubernetes | Apache 2.0 |
| Docker | Apache 2.0 |
| TensorFlow | Apache 2.0 |
| Swift | Apache 2.0 |
| Linux Kernel | GPL v2 |
| GCC | GPL v3 |
| MySQL | GPL v2 |
| FFmpeg | LGPL |
| Qt | LGPL |
| MongoDB | SSPL（类似 GPL） |
| Redis | BSD 3-Clause |
| PostgreSQL | PostgreSQL License（类 MIT） |

## 如何选择许可证

### 选择流程图

```text
是否希望代码被广泛使用？
├── 是 → 是否介意被用于闭源商业产品？
│   ├── 不介意 → MIT / Apache 2.0 / BSD
│   │   ├── 是否需要专利保护？ → Apache 2.0
│   │   └── 不需要 → MIT
│   └── 介意 → 修改后的代码是否需要开源？
│       ├── 整个项目 → GPL v3
│       ├── 仅修改的文件 → MPL 2.0
│       └── 仅库本身 → LGPL
└── 否（仅内部使用） → 可以不选择许可证
```

### 常见场景建议

| 场景 | 推荐许可证 |
|------|------------|
| 个人项目、博客 | MIT |
| 创业公司、商业产品 | Apache 2.0 |
| 希望保持开源生态 | GPL v3 |
| 开发通用库/框架 | MIT 或 Apache 2.0 |
| 开发可被商业软件引用的库 | LGPL 或 MPL 2.0 |
| 技术文档、教程 | CC BY 或 CC BY-SA |
| 希望完全放弃版权 | CC0 或 Unlicense |

## 如何在项目中添加许可证

### 在 GitHub 仓库中添加

1. 在仓库中创建 `LICENSE` 文件（注意：文件名必须全大写）
2. GitHub 在创建新仓库时提供许可证选择功能
3. 在 `package.json` 中标明许可证类型

```json [package.json]
{
  "name": "my-project",
  "version": "1.0.0",
  "license": "MIT"
}
```

### 在源代码文件中说明

```javascript
/*!
 * My Project v1.0.0
 * Copyright (c) 2024 Your Name
 * Released under the MIT License
 * https://opensource.org/licenses/MIT
 */
```

### 多个许可证的情况

如果项目包含来自不同许可证的代码：

```text
project/
├── LICENSE           # 项目主许可证
├── NOTICE            # 第三方声明
├── third-party/
│   ├── lib-a/
│   │   └── LICENSE   # MIT
│   └── lib-b/
│       └── LICENSE   # Apache 2.0
```

## 相关资源

- [Choose an open source license](https://choosealicense.com/) — GitHub 提供的许可证选择工具
- [Open Source Initiative](https://opensource.org/licenses/) — 开源许可证官方列表
- [SPDX License List](https://spdx.org/licenses/) — 标准化的许可证标识符
- [TLDRLegal](https://www.tldrlegal.com/) — 许可证内容摘要
- [Creative Commons](https://creativecommons.org/choose/) — CC 许可证选择工具
- [GNU Licenses](https://www.gnu.org/licenses/) — GNU 许可证官方说明
- [Open Source Guides](https://opensource.guide/) — GitHub 开源指南
