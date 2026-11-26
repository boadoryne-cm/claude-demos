"""Pull key terms out of a commercial lease with Claude.

    python -m lease_extractor.extract lease_extractor/leases/L01-two-spoons-cafe.md

Every value comes back with the clause it came from and a word-for-word quote,
so a person (and checks.py) can confirm it against the document.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common.claude import call_json

MODEL = "claude-opus-5-5"
EFFORT = "high"

# name: (JSON type for value, definition shown to Claude)
FIELDS = {
    "landlord": ("string", "Landlord's name as written, without the ACN."),
    "tenant": ("string", "Tenant's name as written, without the ACN."),
    "premises": ("string", "Address or description of the premises."),
    "permitted_use": ("string", "What the premises may be used for."),
    "commencement_date": ("string", "Start date of the lease, YYYY-MM-DD."),
    "term_months": ("integer", "Length of the current term in months, after any deed of variation."),
    "expiry_date": ("string", "End date of the current term, YYYY-MM-DD, after any deed of variation."),
    "annual_rent": ("number", "Base rent per year, excluding GST, payable from the commencement date. Apply any special condition or variation that changes it. Convert weekly or monthly amounts to a yearly amount. Ignore rent-free periods and other incentives."),
    "rent_review_type": ("review_enum", "How rent is reviewed during the initial term: fixed (set percentage), cpi, market, mixed (more than one method), or none."),
    "fixed_review_percent": ("number|null", "Percentage of any fixed increase, for example 4 for 4%. Null if there is no fixed increase."),
    "number_of_options": ("integer", "Number of options to renew. 0 if none."),
    "option_term_months": ("integer|null", "Length of each option term in months. Null if there are no options."),
    "security_type": ("security_enum", "bank_guarantee, cash_bond, or none. A personal guarantee alone counts as none."),
    "security_amount": ("number|null", "Dollar amount of the security. If it is stated as a formula (for example 3 months' rent plus GST), calculate it. Null if none."),
    "outgoings_percent": ("number|null", "Tenant's share of outgoings as a percentage, for example 12.5. 0 if the tenant pays none; 100 if the tenant pays all."),
    "break_clause": ("boolean", "True if the landlord or tenant may end the lease early for a reason other than breach (for example a tenant break right or a landlord redevelopment clause)."),
    "break_notice_months": ("integer|null", "Notice period in months for that early-ending right. Null if there is none."),
}

# The API rejected a schema with 17 typed sub-objects ("compiled grammar is too large"),
# so Claude returns every value as text in one simple list and the code converts it.
SCHEMA = {
    "type": "object",
    "properties": {
        "fields": {
            "type": "array",
            "description": "One entry for every field, in the order listed.",
            "items": {
                "type": "object",
                "properties": {
                    "field": {"type": "string", "enum": list(FIELDS)},
                    "value": {"type": "string", "description": "Plain text: numbers without $ or commas, dates as YYYY-MM-DD, true or false, empty if none."},
                    "clause": {"type": "string", "description": "Clause or schedule item, e.g. 'Item 7' or 'clause 4.1'. Empty if not stated."},
                    "quote": {"type": "string", "description": "Exact words copied from the lease that support the value. Empty if the lease is silent."},
                },
                "required": ["field", "value", "clause", "quote"],
                "additionalProperties": False,
            },
        },
        "issues": {
            "type": "array",
            "description": "Conflicts, ambiguities or anything a person should check. Empty if none.",
            "items": {
                "type": "object",
                "properties": {
                    "fields": {"type": "array", "items": {"type": "string", "enum": list(FIELDS)}},
                    "description": {"type": "string"},
                },
                "required": ["fields", "description"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["fields", "issues"],
    "additionalProperties": False,
}

ENUMS = {"review_enum": {"fixed", "cpi", "market", "mixed", "none"}, "security_enum": {"bank_guarantee", "cash_bond", "none"}}


def coerce(t: str, raw: str):
    """Turn Claude's text value into the field's type. Raises ValueError if it can't."""
    s = (raw or "").strip()
    nullable = t.endswith("|null")
    base = t.split("|")[0]
    if s == "" or (s.lower() in ("null", "none", "n/a") and base not in ENUMS):
        if base == "string":
            return ""
        if base == "boolean":
            return False
        return None if nullable else 0
    if base == "string":
        return s
    if base in ENUMS:
        if s.lower() not in ENUMS[base]:
            raise ValueError(f"not one of {sorted(ENUMS[base])}")
        return s.lower()
    if base == "boolean":
        if s.lower() in ("true", "yes"):
            return True
        if s.lower() in ("false", "no"):
            return False
        raise ValueError("not true or false")
    n = float(s.replace("$", "").replace(",", "").replace("%", ""))
    return int(n) if base == "integer" else n


def to_record(data: dict) -> tuple[dict, list[dict]]:
    """Claude's list -> {field: {value, clause, quote}} plus problems found while converting."""
    fields, problems = {}, []
    for item in data["fields"]:
        if item["field"] in fields:
            problems.append({"fields": [item["field"]], "description": "field returned twice; first kept"})
            continue
        t = FIELDS[item["field"]][0]
        try:
            value = coerce(t, item["value"])
        except ValueError as e:
            problems.append({"fields": [item["field"]], "description": f"unreadable value '{item['value']}': {e}"})
            value = None
        fields[item["field"]] = {"value": value, "clause": item["clause"], "quote": item["quote"]}
    for name, (t, _) in FIELDS.items():
        if name not in fields:
            problems.append({"fields": [name], "description": "field missing from the answer"})
            fields[name] = {"value": coerce(t, ""), "clause": "", "quote": ""}
    return fields, problems


SYSTEM = """You extract key terms from Australian commercial and retail leases for a property manager's lease register.

Read the whole document, including schedules, special conditions and any deed of variation. Later documents and special conditions change earlier terms when they say so.

Return one entry for every field below. For each, give the value as plain text, the clause it came from, and a quote copied word for word from the lease. Quotes must be exact so they can be found in the document; keep them short. If the lease is silent on a field, use the empty or null value the definition allows and leave the quote empty.

If two parts of the lease disagree, or a value needs a calculation or judgement, still give your best value and record it under issues so a person checks it. Do not guess silently.

Fields:
""" + "\n".join(f"- {name}: {definition}" for name, (_, definition) in FIELDS.items())


def extract(lease_text: str):
    """Returns the API Result with .data = {"fields": {...typed...}, "issues": [...]}."""
    r = call_json(model=MODEL, system=SYSTEM, user=f"<lease>\n{lease_text}\n</lease>",
                  schema=SCHEMA, effort=EFFORT, max_tokens=16000)
    r.extra["raw"] = r.data
    fields, problems = to_record(r.data)
    r.data = {"fields": fields, "issues": r.data["issues"] + problems}
    return r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("lease", type=Path)
    a = ap.parse_args()
    r = extract(a.lease.read_text())
    print(json.dumps(r.data, indent=2, ensure_ascii=False))
    print(f"\n[{r.model_served}, ${r.cost_usd:.4f}, {r.seconds:.1f}s]")


if __name__ == "__main__":
    main()
