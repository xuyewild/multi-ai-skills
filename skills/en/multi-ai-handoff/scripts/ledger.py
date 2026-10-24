#!/usr/bin/env python3
"""Cost ledger for paid AI actions (video / image generation, paid APIs).
Records money or credits only; it never talks to any platform.

付费动作账本：先预留、再点一次、再结算。只记账，不操作平台。

Usage / 用法
  python3 ledger.py LEDGER.json init --unit credits --limit 5000 [--retry-limit 3]
  python3 ledger.py LEDGER.json reserve --id ep3-n07-a1 --item ep3/n07 --cost 120 [--kind first|retry|autofix|human]
  python3 ledger.py LEDGER.json submitted --id ep3-n07-a1 --task TASK_ID
  python3 ledger.py LEDGER.json unknown --id ep3-n07-a1      # clicked, not sure it was accepted
  python3 ledger.py LEDGER.json settle --id ep3-n07-a1 --charge 118
  python3 ledger.py LEDGER.json refund --id ep3-n07-a1 --amount 118
  python3 ledger.py LEDGER.json status [--item ep3/n07]

Rules enforced
  * reserve fails if spent + reserved + cost would exceed --limit
  * reserve fails if any attempt of the same item is still `unknown` (reconcile first, never re-click)
  * first + retry + autofix attempts of one item are capped at --retry-limit;
    `human` (owner asked for a redo) is counted separately
Exit codes: 0 ok, 1 refused by a rule, 2 usage error.
"""
import argparse
import json
import os
import sys
from decimal import Decimal
from pathlib import Path

CAPPED = ("first", "retry", "autofix")


def load(path):
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"ERROR ledger not found: {p} (run init first)")
    return json.loads(p.read_text(encoding="utf-8"))


def store(path, data):
    p = Path(path)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, p)


def D(x):
    return Decimal(str(x))


def totals(data):
    spent = sum(D(a.get("charge", 0)) - D(a.get("refund", 0)) for a in data["attempts"].values())
    reserved = sum(D(a["cost"]) for a in data["attempts"].values()
                   if a["state"] in ("reserved", "submitted", "unknown"))
    return spent, reserved


def refuse(msg):
    print("REFUSED " + msg)
    return 1


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("ledger")
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init")
    i.add_argument("--unit", required=True)
    i.add_argument("--limit", required=True)
    i.add_argument("--retry-limit", type=int, default=3)
    r = sub.add_parser("reserve")
    r.add_argument("--id", required=True)
    r.add_argument("--item", required=True)
    r.add_argument("--cost", required=True)
    r.add_argument("--kind", choices=CAPPED + ("human",), default="first")
    for name, extra in (("submitted", "--task"), ("unknown", None), ("settle", "--charge"), ("refund", "--amount")):
        s = sub.add_parser(name)
        s.add_argument("--id", required=True)
        if extra:
            s.add_argument(extra, required=True)
    st = sub.add_parser("status")
    st.add_argument("--item")
    a = p.parse_args(argv)

    if a.cmd == "init":
        if Path(a.ledger).exists():
            return refuse("ledger already exists; not overwriting")
        store(a.ledger, {"unit": a.unit, "limit": str(D(a.limit)),
                         "retry_limit": a.retry_limit, "attempts": {}})
        print("ok")
        return 0

    data = load(a.ledger)
    att = data["attempts"]

    if a.cmd == "status":
        spent, reserved = totals(data)
        print(f"limit {data['limit']} {data['unit']} | spent {spent} | reserved {reserved} | "
              f"left {D(data['limit']) - spent - reserved}")
        for k, v in att.items():
            if a.item and v["item"] != a.item:
                continue
            print(f"  {k}: {v['item']} {v['kind']} {v['state']} cost={v['cost']} "
                  f"charge={v.get('charge', '-')} task={v.get('task', '-')}")
        return 0

    if a.cmd == "reserve":
        if a.id in att:
            return refuse(f"attempt id {a.id} already used")
        same = [v for v in att.values() if v["item"] == a.item]
        if any(v["state"] == "unknown" for v in same):
            return refuse(f"{a.item} has an attempt in state `unknown`; reconcile with the platform first")
        if a.kind in CAPPED and sum(v["kind"] in CAPPED for v in same) >= data["retry_limit"]:
            return refuse(f"{a.item} reached the retry limit ({data['retry_limit']}); ask the owner")
        spent, reserved = totals(data)
        if spent + reserved + D(a.cost) > D(data["limit"]):
            return refuse("over budget; ask the owner")
        att[a.id] = {"item": a.item, "kind": a.kind, "cost": str(D(a.cost)), "state": "reserved"}
    else:
        if a.id not in att:
            return refuse(f"unknown attempt id {a.id}")
        rec = att[a.id]
        if a.cmd == "submitted":
            rec.update(state="submitted", task=a.task)
        elif a.cmd == "unknown":
            rec["state"] = "unknown"
        elif a.cmd == "settle":
            rec.update(state="settled", charge=str(D(a.charge)))
        elif a.cmd == "refund":
            if rec.get("refund"):
                print("ok (already refunded)")
                return 0
            rec.update(refund=str(D(a.amount)))
    store(a.ledger, data)
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
