"""Extract every sample lease, run the rule checks, and score against the labels.

    python -m lease_extractor.evaluate               # real run (costs money)
    python -m lease_extractor.evaluate --ids L07     # one lease
    python -m lease_extractor.evaluate --fake oracle # offline plumbing test

Writes register.csv (one row per lease, ready for Google Sheets), review_queue.csv
(every flag a person should look at) and report.md.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from common.claude import CallFailed, fake_result
from common.text import norm
from lease_extractor.checks import run_checks
from lease_extractor.extract import EFFORT, FIELDS, MODEL, extract
from lease_extractor.labels import LABELS

HERE = Path(__file__).resolve().parent


def leases() -> dict[str, tuple[str, str]]:
    return {p.name[:3]: (p.name, p.read_text()) for p in sorted((HERE / "leases").glob("L*.md"))}


def fake_extraction(lid: str, kind: str):
    fields = {}
    for name, (t, _) in FIELDS.items():
        label = LABELS[lid][name]
        if kind == "oracle":
            value = " ".join(label) if isinstance(label, list) else (label["conflict"][0] if isinstance(label, dict) else label)
        else:
            value = {"string": "", "integer": 0, "number": 0, "boolean": False, "review_enum": "none",
                     "security_enum": "none"}.get(t)
        fields[name] = {"value": value, "clause": "", "quote": ""}
    issues = [{"fields": ["expiry_date"], "description": "term and expiry disagree"}] if kind == "oracle" and lid == "L07" else []
    return fake_result({"fields": fields, "issues": issues})


def is_correct(label, value) -> bool:
    if isinstance(label, dict):  # a deliberate conflict: any listed value is acceptable
        return value in label["conflict"]
    if isinstance(label, list):
        v = norm(str(value or ""))
        return all(tok in v for tok in label)
    if label is None:
        return value in (None, 0)
    if isinstance(label, bool) or isinstance(value, bool):
        return label is value
    if isinstance(label, (int, float)):
        return isinstance(value, (int, float)) and abs(value - label) < 0.5
    return value == label


def score(lid: str, data: dict, flags: list) -> list[dict]:
    flagged = defaultdict(list)
    for f, level, msg in flags:
        flagged[f].append(f"{level}: {msg}")
    rows = []
    for name in FIELDS:
        label = LABELS[lid][name]
        value = data["fields"][name]["value"]
        ok = is_correct(label, value)
        conflict = isinstance(label, dict)
        rows.append({"lease": lid, "field": name, "value": value, "label": label, "correct": ok,
                     "flagged": bool(flagged[name]), "flags": flagged[name], "conflict": conflict,
                     # a deliberate conflict only counts as handled if a person is pointed at it
                     "handled": ok and (not conflict or bool(flagged[name]))})
    return rows


def run_one(lid: str, name: str, text: str, fake: str | None) -> dict:
    try:
        res = fake_extraction(lid, fake) if fake else extract(text)
    except CallFailed as e:
        return {"lease": lid, "file": name, "error": e.kind, "detail": e.detail, "usage": e.usage}
    flags = run_checks(res.data["fields"], res.data["issues"], text)
    return {"lease": lid, "file": name, "data": res.data, "flags": flags, "scores": score(lid, res.data, flags),
            "model_served": res.model_served, "fallback_used": res.fallback_used, "usage": res.usage,
            "cost_usd": res.cost_usd, "seconds": round(res.seconds, 1), "request_id": res.request_id}


def report(rows: list[dict], errors: list[dict], fake: str | None) -> str:
    s = [x for r in rows for x in r["scores"]]
    n = len(s)
    correct = sum(x["correct"] for x in s)
    wrong = [x for x in s if not x["correct"]]
    caught = [x for x in wrong if x["flagged"]]
    false_alarms = [x for x in s if x["correct"] and x["flagged"] and not x["conflict"]]
    conflicts = [x for x in s if x["conflict"]]
    lines = [f"# Lease extraction results" + (f" (fake: {fake})" if fake else ""), "",
             f"Run at {datetime.now():%Y-%m-%d %H:%M}. Model: {MODEL} (effort {EFFORT}). "
             f"{len(rows)} leases, {len(FIELDS)} fields each.", "",
             f"**Fields correct: {correct}/{n} ({100 * correct / max(n, 1):.0f}%)**", "",
             f"- Wrong values flagged for review by the checks: {len(caught)}/{len(wrong)}",
             f"- Wrong values that slipped through unflagged: {len(wrong) - len(caught)}",
             f"- Correct values flagged anyway (extra review work): {len(false_alarms)}",
             f"- Deliberate conflicts flagged: {sum(x['flagged'] for x in conflicts)}/{len(conflicts)}",
             f"- Calls that failed (not scored): {len(errors)}", "",
             "| Field | Correct |", "|---|---|"]
    by_field = defaultdict(list)
    for x in s:
        by_field[x["field"]].append(x["correct"])
    lines += [f"| {f} | {sum(v)}/{len(v)} |" for f, v in by_field.items()]
    lines += ["", "| Lease | Correct | Flags raised |", "|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['file']} | {sum(x['correct'] for x in r['scores'])}/{len(r['scores'])} | {len(r['flags'])} |")
    if wrong:
        lines += ["", "## Wrong values", ""]
        for x in wrong:
            lines.append(f"- {x['lease']} {x['field']}: got `{x['value']}`, expected `{x['label']}`"
                         + (f" (flagged: {'; '.join(x['flags'])})" if x["flagged"] else " (NOT flagged)"))
    if false_alarms:
        lines += ["", "## Correct values that were flagged", ""]
        lines += [f"- {x['lease']} {x['field']} = `{x['value']}`: {'; '.join(x['flags'])}" for x in false_alarms]
    if rows and not fake:
        cost = sum(r["cost_usd"] for r in rows)
        lines += ["", "## Cost and speed", "",
                  f"- ${cost:.3f} total, ${cost / len(rows):.3f} per lease",
                  f"- {sum(r['seconds'] for r in rows) / len(rows):.0f}s per lease on average",
                  f"- Models that answered: {sorted({r['model_served'] for r in rows})}; fallbacks used: {sum(r['fallback_used'] for r in rows)}"]
    if errors:
        lines += ["", "## Calls that failed", ""] + [f"- {e['lease']}: {e['error']}: {e['detail']}" for e in errors]
    lines += ["", "Labels were written together with the fictional leases. Eight leases is a small sample, so treat percentages as indicative."]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", help="comma-separated lease ids, e.g. L01,L07")
    ap.add_argument("--fake", choices=["oracle", "null"])
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    todo = leases()
    if a.ids:
        todo = {k: v for k, v in todo.items() if k in a.ids.split(",")}
    started = time.monotonic()
    with ThreadPoolExecutor(a.workers) as ex:
        out = list(ex.map(lambda kv: run_one(kv[0], kv[1][0], kv[1][1], a.fake), todo.items()))
    rows = [r for r in out if "error" not in r]
    errors = [r for r in out if "error" in r]

    d = HERE / "results" / (f"{datetime.now():%Y%m%d-%H%M%S}" + (f"-fake-{a.fake}" if a.fake else ""))
    d.mkdir(parents=True)
    (d / "extractions.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
    with open(d / "register.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["lease_file", *FIELDS, "needs_review"])
        for r in rows:
            w.writerow([r["file"], *[r["data"]["fields"][k]["value"] for k in FIELDS],
                        "; ".join(sorted({fl[0] for fl in r["flags"]}))])
    with open(d / "review_queue.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["lease_file", "field", "value", "level", "reason", "quote"])
        for r in rows:
            for field, level, msg in r["flags"]:
                fv = r["data"]["fields"].get(field, {})
                w.writerow([r["file"], field, fv.get("value", ""), level, msg, fv.get("quote", "")])
    md = report(rows, errors, a.fake)
    (d / "report.md").write_text(md)
    print(md)
    print(f"Saved to {d} ({time.monotonic() - started:.0f}s)")


if __name__ == "__main__":
    main()
