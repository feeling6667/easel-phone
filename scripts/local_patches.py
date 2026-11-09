#!/usr/bin/env python3
"""本机补丁清单：把仓库里所有【本机补丁 …】标记汇总成 docs/local-patches.md。

为什么要这个文件：本仓库是上游 Easel 的分叉，行为以**本仓库**为准（见 CONTRIBUTING
「本机补丁与契约」）。既然如此，哪些地方和上游不一样就必须是**可枚举**的 —— 否则
要么测试替上游守着旧规矩（红），要么某天上游合进来时没人知道哪些冲突是故意的。

用法：
    python scripts/local_patches.py            # 打印清单
    python scripts/local_patches.py --write    # 写入 docs/local-patches.md
    python scripts/local_patches.py --check    # 校验文档是否最新（CI 用）
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "local-patches.md"
# 清单口径：**任何含「本机补丁」四个字的行**都算一处（注释、文档、测试都算）。
# 标记本身有几种写法，括号形式最好看，全部统一成 【本机补丁 YYYY-MM-DD】 是长期目标：
#   【本机补丁 2026-10-12】说明…   （本机补丁）说明…   ── 本机补丁 1/3：说明…
# 标记里若带日期或 n/m 编号，会被抽出来放进「标记」列。
TAG_RE = re.compile(r"【本机补丁([^】]*)】|（本机补丁([^）]*)）|「本机补丁([^」]*)」")
NUM_RE = re.compile(r"本机补丁\s*(\d+/\d+)")
SELF = Path(__file__).resolve()
SKIP_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "vendor"}
TEXT_EXTS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".css", ".sh", ".ps1", ".psd1",
    ".yml", ".yaml", ".json", ".toml", ".md",
}


def iter_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.suffix.lower() not in TEXT_EXTS:
            continue
        # CONTRIBUTING 是「规矩」本身，里面必然出现这些字；本脚本和账本同理。
        if rel.as_posix() in {"CONTRIBUTING.md", DOC.relative_to(ROOT).as_posix()} or path.resolve() == SELF:
            continue
        if rel.parts[:2] == ("skills", "builtin") and "vendor" in rel.parts:
            continue
        yield rel, path


def collect() -> list[dict]:
    rows: list[dict] = []
    for rel, path in iter_files():
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, 1):
            if "本机补丁" not in line:
                continue
            tag_match = TAG_RE.search(line)
            num_match = NUM_RE.search(line)
            tag = ""
            if tag_match:
                tag = next((g for g in tag_match.groups() if g), "").strip()
                end = tag_match.end()
            elif num_match:
                tag = num_match.group(1).strip()
                end = num_match.end()
            else:
                end = line.index("本机补丁") + len("本机补丁")
            summary = line[end:].strip()
            summary = re.sub(r"^(】|）|」|：|:)\s*", "", summary)
            summary = re.sub(r"^(#|//|\*|--|──)\s*", "", summary)
            summary = summary.rstrip("─━═ ").replace("|", "\\|")
            if len(summary) > 70:
                summary = summary[:69].rstrip() + "…"
            rows.append({"file": rel.as_posix(), "line": number, "tag": tag, "summary": summary})
    return rows


def render(rows: list[dict]) -> str:
    by_file: dict[str, list[dict]] = {}
    for row in rows:
        by_file.setdefault(row["file"], []).append(row)

    parts = [
        "# 本机补丁清单",
        "",
        "> 本文件由 `python scripts/local_patches.py --write` 生成，**不要手改**。",
        "> CI 会跑 `--check`，标记与本文档不一致就红。",
        "",
        "本仓库的行为**以本仓库为准**：凡是和上游 Easel 不一样的地方，都在源码里用",
        "`【本机补丁 YYYY-MM-DD】` 标出来，并对齐了对应的测试断言。",
        "规则与模板见 [CONTRIBUTING.md](../CONTRIBUTING.md) 的「本机补丁与契约」一节。",
        "",
        f"共 **{len(rows)}** 处，分布在 **{len(by_file)}** 个文件：",
        "",
        "| 文件 | 行 | 标记 | 说明 |",
        "| --- | ---: | --- | --- |",
    ]
    for file, items in by_file.items():
        for item in items:
            parts.append(
                f"| `{file}` | {item['line']} | {item['tag'] or '—'} | {item['summary']} |"
            )
    parts.append("")
    return "\n".join(parts)


def main(argv: list[str]) -> int:
    rows = collect()
    if not rows:
        print("没有找到任何【本机补丁】标记")
        return 1
    content = render(rows)

    if "--write" in argv:
        DOC.parent.mkdir(parents=True, exist_ok=True)
        DOC.write_text(content, encoding="utf-8")
        print(f"已写入 {DOC.relative_to(ROOT)}（{len(rows)} 处）")
        return 0

    if "--check" in argv:
        current = DOC.read_text(encoding="utf-8") if DOC.is_file() else ""
        if current != content:
            print("FAIL: docs/local-patches.md 与本机补丁标记不一致", file=sys.stderr)
            print("      修法：python scripts/local_patches.py --write", file=sys.stderr)
            return 1
        print(f"OK: {len(rows)} 处本机补丁与 docs/local-patches.md 一致")
        return 0

    print(content)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
