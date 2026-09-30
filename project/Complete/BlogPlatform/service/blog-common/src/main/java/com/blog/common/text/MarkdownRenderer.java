package com.blog.common.text;

import java.util.ArrayList;
import java.util.List;

/**
 * 最小 Markdown 渲染器：**先全量转义，再渲染自己产出的标签**。
 *
 * <p>为什么自己写：引入一个完整 Markdown 库意味着引入它的全部攻击面与版本升级负担，
 * 而本项目只需要「后台作者写的 Markdown → 读者端安全 HTML」这一条路径。
 * 安全性的关键不在渲染能力，而在**顺序**——先 escape 再拼标签，任何用户输入的
 * {@code <script>} 都会先变成文本，不存在「消毒漏项」的可能。
 *
 * <p>明确支持：ATX 标题（{@code #} 到 {@code ###}）、段落、无序列表、围栏代码块、
 * 行内 {@code **粗体**} 与反引号代码、链接（仅 http/https 与站内相对路径）。
 * 明确不支持：表格、引用块、嵌套列表、HTML 混排——不支持的一律按纯文本输出，
 * **不做「看起来像但不安全」的降级实现**。
 */
public final class MarkdownRenderer {

    private MarkdownRenderer() {
    }

    /** 把 Markdown 原文渲染为消毒后的 HTML 片段。 */
    public static String toSafeHtml(String markdown) {
        if (markdown == null || markdown.isBlank()) {
            return "";
        }
        StringBuilder html = new StringBuilder(markdown.length() + 64);
        List<String> paragraph = new ArrayList<>();
        List<String> listItems = new ArrayList<>();
        boolean inCode = false;
        StringBuilder code = new StringBuilder();

        for (String raw : markdown.replace("\r\n", "\n").replace('\r', '\n').split("\n", -1)) {
            String line = raw.stripTrailing();

            if (line.stripLeading().startsWith("```")) {
                closeList(html, listItems);
                if (inCode) {
                    html.append("<pre><code>").append(escape(code.toString())).append("</code></pre>\n");
                    code.setLength(0);
                } else {
                    flushParagraph(html, paragraph);
                }
                inCode = !inCode;
                continue;
            }
            if (inCode) {
                code.append(raw).append('\n');
                continue;
            }

            String trimmed = line.strip();
            if (trimmed.isEmpty()) {
                flushParagraph(html, paragraph);
                closeList(html, listItems);
                continue;
            }

            String heading = headingOf(trimmed);
            if (heading != null) {
                flushParagraph(html, paragraph);
                closeList(html, listItems);
                html.append(heading).append('\n');
                continue;
            }

            if (trimmed.startsWith("- ")) {
                flushParagraph(html, paragraph);
                listItems.add(trimmed.substring(2));
                continue;
            }

            closeList(html, listItems);
            paragraph.add(trimmed);
        }

        if (inCode && code.length() > 0) {
            html.append("<pre><code>").append(escape(code.toString())).append("</code></pre>\n");
        }
        flushParagraph(html, paragraph);
        closeList(html, listItems);
        return html.toString();
    }

    private static String headingOf(String line) {
        int level = 0;
        while (level < 3 && level < line.length() && line.charAt(level) == '#') {
            level++;
        }
        if (level == 0 || line.length() <= level || line.charAt(level) != ' ') {
            return null;
        }
        return "<h" + level + ">" + inline(line.substring(level + 1).strip()) + "</h" + level + ">";
    }

    private static void flushParagraph(StringBuilder html, List<String> lines) {
        if (lines.isEmpty()) {
            return;
        }
        html.append("<p>").append(inline(String.join(" ", lines))).append("</p>\n");
        lines.clear();
    }

    private static void closeList(StringBuilder html, List<String> items) {
        if (items.isEmpty()) {
            return;
        }
        html.append("<ul>");
        for (String item : items) {
            html.append("<li>").append(inline(item)).append("</li>");
        }
        html.append("</ul>\n");
        items.clear();
    }

    /** 行内语法：输入已被调用方 escape，产出的标签是唯一允许出现的标签。 */
    private static String inline(String text) {
        String s = escape(text);
        s = s.replaceAll("\\*\\*(.+?)\\*\\*", "<strong>$1</strong>");
        s = s.replaceAll("`([^`]+)`", "<code>$1</code>");
        // 链接只放行 http/https 与站内相对路径；其他协议（含 javascript:）整段降级为纯文本
        s = s.replaceAll("\\[([^\\]]+)\\]\\((https?://[^)\\s]+|/[^)\\s]*)\\)", "<a href=\"$2\">$1</a>");
        s = s.replaceAll("\\[([^\\]]+)\\]\\(([^)]*)\\)", "$1（$2）");
        return s;
    }

    private static String escape(String s) {
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace("\"", "&quot;");
    }
}
