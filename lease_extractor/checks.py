"""Rule checks on an extraction. They don't know the right answers; they look for
things a careful person would want to double-check before trusting the register.

Each flag is (field, level, message). level "error" means the value can't be trusted
as is; "check" means it is probably right but was calculated or judged.
"""
from __future__ import annotations

import re
from datetime import date, timedelta

from common.text import quote_in

EMPTY = (None, "", "none", 0, False)


def _add_months(d: date, months: int) -> date:
    y, m = divmod(d.month - 1 + months, 12)
    return date(d.year + y, m + 1, d.day)


def _date(v) -> date | None:
    try:
        return date.fromisoformat(v)
    except (TypeError, ValueError):
        return None


def _numbers(text: str) -> list[float]:
    return [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*(?:\.\d+)?", text or "")]


def run_checks(fields: dict, issues: list[dict], lease_text: str) -> list[tuple[str, str, str]]:
    flags: list[tuple[str, str, str]] = []
    v = {k: f["value"] for k, f in fields.items()}

    # 1. Every value must be backed by a quote that really is in the lease.
    for name, f in fields.items():
        if f["quote"] and not quote_in(f["quote"], lease_text):
            flags.append((name, "error", "quote not found in the lease"))
        elif not f["quote"] and f["value"] not in EMPTY:
            flags.append((name, "error", "value given without a supporting quote"))

    # 2. Every lease has these; an empty one means something was missed.
    for name in ("landlord", "tenant", "premises", "commencement_date", "term_months", "expiry_date", "annual_rent"):
        if v[name] in EMPTY:
            flags.append((name, "error", "required field is empty"))

    # 3. Dates must agree with the term.
    start, end, term = _date(v["commencement_date"]), _date(v["expiry_date"]), v["term_months"]
    if v["commencement_date"] and not start:
        flags.append(("commencement_date", "error", "not a valid YYYY-MM-DD date"))
    if v["expiry_date"] and not end:
        flags.append(("expiry_date", "error", "not a valid YYYY-MM-DD date"))
    if start and end and isinstance(term, int) and term > 0:
        expected = _add_months(start, term) - timedelta(days=1)
        if expected != end:
            msg = f"start + {term} months ends {expected.isoformat()}, but expiry is {end.isoformat()}"
            flags.append(("expiry_date", "error", msg))
            flags.append(("term_months", "error", msg))

    # 4. Rent should be traceable to a number in its quote (as is, x12 monthly or x52 weekly).
    rent = v["annual_rent"]
    if isinstance(rent, (int, float)):
        if rent <= 0:
            flags.append(("annual_rent", "error", "rent is zero or negative"))
        else:
            nums = _numbers(fields["annual_rent"]["quote"])
            if not any(abs(rent - n * k) < 1 for n in nums for k in (1, 12, 52)):
                flags.append(("annual_rent", "check", "rent does not match a figure in its quote"))

    # 5. Review settings must hang together.
    if v["rent_review_type"] in ("fixed", "mixed") and v["fixed_review_percent"] in (None, 0):
        flags.append(("fixed_review_percent", "error", "fixed review without a percentage"))
    if v["rent_review_type"] in ("cpi", "market", "none") and v["fixed_review_percent"] not in (None, 0):
        flags.append(("fixed_review_percent", "error", "percentage given but review is not fixed"))
    if isinstance(v["fixed_review_percent"], (int, float)) and not 0 < v["fixed_review_percent"] <= 10:
        flags.append(("fixed_review_percent", "check", "unusual review percentage"))

    # 6. Options.
    if (v["number_of_options"] or 0) > 0 and not v["option_term_months"]:
        flags.append(("option_term_months", "error", "options without an option term"))
    if (v["number_of_options"] or 0) == 0 and v["option_term_months"]:
        flags.append(("option_term_months", "error", "option term but no options"))

    # 7. Security.
    if v["security_type"] == "none" and v["security_amount"] not in (None, 0):
        flags.append(("security_amount", "error", "amount given but security type is none"))
    if v["security_type"] != "none" and not v["security_amount"]:
        flags.append(("security_amount", "error", "security without an amount"))
    if isinstance(v["security_amount"], (int, float)) and v["security_amount"]:
        if not any(abs(v["security_amount"] - n) < 1 for n in _numbers(fields["security_amount"]["quote"])):
            flags.append(("security_amount", "check", "amount was calculated, not stated; check the maths"))

    # 8. Outgoings and break clause.
    if isinstance(v["outgoings_percent"], (int, float)) and not 0 <= v["outgoings_percent"] <= 100:
        flags.append(("outgoings_percent", "error", "outgoings share outside 0 to 100"))
    if v["break_clause"] and not v["break_notice_months"]:
        flags.append(("break_notice_months", "error", "break right without a notice period"))
    if not v["break_clause"] and v["break_notice_months"]:
        flags.append(("break_notice_months", "error", "notice period but no break right"))

    # 9. The value should be visible in its own quote (catches values copied from the wrong place).
    words = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}
    filler = {"pty", "ltd", "limited", "as", "trustee", "for", "the", "and", "trading", "acn", "abn"}
    for name in ("landlord", "tenant"):
        toks = [t for t in re.findall(r"[a-z]+", str(v[name] or "").lower()) if t not in filler]
        q = set(re.findall(r"[a-z]+", fields[name]["quote"].lower()))
        if toks and q and sum(t in q for t in toks) < len(toks) / 2:
            flags.append((name, "error", "name does not match its quote"))
    for name in ("fixed_review_percent", "outgoings_percent"):
        x = v[name]
        if isinstance(x, (int, float)) and x and fields[name]["quote"]:
            if not any(abs(x - n) < 0.01 for n in _numbers(fields[name]["quote"])) and not (x == 100 and "all" in fields[name]["quote"].lower()):
                flags.append((name, "error", "value does not appear in its quote"))
    n_opt = v["number_of_options"]
    if isinstance(n_opt, int) and n_opt > 0 and fields["number_of_options"]["quote"]:
        q = fields["number_of_options"]["quote"].lower()
        if str(n_opt) not in q and words.get(n_opt, "#") not in q and not (n_opt == 1 and re.search(r"\b(an|one|a)\b", q)):
            flags.append(("number_of_options", "error", "count does not appear in its quote"))

    # 10. Anything Claude itself raised.
    for issue in issues:
        for name in issue["fields"] or ["(general)"]:
            flags.append((name, "check", "Claude: " + issue["description"]))
    return flags
