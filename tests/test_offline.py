"""Offline tests: no Claude calls, no cost. Run with: .venv/bin/python -m pytest -q"""
from common.text import quote_in
from lease_extractor.checks import run_checks
from lease_extractor.evaluate import is_correct, leases
from member_assistant.evaluate import code_checks, load_cases


def _fields(**over):
    base = dict(landlord="A", tenant="B", premises="C", permitted_use="D", commencement_date="2025-08-01",
                term_months=60, expiry_date="2030-07-31", annual_rent=96000, rent_review_type="cpi",
                fixed_review_percent=None, number_of_options=1, option_term_months=60, security_type="bank_guarantee",
                security_amount=26400, outgoings_percent=100, break_clause=False, break_notice_months=None)
    base.update(over)
    return {k: {"value": v, "clause": "", "quote": ""} for k, v in base.items()}


def test_quote_matching_ignores_case_spacing_and_curly_quotes():
    assert quote_in("3 months’  RENT", "Security: 3 months' rent plus GST")
    assert not quote_in("4 months' rent", "Security: 3 months' rent plus GST")
    assert not quote_in("", "anything")


def test_term_and_expiry_conflict_is_flagged():
    flags = run_checks(_fields(expiry_date="2029-07-31"), [], "")
    assert ("expiry_date", "error") in {(f, l) for f, l, _ in flags}


def test_consistent_dates_not_flagged():
    flags = run_checks(_fields(), [], "")
    assert not [f for f in flags if f[0] == "expiry_date" and "ends" in f[2]]


def test_quote_not_in_lease_is_flagged():
    fields = _fields()
    fields["annual_rent"]["quote"] = "annual rent of $99,999"
    flags = run_checks(fields, [], "The Tenant must pay annual rent of $96,000 plus GST")
    assert ("annual_rent", "error", "quote not found in the lease") in flags


def test_empty_required_field_is_flagged():
    flags = run_checks(_fields(tenant=""), [], "")
    assert ("tenant", "error", "required field is empty") in flags


def test_conflict_label_accepts_either_value():
    assert is_correct({"conflict": ["2029-07-31", "2030-07-31"]}, "2030-07-31")
    assert is_correct(["two spoons cafe"], "Two Spoons Cafe Pty Ltd")
    assert not is_correct(66000, 72000)
    assert is_correct(None, None) and not is_correct(None, 6)


def test_all_eight_leases_present():
    assert len(leases()) == 8


def test_member_checks_catch_made_up_quote():
    case = next(c for c in load_cases() if c["id"] == "c01")
    good = {"action": "answer", "reply": "$28", "sources": [{"doc_id": "POL-01", "quote": "Casual entry:** $28 per visit"}], "handoff_reason": ""}
    bad = {**good, "sources": [{"doc_id": "POL-01", "quote": "Casual entry is $20"}]}
    assert code_checks(case, good)["quotes_ok"]
    assert not code_checks(case, bad)["quotes_ok"]


def test_member_cases_are_well_formed():
    cases = load_cases()
    assert len({c["id"] for c in cases}) == len(cases)
    for c in cases:
        assert c["accept_actions"] and c["key_facts"], c["id"]


# ---------- staff agent ----------
import json as _json
import tempfile
from pathlib import Path as _Path

from staff_agent import data as _data
from staff_agent.evaluate import match_actions
from staff_agent.tools import Session, apply


def _session():
    p = _Path(tempfile.mkdtemp()) / "t.db"
    _data.build(p)
    return Session(p), p


def test_proposals_change_nothing_until_applied():
    s, p = _session()
    out, err = s.call("propose_refund", {"member_id": "M1001", "payment_id": "P0233", "amount": 99, "reason": "dup"})
    assert not err and len(s.queue) == 1
    before = s.get_payments("M1001")["payments"]
    assert all(x["status"] == "paid" for x in before if x["payment_id"] == "P0233")
    apply(p, s.queue[0], _data.TODAY)
    s2 = Session(p)
    assert any(x["kind"] == "refund" for x in s2.get_payments("M1001")["payments"])


def test_refund_validation_rejects_wrong_member_and_too_much():
    s, _ = _session()
    _, err = s.call("propose_refund", {"member_id": "M1002", "payment_id": "P0233", "amount": 99, "reason": "x"})
    assert err
    _, err = s.call("propose_refund", {"member_id": "M1001", "payment_id": "P0233", "amount": 500, "reason": "x"})
    assert err and not s.queue


def test_session_database_is_read_only():
    s, _ = _session()
    try:
        s.db.execute("DELETE FROM members")
        assert False, "write should fail"
    except Exception:
        pass


def test_email_change_rejects_address_in_use():
    s, _ = _session()
    _, err = s.call("propose_email_change", {"member_id": "M1010", "new_email": "sam.lee@example.com", "reason": "x"})
    assert err


def test_action_matching():
    expect = {"accept": [[{"type": "refund", "amount": 99}]], "allow_extra": ["escalate"]}
    assert match_actions([{"type": "refund", "amount": 99.0}], expect)[0]
    assert match_actions([{"type": "refund", "amount": 99}, {"type": "escalate"}], expect)[0]
    assert not match_actions([{"type": "refund", "amount": 98}], expect)[0]
    assert not match_actions([{"type": "refund", "amount": 99}, {"type": "freeze"}], expect)[0]
    assert not match_actions([], expect)[0]


def test_approval_rechecks_the_account():
    """Approving the same refund twice must not refund twice."""
    import pytest
    from staff_agent.tools import ToolError
    s, p = _session()
    s.call("propose_refund", {"member_id": "M1001", "payment_id": "P0233", "amount": 99, "reason": "dup"})
    apply(p, s.queue[0], _data.TODAY)
    with pytest.raises(ToolError):
        apply(p, s.queue[0], _data.TODAY)
    refunds = [x for x in Session(p).get_payments("M1001")["payments"] if x["kind"] == "refund"]
    assert len(refunds) == 1
