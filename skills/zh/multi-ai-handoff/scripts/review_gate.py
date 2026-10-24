#!/usr/bin/env python3
"""Review gate: record independent reviews with file hashes, and block hand-off
when the reviewed files changed or the verdict is not PASS.

复核闸门：把独立复核的结论和所审文件的 SHA256 记下来；下一步开工前检查，
结论不是 PASS、或文件变了，就不放行。

Usage / 用法
  record  --stage S --dir D --report R.md --product F... [--basis F...] --mode MODE
  check   --stage S --dir D [--product F... --basis F... | --from-record] [--max-rework 2]
  ruling  --stage S --dir D --quote TEXT --source TEXT --product F... [--basis F...]

  A file may be given as `path#kw1,kw2`: only lines containing any keyword are
  hashed, so edits to unrelated rows of a shared table do not invalidate the record.
  文件可写成 `路径#关键词1,关键词2`：只对含关键词的行算哈希。

The report must contain exactly one line starting with `- 结论：` or `- Verdict:`
followed by PASS / REVISE / NEEDS_EVIDENCE / NEEDS_DECISION.

Exit codes: 0 = may proceed (PASS or RULED), 1 = blocked, 2 = usage error.
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

VERDICTS = ("PASS", "REVISE", "NEEDS_EVIDENCE", "NEEDS_DECISION")
VERDICT_RE = re.compile(r"^\s*-\s*(?:结论|Verdict)\s*[：:]\s*([A-Z_]+)", re.M)
MODES = ("independent", "degraded", "self")


def file_hash(spec):
    path, _, kws = spec.partition("#")
    p = Path(path)
    if not p.is_file():
        return None
    data = p.read_bytes()
    if kws:
        words = [k for k in kws.split(",") if k]
        lines = data.decode("utf-8", errors="replace").splitlines()
        data = "\n".join(l for l in lines if any(w in l for w in words)).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def hashes(specs):
    return {s: file_hash(s) for s in specs or []}


def parse_verdict(text):
    found = VERDICT_RE.findall(text)
    if len(found) != 1 or found[0] not in VERDICTS:
        return None
    return found[0]


def records(directory, stage):
    d = Path(directory)
    out = []
    for f in sorted(d.glob("*.review.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if r.get("stage") == stage:
            r["_file"] = f.name
            out.append(r)
    out.sort(key=lambda r: r.get("time", ""))
    return out


def save(directory, rec):
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    safe = re.sub(r"[^\w.-]+", "_", rec["stage"])
    path = d / f"{safe}_{stamp}.review.json"
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def cmd_record(a):
    text = Path(a.report).read_text(encoding="utf-8")
    verdict = parse_verdict(text)
    missing = [s for s, h in hashes(a.product + (a.basis or [])).items() if h is None]
    if missing:
        print("ERROR missing files: " + ", ".join(missing))
        return 2
    rec = {
        "kind": "review",
        "stage": a.stage,
        "time": dt.datetime.now().isoformat(timespec="microseconds"),
        "mode": a.mode,
        "verdict": verdict or "UNPARSEABLE",
        "product": hashes(a.product),
        "basis": hashes(a.basis),
        "report": text,
    }
    path = save(a.dir, rec)
    print(f"recorded {rec['verdict']} -> {path}")
    return 0


def cmd_ruling(a):
    rec = {
        "kind": "ruling",
        "stage": a.stage,
        "time": dt.datetime.now().isoformat(timespec="microseconds"),
        "verdict": "RULED",
        "quote": a.quote,
        "source": a.source,
        "product": hashes(a.product),
        "basis": hashes(a.basis),
    }
    if None in rec["product"].values() or None in rec["basis"].values():
        print("ERROR missing files")
        return 2
    path = save(a.dir, rec)
    print(f"recorded RULED -> {path}")
    return 0


def cmd_check(a):
    recs = records(a.dir, a.stage)
    if a.from_record:
        if not recs:
            print("STATUS MISSING")
            return 1
        latest = recs[-1]
    else:
        wanted = set(a.product or [])
        same = [r for r in recs if set(r["product"]) == wanted]
        if not same:
            print("STATUS MISSING")
            return 1
        latest = same[-1]
        recs = same
    for spec, old in {**latest["product"], **latest["basis"]}.items():
        if file_hash(spec) != old:
            print(f"STATUS STALE  changed: {spec}")
            return 1
    if not a.from_record and set(a.basis or []) - set(latest["basis"]):
        print("STATUS STALE  new basis files not covered by the record")
        return 1
    v = latest["verdict"]
    if v == "RULED":
        print(f"STATUS RULED  (human ruling: {latest['source']})")
        return 0
    if v == "PASS":
        if latest.get("mode") == "self":
            print("STATUS SELF_REVIEW  a self-review cannot release the gate")
            return 1
        print("STATUS PASS")
        return 0
    # count rework rounds since the last PASS / RULED
    rounds = 0
    for r in reversed(recs):
        if r["verdict"] in ("PASS", "RULED"):
            break
        if r["verdict"] == "REVISE":
            rounds += 1
    if v == "REVISE" and rounds > a.max_rework:
        print(f"STATUS LIMIT  {rounds} REVISE rounds; stop and ask the owner")
        return 1
    print(f"STATUS {v}")
    return 1


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("--stage", required=True)
    r.add_argument("--dir", required=True)
    r.add_argument("--report", required=True)
    r.add_argument("--product", nargs="+", required=True)
    r.add_argument("--basis", nargs="*", default=[])
    r.add_argument("--mode", choices=MODES, required=True,
                   help="independent = read-only reviewer in its own context; "
                        "degraded = isolation by prompt only; self = author reviewed itself")
    c = sub.add_parser("check")
    c.add_argument("--stage", required=True)
    c.add_argument("--dir", required=True)
    c.add_argument("--product", nargs="*", default=[])
    c.add_argument("--basis", nargs="*", default=[])
    c.add_argument("--from-record", action="store_true",
                   help="use the file list stored in the latest record")
    c.add_argument("--max-rework", type=int, default=2)
    u = sub.add_parser("ruling")
    u.add_argument("--stage", required=True)
    u.add_argument("--dir", required=True)
    u.add_argument("--quote", required=True, help="the owner's exact words")
    u.add_argument("--source", required=True, help="where / when the owner said it")
    u.add_argument("--product", nargs="+", required=True)
    u.add_argument("--basis", nargs="*", default=[])
    a = p.parse_args(argv)
    if a.cmd == "check" and not a.from_record and not a.product:
        p.error("check needs --product or --from-record")
    return {"record": cmd_record, "check": cmd_check, "ruling": cmd_ruling}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
