"""Plant one mistake at a time in real, correct extractions and see which ones the rule checks catch.
No Claude calls. Shows what a reviewer can rely on the checks for, and what still needs human eyes.

    python -m lease_extractor.stress_checks [results folder]
"""
from __future__ import annotations

import copy
import json
import sys
from collections import defaultdict
from pathlib import Path

from lease_extractor.checks import run_checks
from lease_extractor.evaluate import leases

HERE = Path(__file__).resolve().parent


def _year_later(d: str) -> str:
    return str(int(d[:4]) + 1) + d[4:]


MUTATIONS = {
    "rent typed wrong (+10%)": ("annual_rent", lambda f: round(f["value"] * 1.1)),
    "expiry a year late": ("expiry_date", lambda f: _year_later(f["value"])),
    "term wrong (12 months short)": ("term_months", lambda f: f["value"] - 12),
    "quote made up": ("annual_rent", None),
    "landlord and tenant swapped": ("tenant", None),
    "review % wrong (+1)": ("fixed_review_percent", lambda f: f["value"] + 1 if f["value"] else None),
    "security amount wrong (+$1,000)": ("security_amount", lambda f: f["value"] + 1000 if f["value"] else None),
    "options count wrong (+1)": ("number_of_options", lambda f: f["value"] + 1),
    "outgoings share wrong (+5 points)": ("outgoings_percent", lambda f: f["value"] + 5 if f["value"] not in (None, 100) else None),
    "break right flipped": ("break_clause", lambda f: not f["value"]),
}


def main() -> None:
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else sorted(p for p in (HERE / "results").iterdir() if "fake" not in p.name)[-1]
    texts = {k: t for k, (_, t) in leases().items()}
    rows = [json.loads(l) for l in (folder / "extractions.jsonl").read_text().splitlines()]
    caught, tried = defaultdict(int), defaultdict(int)
    for r in rows:
        if "error" in r:
            continue
        fields, issues, text = r["data"]["fields"], r["data"]["issues"], texts[r["lease"]]
        base = {(f, m) for f, _, m in run_checks(fields, [], text)}
        for name, (target, change) in MUTATIONS.items():
            f2 = copy.deepcopy(fields)
            if name == "quote made up":
                f2[target]["quote"] = f2[target]["quote"].replace("0", "5", 1) or "rent of $1"
            elif name == "landlord and tenant swapped":
                f2["tenant"]["value"], f2["landlord"]["value"] = fields["landlord"]["value"], fields["tenant"]["value"]
            else:
                new = change(f2[target])
                if new is None or new == f2[target]["value"]:
                    continue  # mutation doesn't apply to this lease
                f2[target]["value"] = new
            tried[name] += 1
            # Claude's own notes are left out: they were written about the real values.
            after = {(f, m) for f, _, m in run_checks(f2, [], text)}
            if after - base:
                caught[name] += 1
    print(f"Planted mistakes in {folder.name} (rule checks only, Claude's own notes excluded)\n")
    print("| Planted mistake | Caught |\n|---|---|")
    for name in MUTATIONS:
        if tried[name]:
            print(f"| {name} | {caught[name]}/{tried[name]} |")
    print(f"\nTotal: {sum(caught.values())}/{sum(tried.values())}")


if __name__ == "__main__":
    main()
