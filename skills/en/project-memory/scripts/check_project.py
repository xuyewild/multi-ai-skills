#!/usr/bin/env python3
"""Project-memory check: rule ledger format and key shared files.

项目记忆巡检：检查规则台账格式和 00_项目/ 下的关键文件。

Usage / 用法
  check_project.py --project ROOT [--require FILE...] [--ledger NAME] [--out REPORT.md]

  The shared folder is 00_项目/ (Chinese layout) or 00_project/ (English layout);
  defaults for --ledger and --require follow whichever exists.
  共用文件夹是 00_项目/ 或 00_project/，--ledger、--require 的默认值跟着变。

Checks / 检查
  - 00_项目/<ledger> exists and has a 优先序 / Priority section
  - every rule row has an id, a valid status, a quote when 现行/active,
    and 替代/Replaced-by pointing to existing ids
  - required files under 00_项目/ exist (missing = warning) and are non-empty (empty = problem)
  - every .md / .json / .csv under 00_项目/ is valid UTF-8

Exit codes: 0 = no problems, 1 = problems found, 2 = usage error.
"""
import argparse
import re
import sys
from pathlib import Path

LAYOUTS = {
    "00_项目": ("规则台账.md", ["已定设定表.md", "进度摘要.md", "负责人备忘.md"]),
    "00_project": ("rule-ledger.md", ["settled-facts.md", "progress-summary.md", "owner-notes.md"]),
}
STATUS = {"现行": "active", "已替代": "replaced", "待定": "pending",
          "active": "active", "replaced": "replaced", "pending": "pending"}
ID_RE = re.compile(r"\bR\d{3,}\b")
COLS = {
    "id": ("编号", "id"),
    "quote": ("原话", "quote"),
    "status": ("状态", "status"),
    "replaced": ("替代", "replaced by", "replaced-by"),
}


def clean(cell):
    return re.sub(r"\*\*|`", "", cell).strip()


def split_row(line):
    # A row like "| a | b \| c |": split on unescaped pipes only.
    body = line.strip().strip("|")
    return [clean(c.replace("\\|", "|")) for c in re.split(r"(?<!\\)\|", body)]


def read_text(path, problems):
    try:
        return path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        problems.append(f"{path.name} 不是 UTF-8 / not UTF-8")
        return None


def check_ledger(path, problems):
    text = read_text(path, problems)
    if text is None:
        return
    if not re.search(r"^#+\s*(优先序|Priority)", text, re.M | re.I):
        problems.append(f"{path.name}：没有“优先序”一节 / no priority section")
    header, rows = None, []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            if rows:
                break  # only the first rule table counts
            header = None
            continue
        cells = split_row(line)
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        low = [c.lower() for c in cells]
        if header is None and any(c in COLS["id"] for c in low):
            header = {k: next((i for i, c in enumerate(low) if c in v), None)
                      for k, v in COLS.items()}
            continue
        if header is not None:
            rows.append(cells)
    if not rows:
        problems.append(f"{path.name}：找不到规则表 / no rule table")
        return
    h = header
    ids = set()
    for cells in rows:
        rid = cells[h["id"]] if h["id"] is not None and h["id"] < len(cells) else ""
        if not ID_RE.fullmatch(rid):
            problems.append(f"{path.name}：一行没有合法编号 / row without id: {'|'.join(cells)[:60]}")
            continue
        if rid in ids:
            problems.append(f"{path.name}：编号重复 / duplicate id {rid}")
        ids.add(rid)
    for cells in rows:
        get = lambda k: cells[h[k]] if h[k] is not None and h[k] < len(cells) else ""
        rid = get("id")
        if not ID_RE.fullmatch(rid):
            continue
        status = STATUS.get(get("status").lower())
        if status is None:
            problems.append(f"{rid}：状态“{get('status')}”不是 现行/已替代/待定")
            continue
        if status == "active" and get("quote") in ("", "—", "-"):
            problems.append(f"{rid}：现行条目没有原话 / active rule without quote")
        if status == "replaced":
            refs = ID_RE.findall(get("replaced"))
            if not refs:
                problems.append(f"{rid}：已替代但没写替代编号 / replaced without target")
            for r in refs:
                if r not in ids:
                    problems.append(f"{rid}：替代编号 {r} 不存在 / unknown target")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--project", required=True)
    ap.add_argument("--require", nargs="*")
    ap.add_argument("--ledger")
    ap.add_argument("--out")
    a = ap.parse_args(argv)

    root = Path(a.project)
    found = [n for n in LAYOUTS if (root / n).is_dir()]
    if not found:
        print(f"找不到 {root}/00_项目 或 00_project / shared folder not found", file=sys.stderr)
        return 2
    SHARED = found[0]
    shared = root / SHARED
    default_ledger, default_require = LAYOUTS[SHARED]
    a.ledger = a.ledger or default_ledger
    a.require = default_require if a.require is None else a.require

    problems, warnings = [], []
    ledger = shared / a.ledger
    if ledger.is_file():
        check_ledger(ledger, problems)
    else:
        problems.append(f"没有规则台账 {SHARED}/{a.ledger} / no rule ledger")
    for name in a.require:
        p = shared / name
        if not p.exists():
            warnings.append(f"缺 {SHARED}/{name} / missing")
        elif p.is_file() and p.stat().st_size == 0:
            problems.append(f"{SHARED}/{name} 是空文件 / empty file")
    for p in sorted(shared.rglob("*")):
        if p.is_file() and p.suffix in (".md", ".json", ".csv") and p != ledger:
            read_text(p, problems)

    lines = ["# 巡检 / Check", ""]
    lines += [f"- 问题 / problem：{x}" for x in problems]
    lines += [f"- 提醒 / warning：{x}" for x in warnings]
    if not problems and not warnings:
        lines.append("- 无问题 / OK")
    report = "\n".join(lines) + "\n"
    print(report, end="")
    if a.out:
        out = Path(a.out)
        out = out if out.is_absolute() else root / out
        out.write_text(report, encoding="utf-8")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
