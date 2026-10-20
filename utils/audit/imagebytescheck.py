#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""imagebytescheck.py —— 配图「字节层面」的两件事（第 69 项巡检）。

背景
----
本仓已有的图片巡检都停在「路径」与「文本」两层：

  - `imagecheck`        引用的文件存不存在；
  - `orphanassetcheck`  文件有没有被引用；
  - `assetsizecheck`    文件多大、有没有内嵌 base64；
  - `svgviewboxcheck`   SVG 的 viewBox 与缩放后字号；
  - `altqualitycheck`   alt 文本写得好不好。

**没有一项真的读过图片的字节头**。于是三类失效依然静默通过：

  1. **扩展名与真实格式不符**：`.png` 其实是 JPEG（存图时改了后缀），
     浏览器按魔数渲染，本地看着正常，某些 CI 的图片优化步骤按扩展名处理就出错；
     反过来 `.jpg` 其实是 SVG 文本，任何按位图解析的工具都会拿到 0×0。
  2. **文件根本不是图**：Git LFS 指针（140 字节的文本）、镜像站返回的 HTML 错误页、
     被 `git add` 进去的空文件——`<img>` 全部渲染成裂图，构建阶段一律不报错。
  3. **真实像素小于正文里的声称宽度**：`<img width="1200">` 对着一张 400 px 的图，
     浏览器放大 3 倍，结论是「这张图很糊」，而作者以为是自己截图没截好。

本项只做**静态可判**的部分：读文件头、读真实像素、跟正文声明比一比。不渲染、不改图。

判据（E 为错误、W 为提示）
--------------------------
E0 ROOT_NOT_FOUND      仓库根既无 docs/ 也无 project/
E1 NO_IMAGES           一张位图都没扫到就拒绝判定（活性，防「路径写错全绿」）
E2 MAGIC_MISMATCH      扩展名与文件头魔数不一致
E3 NOT_AN_IMAGE        文件头认不出是任何已知图片格式（LFS 指针 / HTML 错误页 / 空文件）
E4 TRUNCATED           能认出格式，但读不到像素尺寸（文件被截断或头部损坏）
W1 UPSCALED            正文声明的显示宽度 > 真实像素宽度（会被放大，观感模糊）
W2 TINY_BITMAP         真实宽度 < 200 px（这个尺寸几乎一定是该用矢量图的图标）
W3 OVERSIZE_BITMAP     真实宽度 > 3840 px（正文最多显示 720 px，多出来的像素是纯负担）

设计取舍
--------
* **只认「能在 `<img>` 里直接用」的格式**：PNG / JPEG / GIF / WebP / BMP / ICO / AVIF。
  SVG 是文本格式，尺寸与缩放由 `svgviewboxcheck` 负责，本项直接跳过——两条判据抢同一件事
  会让「改哪一条」变成争论。
* **声称宽度只认显式写法**：`<img width="1200">`、`style="width:1200px"`、`zoom:150%`。
  Markdown 原生 `![alt](x.png)` 没有宽度语义（浏览器用原始像素），不参与 W1 判定。
* **W3 的门槛定在 3840**：本仓正文最大宽度约 720 px，2× 屏下需要 1,440 px；
  3,840 是 4K 屏全宽的余量，超过它基本是把原图直接扔进仓库了。
* **W1 与 W2 不叠加**：一张 150 px 的图被声明成 400 px，只报 W1——根因只有一个。

用法
----
    python3 utils/audit/imagebytescheck.py                  # 默认根：仓库根
    python3 utils/audit/imagebytescheck.py --verbose         # 连 W 一起列
    python3 utils/audit/imagebytescheck.py --selftest        # 判据自测
    python3 utils/audit/imagebytescheck.py --summary         # 按目录聚合，看哪一片最差

退出码：0 = 无 E；1 = 有 E；2 = 根目录不存在。
"""
from __future__ import annotations

import argparse
import os
import re
import struct
import sys

RASTER_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico", ".avif"}
SKIP_DIRS = {".vitepress", "node_modules", "dist", ".git", "assets_cache"}

IMG_TAG = re.compile(r"<img\b[^>]*>", re.I)
SRC_ATTR = re.compile(r'\bsrc\s*=\s*"([^"]+)"', re.I)
WIDTH_ATTR = re.compile(r'\bwidth\s*=\s*"?(\d+)(?:px)?"?', re.I)
STYLE_ATTR = re.compile(r'\bstyle\s*=\s*"([^"]*)"', re.I)
STYLE_W = re.compile(r'width\s*:\s*(\d+)(?:px)?', re.I)
ZOOM = re.compile(r'zoom\s*:\s*(\d+)%', re.I)


# ---------------- 魔数与尺寸 ----------------
def sniff(head: bytes, ext: str):
    """返回 (格式名, (w, h) 或 None, 是否与扩展名相符)。认不出返回 (None, None, False)。"""
    def ok(name):
        return name, None, _ext_matches(name, ext)

    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png", _png_size(head), _ext_matches("png", ext)
    if head.startswith(b"\xff\xd8\xff"):
        return "jpeg", _jpeg_size(head), _ext_matches("jpeg", ext)
    if head[:6] in (b"GIF87a", b"GIF89a"):
        if len(head) >= 10:
            return "gif", struct.unpack("<HH", head[6:10]), _ext_matches("gif", ext)
        return "gif", None, _ext_matches("gif", ext)
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp", _webp_size(head), _ext_matches("webp", ext)
    if head[:2] == b"BM":
        return "bmp", _bmp_size(head), _ext_matches("bmp", ext)
    if head[:4] == b"\x00\x00\x01\x00":
        return "ico", _ico_size(head), _ext_matches("ico", ext)
    if head[4:8] == b"ftyp" and head[8:12] in (b"avif", b"avis"):
        return "avif", _isobmff_size(head), _ext_matches("avif", ext)
    return None, None, False


def _ext_matches(fmt: str, ext: str) -> bool:
    if fmt == "jpeg":
        return ext in (".jpg", ".jpeg")
    return ext == "." + fmt


def _png_size(b: bytes):
    if len(b) < 24 or b[12:16] != b"IHDR":
        return None
    w, h = struct.unpack(">II", b[16:24])
    return (w, h) if w and h else None


def _jpeg_size(b: bytes):
    i = 2
    n = len(b)
    while i + 9 < n:
        if b[i] != 0xFF:
            i += 1
            continue
        m = b[i + 1]
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7 or m == 0x01:
            i += 2
            continue
        seglen = struct.unpack(">H", b[i + 2:i + 4])[0]
        if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            if i + 9 > n:
                return None
            h, w = struct.unpack(">HH", b[i + 5:i + 9])
            return (w, h) if w and h else None
        i += 2 + seglen
    return None


def _webp_size(b: bytes):
    if len(b) < 30:
        return None
    fmt = b[12:16]
    if fmt == b"VP8 ":
        w, h = struct.unpack("<HH", b[26:30])
        return (w & 0x3FFF, h & 0x3FFF)
    if fmt == b"VP8L":
        bits = int.from_bytes(b[21:25], "little")
        return ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
    if fmt == b"VP8X":
        w = int.from_bytes(b[24:27], "little") + 1
        h = int.from_bytes(b[27:30], "little") + 1
        return (w, h)
    return None


def _bmp_size(b: bytes):
    if len(b) < 26:
        return None
    w, h = struct.unpack("<ii", b[18:26])
    return (abs(w), abs(h)) if w and h else None


def _ico_size(b: bytes):
    if len(b) < 8:
        return None
    w = b[6] or 256
    h = b[7] or 256
    return (w, h)


def _isobmff_size(b: bytes):
    """AVIF 的 ispe box 一般在前 200 字节内。"""
    idx = b.find(b"ispe")
    if idx < 0 or len(b) < idx + 12:
        return None
    w, h = struct.unpack(">II", b[idx + 4:idx + 12])
    return (w, h) if w and h else None


def probe(path: str):
    """返回 (fmt, size, ext_ok, note)。

    JPEG 的 SOF 段可能被挤到很后面：实测 `CSS3笔记-*.jpg` 的 SOF 在第 24,188 字节，
    前面是两个 11 KB / 12 KB 的 APP1（EXIF + XMP）。只读前 4 KB 会把这类正常文件
    误判成 E4，所以要按需加读。
    """
    ext = os.path.splitext(path)[1].lower()
    try:
        with open(path, "rb") as f:
            head = f.read(65536)
            if not head:
                return None, None, False, "0 字节"
            fmt, size, ext_ok = sniff(head, ext)
            if fmt == "jpeg" and size is None:
                for cap in (262144, 1048576, 8388608):
                    f.seek(0)
                    chunk = f.read(cap)
                    if len(chunk) <= len(head):
                        break
                    head, size = chunk, _jpeg_size(chunk)
                    if size:
                        break
            return fmt, size, ext_ok, ""
    except OSError as e:
        return None, None, False, f"读取失败 {e}"


# ---------------- 正文里的声称宽度 ----------------
def declared_widths(md_path: str, root: str):
    """返回 {abs_asset_path: declared_px}，只收显式写了宽度的 <img>。"""
    out = {}
    try:
        with open(md_path, encoding="utf-8", errors="ignore") as f:
            src = f.read()
    except OSError:
        return out
    base = os.path.dirname(md_path)
    for tag in IMG_TAG.findall(src):
        m = SRC_ATTR.search(tag)
        if not m:
            continue
        raw = m.group(1).split("#")[0].split("?")[0]
        if not raw or raw.startswith(("http://", "https://", "data:")):
            continue
        if raw.startswith("/"):
            p = os.path.join(root, "public", raw.lstrip("/"))
        else:
            p = os.path.normpath(os.path.join(base, raw))
        if not os.path.isfile(p):
            continue
        px = None
        wm = WIDTH_ATTR.search(tag)
        if wm:
            px = int(wm.group(1))
        else:
            sm = STYLE_ATTR.search(tag)
            if sm:
                zw = STYLE_W.search(sm.group(1))
                if zw:
                    px = int(zw.group(1))
        out[os.path.abspath(p)] = px  # None 表示「有这个 <img> 但没写宽度」
    return out


def iter_markdown(root: str):
    for base in ("docs", "project"):
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dirpath, dirnames, filenames in os.walk(d):
            dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS]
            for fn in sorted(filenames):
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn)


def iter_rasters(root: str):
    for base in ("docs", "project", "public"):
        d = os.path.join(root, base)
        if not os.path.isdir(d):
            continue
        for dirpath, dirnames, filenames in os.walk(d):
            dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS]
            for fn in sorted(filenames):
                if os.path.splitext(fn)[1].lower() in RASTER_EXT:
                    yield os.path.join(dirpath, fn)


# ---------------- 判定 ----------------
def check_file(path: str, declared: dict):
    out = []
    ext = os.path.splitext(path)[1].lower()
    fmt, size, ext_ok, note = probe(path)
    if note:
        return [("E3", "NOT_AN_IMAGE", f"{path}: {note}")]
    if fmt is None:
        head_txt = b""
        try:
            with open(path, "rb") as f:
                head_txt = f.read(80)
        except OSError:
            pass
        hint = "Git LFS 指针" if head_txt.startswith(b"version https://git-lfs") else \
               "疑似 HTML/文本" if b"<" in head_txt[:20] else "未知魔数"
        return [("E3", "NOT_AN_IMAGE", f"{path}: 扩展名 {ext}，{hint}")]

    if not ext_ok:
        out.append(("E2", "MAGIC_MISMATCH", f"{path}: 扩展名 {ext}，实际是 {fmt.upper()}"))

    if size is None:
        out.append(("E4", "TRUNCATED", f"{path}: 认出 {fmt.upper()} 但读不到像素尺寸"))
        return out

    w, h = size
    want = declared.get(os.path.abspath(path))
    if want and want > w:
        out.append(("W1", "UPSCALED",
                    f"{path}: 声明 {want}px，真实 {w}px（放大 {want / w:.2f}×）"))
    if w < 200:
        out.append(("W2", "TINY_BITMAP", f"{path}: {w}×{h}，这个尺寸建议用 SVG"))
    if w > 3840:
        out.append(("W3", "OVERSIZE_BITMAP", f"{path}: {w}×{h}，正文最多显示 720px"))
    return out


def run(root: str):
    declared = {}
    for md in iter_markdown(root):
        declared.update(declared_widths(md, root))
    findings = []
    n = 0
    for p in iter_rasters(root):
        n += 1
        findings.extend(check_file(p, declared))
    return findings, n, len(declared)


# ---------------- selftest ----------------
def _png(w: int, h: int) -> bytes:
    ihdr = struct.pack(">II", w, h) + b"\x08\x06\x00\x00\x00"
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + ihdr


def _jpeg(w: int, h: int) -> bytes:
    sof = b"\xff\xc0" + struct.pack(">H", 17) + b"\x08" + struct.pack(">HH", h, w) + b"\x03" + b"\x00" * 9
    return b"\xff\xd8\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x00" * 9 + sof


def _gif(w: int, h: int) -> bytes:
    return b"GIF89a" + struct.pack("<HH", w, h) + b"\x00" * 10


def _mk(tmp: str, name: str, body: bytes) -> str:
    p = os.path.join(tmp, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(body)
    return p


def selftest() -> int:
    import tempfile

    cases = []
    with tempfile.TemporaryDirectory() as tmp:
        # 1) 正常 PNG，扩展名对，尺寸正常 → 无判据
        p1 = _mk(tmp, "docs/a/ok.png", _png(760, 400))
        cases.append(("ok-no-finding", check_file(p1, {}) == [], str(check_file(p1, {}))))

        # 2) .png 里装的是 JPEG → E2
        p2 = _mk(tmp, "docs/a/wrong.png", _jpeg(300, 200))
        codes = [c for c, _, _ in check_file(p2, {})]
        cases.append(("magic-E2", "E2" in codes, str(codes)))

        # 3) .jpg 后缀的 jpeg 不应报 E2
        p3 = _mk(tmp, "docs/a/plain.jpg", _jpeg(300, 200))
        cases.append(("jpeg-ext-ok", check_file(p3, {}) == [], str(check_file(p3, {}))))

        # 4) Git LFS 指针 → E3
        p4 = _mk(tmp, "docs/a/lfs.png",
                 b"version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 12345\n")
        codes = [c for c, _, _ in check_file(p4, {})]
        cases.append(("lfs-E3", codes == ["E3"], str(codes)))

        # 5) 空文件 → E3
        p5 = _mk(tmp, "docs/a/empty.gif", b"")
        codes = [c for c, _, _ in check_file(p5, {})]
        cases.append(("empty-E3", codes == ["E3"], str(codes)))

        # 6) PNG 只有魔数没有 IHDR → E4
        p6 = _mk(tmp, "docs/a/cut.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 4)
        codes = [c for c, _, _ in check_file(p6, {})]
        cases.append(("truncated-E4", codes == ["E4"], str(codes)))

        # 7) 声明宽度大于真实宽度 → W1
        p7 = _mk(tmp, "docs/a/up.png", _png(400, 200))
        codes = [c for c, _, _ in check_file(p7, {os.path.abspath(p7): 1200})]
        cases.append(("upscaled-W1", codes == ["W1"], str(codes)))

        # 8) 声明宽度小于真实宽度 → 不报
        codes = [c for c, _, _ in check_file(p7, {os.path.abspath(p7): 200})]
        cases.append(("downscale-silent", codes == [], str(codes)))

        # 9) 真实宽度 120 < 200 → W2
        p9 = _mk(tmp, "docs/a/icon.png", _png(120, 120))
        codes = [c for c, _, _ in check_file(p9, {})]
        cases.append(("tiny-W2", codes == ["W2"], str(codes)))

        # 10) 真实宽度 5000 → W3
        p10 = _mk(tmp, "docs/a/huge.png", _png(5000, 3000))
        codes = [c for c, _, _ in check_file(p10, {})]
        cases.append(("oversize-W3", codes == ["W3"], str(codes)))

        # 11) GIF 尺寸解析
        p11 = _mk(tmp, "docs/a/anim.gif", _gif(640, 480))
        cases.append(("gif-size", probe(p11)[1] == (640, 480), str(probe(p11))))

        # 12) 正文声称宽度解析：width 属性
        _mk(tmp, "docs/b/x.png", _png(300, 200))
        md = os.path.join(tmp, "docs/b/page.md")
        with open(md, "w", encoding="utf-8") as f:
            f.write('<p><img src="./x.png" width="900" /></p>\n')
        d = declared_widths(md, tmp)
        cases.append(("declared-width-attr", d.get(os.path.abspath(os.path.join(tmp, "docs/b/x.png"))) == 900, str(d)))

        # 13) 正文声称宽度解析：zoom
        with open(md, "w", encoding="utf-8") as f:
            f.write('<p><img src="./x.png" style="zoom:75%;" /></p>\n')
        d = declared_widths(md, tmp)
        cases.append(("declared-zoom", d.get(os.path.abspath(os.path.join(tmp, "docs/b/x.png"))) is None, str(d)))

        # 14) 活性：目录里应有位图，SVG 不计入
        _mk(tmp, "docs/b/v.svg", b'<svg viewBox="0 0 10 10"></svg>')
        findings, n, _ = run(tmp)
        cases.append(("activity-count", n >= 5, f"scanned={n}"))

    ok = 0
    for name, passed, msg in cases:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}" + ("" if passed else f" :: {msg}"))
        ok += 1 if passed else 0
    print(f"selftest {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    root = os.path.abspath(args.root)
    if not os.path.isdir(os.path.join(root, "docs")) and not os.path.isdir(os.path.join(root, "project")):
        print(f"E0 ROOT_NOT_FOUND: {root}")
        return 2

    findings, n, n_decl = run(root)
    if n == 0:
        print("E1 NO_IMAGES: 一张位图都没扫到，拒绝判定")
        return 2

    errors = [x for x in findings if x[0].startswith("E")]
    warns = [x for x in findings if x[0].startswith("W")]

    for code, kind, msg in findings:
        if args.verbose or code.startswith("E"):
            print(f"{code} {kind}: {msg}")

    if args.summary:
        agg = {}
        for code, kind, msg in findings:
            if not code.startswith("W"):
                continue
            key = "/".join(os.path.relpath(msg.split(":")[0], root).split(os.sep)[:3])
            agg[key] = agg.get(key, 0) + 1
        for k in sorted(agg, key=lambda x: -agg[x]):
            print(f"  {agg[k]:4d}  {k}")

    print(f"images={n} declared={n_decl} E={len(errors)} W={len(warns)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
