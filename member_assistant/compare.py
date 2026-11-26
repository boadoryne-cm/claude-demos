"""Compare prompt versions across several runs.

    python -m member_assistant.compare                 # every run graded with the current rules
"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

from member_assistant.evaluate import JUDGE_VERSION

HERE = Path(__file__).resolve().parent


def main() -> None:
    runs = defaultdict(list)  # prompt -> [ {id: row} ]
    for d in sorted((HERE / "results").iterdir()):
        if "fake" in d.name or not (d / "results.jsonl").exists():
            continue
        rows = [json.loads(l) for l in (d / "results.jsonl").read_text().splitlines()]
        if len(rows) < 31 or any(r.get("judge_version") != JUDGE_VERSION for r in rows):
            continue  # partial runs and runs graded with older rules are not comparable
        runs[d.name.split("-")[0]].append({r["id"]: r for r in rows})
    print(f"Grading rules v{JUDGE_VERSION}. Only complete runs.\n")
    print("| Prompt | Runs | Passed per run | Average | Unsupported claims per run |\n|---|---|---|---|---|")
    for p, rs in sorted(runs.items()):
        passed = [sum(r["passed"] for r in run.values()) for run in rs]
        unsup = [sum(len(r["judge"]["unsupported_claims"]) for r in run.values()) for run in rs]
        print(f"| {p} | {len(rs)} | {', '.join(map(str, passed))} of 31 | {100 * statistics.mean(passed) / 31:.0f}% | {', '.join(map(str, unsup))} |")
    ids = sorted({i for rs in runs.values() for run in rs for i in run})
    print("\nCases that failed at least once (times passed / runs):\n")
    print("| Case | " + " | ".join(sorted(runs)) + " |\n|---|" + "---|" * len(runs))
    for i in ids:
        cells = []
        for p in sorted(runs):
            got = [run[i]["passed"] for run in runs[p] if i in run]
            cells.append(f"{sum(got)}/{len(got)}")
        if any(c.split("/")[0] != c.split("/")[1] for c in cells):
            print(f"| {i} | " + " | ".join(cells) + " |")


if __name__ == "__main__":
    main()
