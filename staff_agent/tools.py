"""The tools the staff agent can call.

Two kinds:
- Look-ups read the members database. They never change it.
- Proposals (refund, fee waiver, freeze, cancellation, email change, incident report,
  escalation) do NOT change anything. Code checks each one against the database and,
  if it is valid, puts it in a queue for a staff member to approve. Only apply()
  changes the database, and the agent cannot call it: the web page calls it when a
  person clicks Approve.
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import date
from pathlib import Path


def _obj(props: dict, required: list[str] | None = None) -> dict:
    return {"type": "object", "properties": props, "required": required if required is not None else list(props),
            "additionalProperties": False}


MID = {"type": "string", "description": "Member ID, e.g. M1001."}
REASON = {"type": "string", "description": "Why, in one sentence, naming the policy or procedure."}
DATE = {"type": "string", "description": "YYYY-MM-DD"}

TOOL_DEFS = [
    {"name": "find_member", "description": "Search members by email address, name or phone number. Returns matching members with their IDs. Use this first to work out whose account a ticket is about.",
     "input_schema": _obj({"query": {"type": "string", "description": "An email, a full or partial name, or a phone number."}})},
    {"name": "get_member", "description": "A member's profile: plan, status, start and end dates, billing day, price paid, concession, email on the account, and family account links.",
     "input_schema": _obj({"member_id": MID})},
    {"name": "get_payments", "description": "A member's payments for the last 12 months, newest first: payment ID, date, amount, kind (membership, annual, fee, class, refund), status (paid, failed, unpaid, refunded) and description.",
     "input_schema": _obj({"member_id": MID})},
    {"name": "get_bookings", "description": "A member's class bookings: class, start time, price paid, status (booked, attended, cancelled_by_member, cancelled_by_ridgeline, no_show), when it was cancelled, and the payment ID.",
     "input_schema": _obj({"member_id": MID})},
    {"name": "get_freezes", "description": "A member's freezes: start and end dates, whether medical, and status.",
     "input_schema": _obj({"member_id": MID})},
    {"name": "get_checkins", "description": "A member's check-ins at the gym, newest first.",
     "input_schema": _obj({"member_id": MID})},
    {"name": "get_account_history", "description": "Notes on a member's account: payment detail updates, fee waivers, refunds, suspensions and email changes.",
     "input_schema": _obj({"member_id": MID})},
    {"name": "propose_refund", "description": "Queue a refund of a payment for staff approval. Does not refund anything by itself.",
     "input_schema": _obj({"member_id": MID, "payment_id": {"type": "string"}, "amount": {"type": "number", "description": "Dollars, e.g. 99 or 197.5"}, "reason": REASON})},
    {"name": "propose_fee_waiver", "description": "Queue a waiver of a failed payment fee for staff approval.",
     "input_schema": _obj({"member_id": MID, "payment_id": {"type": "string", "description": "The fee payment's ID."}, "reason": REASON})},
    {"name": "propose_freeze", "description": "Queue a membership freeze for staff approval.",
     "input_schema": _obj({"member_id": MID, "start_date": DATE, "weeks": {"type": "integer"}, "medical": {"type": "boolean"}, "reason": REASON})},
    {"name": "propose_cancellation", "description": "Queue a membership cancellation for staff approval.",
     "input_schema": _obj({"member_id": MID, "effective_date": {**DATE, "description": "The day the membership ends, YYYY-MM-DD."}, "reason": REASON})},
    {"name": "propose_email_change", "description": "Queue a change to the email address on an account for staff approval.",
     "input_schema": _obj({"member_id": MID, "new_email": {"type": "string"}, "reason": REASON})},
    {"name": "propose_incident_report", "description": "Queue an injury incident report for staff approval.",
     "input_schema": _obj({"member_id": MID, "incident_date": DATE, "description": {"type": "string"}, "reported_late": {"type": "boolean", "description": "True if not reported to staff on the day."}})},
    {"name": "escalate_to_manager", "description": "Flag the case for a manager, for example a refund over $300, a compensation question, or anything the procedures don't cover.",
     "input_schema": _obj({"member_id": {**MID, "description": "Member ID, or empty if no member was identified."}, "reason": REASON})},
]
for t in TOOL_DEFS:
    t["strict"] = True

ACTION_TOOLS = {"propose_refund": "refund", "propose_fee_waiver": "fee_waiver", "propose_freeze": "freeze",
                "propose_cancellation": "cancellation", "propose_email_change": "email_change",
                "propose_incident_report": "incident_report", "escalate_to_manager": "escalate"}


class ToolError(Exception):
    """Shown to Claude as an error result so it can correct itself."""


def _rows(db: sqlite3.Connection, sql: str, *args) -> list[dict]:
    cur = db.execute(sql, args)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _member(db, mid: str) -> dict:
    rows = _rows(db, "SELECT * FROM members WHERE member_id = ?", (mid or "").strip().upper())
    if not rows:
        raise ToolError(f"No member with ID '{mid}'. Use find_member to look up the ID.")
    return rows[0]


def _date(s: str, field: str) -> date:
    try:
        return date.fromisoformat(s)
    except (TypeError, ValueError):
        raise ToolError(f"{field} must be a date in YYYY-MM-DD format, got '{s}'.")


class Session:
    """One agent run: a database connection plus the queue of proposed actions."""

    def __init__(self, db_path: Path):
        self.db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, check_same_thread=False)
        self.queue: list[dict] = []

    def close(self) -> None:
        self.db.close()

    # ---- look-ups -------------------------------------------------------------
    def find_member(self, query: str):
        q = (query or "").strip().lower()
        if not q:
            raise ToolError("query is empty.")
        digits = re.sub(r"\D", "", q)
        rows = _rows(self.db, """SELECT member_id, first_name, last_name, email, account_holder_id FROM members
                                 WHERE lower(email) = ? OR lower(first_name || ' ' || last_name) LIKE ?
                                 OR (? != '' AND replace(phone, ' ', '') LIKE ?)""",
                     q, f"%{q}%", digits, f"%{digits}%" if len(digits) >= 6 else "#")
        return {"matches": rows} if rows else {"matches": [], "note": "No member found for that search."}

    def get_member(self, member_id: str):
        m = _member(self.db, member_id)
        m["family_members"] = _rows(self.db, "SELECT member_id, first_name, last_name FROM members WHERE account_holder_id = ?", m["member_id"])
        return m

    def get_payments(self, member_id: str):
        _member(self.db, member_id)
        return {"payments": _rows(self.db, "SELECT payment_id, date, amount, kind, status, description, refund_of FROM payments WHERE member_id = ? ORDER BY date DESC, payment_id DESC", member_id.upper())}

    def get_bookings(self, member_id: str):
        _member(self.db, member_id)
        return {"bookings": _rows(self.db, "SELECT * FROM bookings WHERE member_id = ? ORDER BY class_start DESC", member_id.upper())}

    def get_freezes(self, member_id: str):
        _member(self.db, member_id)
        return {"freezes": _rows(self.db, "SELECT * FROM freezes WHERE member_id = ? ORDER BY start_date DESC", member_id.upper())}

    def get_checkins(self, member_id: str):
        _member(self.db, member_id)
        return {"checkins": [r["at"] for r in _rows(self.db, "SELECT at FROM checkins WHERE member_id = ? ORDER BY at DESC", member_id.upper())]}

    def get_account_history(self, member_id: str):
        _member(self.db, member_id)
        return {"history": _rows(self.db, "SELECT date, event, detail FROM history WHERE member_id = ? ORDER BY date DESC", member_id.upper())}

    # ---- proposals: validated, queued, never applied here ------------------
    def _queue(self, kind: str, params: dict, summary: str):
        action = {"id": f"A{len(self.queue) + 1}", "type": kind, **params, "summary": summary}
        self.queue.append(action)
        return {"queued": action["id"], "status": "Waiting for staff approval. Nothing has changed yet.", "summary": summary}

    def _payment(self, mid: str, pid: str) -> dict:
        rows = _rows(self.db, "SELECT * FROM payments WHERE payment_id = ?", (pid or "").strip().upper())
        if not rows or rows[0]["member_id"] != mid:
            raise ToolError(f"Payment '{pid}' does not belong to member {mid}.")
        return rows[0]

    def propose_refund(self, member_id, payment_id, amount, reason):
        m = _member(self.db, member_id)
        p = self._payment(m["member_id"], payment_id)
        if p["status"] != "paid" or p["amount"] <= 0:
            raise ToolError(f"Payment {p['payment_id']} has status '{p['status']}', so it can't be refunded.")
        if not 0 < amount <= p["amount"] + 1e-9:
            raise ToolError(f"Refund amount must be more than 0 and at most the payment amount (${p['amount']:.2f}).")
        return self._queue("refund", {"member_id": m["member_id"], "payment_id": p["payment_id"], "amount": round(amount, 2), "reason": reason},
                           f"Refund ${amount:,.2f} of {p['payment_id']} ({p['description']}) to {m['first_name']} {m['last_name']}")

    def propose_fee_waiver(self, member_id, payment_id, reason):
        m = _member(self.db, member_id)
        p = self._payment(m["member_id"], payment_id)
        if p["kind"] != "fee" or p["status"] not in ("paid", "unpaid"):
            raise ToolError(f"Payment {p['payment_id']} is not an outstanding or paid fee.")
        return self._queue("fee_waiver", {"member_id": m["member_id"], "payment_id": p["payment_id"], "amount": p["amount"], "reason": reason},
                           f"Waive the ${p['amount']:.2f} {p['description'].lower()} ({p['payment_id']}) for {m['first_name']} {m['last_name']}")

    def propose_freeze(self, member_id, start_date, weeks, medical, reason):
        m = _member(self.db, member_id)
        _date(start_date, "start_date")
        if not 1 <= weeks <= 26:
            raise ToolError("weeks must be between 1 and 26.")
        return self._queue("freeze", {"member_id": m["member_id"], "start_date": start_date, "weeks": weeks, "medical": medical, "reason": reason},
                           f"Freeze {m['first_name']} {m['last_name']}'s membership for {weeks} weeks from {start_date}" + (" (medical)" if medical else ""))

    def propose_cancellation(self, member_id, effective_date, reason):
        m = _member(self.db, member_id)
        _date(effective_date, "effective_date")
        return self._queue("cancellation", {"member_id": m["member_id"], "effective_date": effective_date, "reason": reason},
                           f"Cancel {m['first_name']} {m['last_name']}'s {m['plan']} membership, ending {effective_date}")

    def propose_email_change(self, member_id, new_email, reason):
        m = _member(self.db, member_id)
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", new_email or ""):
            raise ToolError(f"'{new_email}' is not a valid email address.")
        if _rows(self.db, "SELECT 1 FROM members WHERE lower(email) = ?", new_email.lower()):
            raise ToolError(f"{new_email} is already used by another account.")
        return self._queue("email_change", {"member_id": m["member_id"], "new_email": new_email, "reason": reason},
                           f"Change {m['first_name']} {m['last_name']}'s login email from {m['email']} to {new_email}")

    def propose_incident_report(self, member_id, incident_date, description, reported_late):
        m = _member(self.db, member_id)
        _date(incident_date, "incident_date")
        return self._queue("incident_report", {"member_id": m["member_id"], "incident_date": incident_date, "description": description, "reported_late": reported_late},
                           f"Log an incident for {m['first_name']} {m['last_name']} on {incident_date}" + (" (reported late)" if reported_late else "") + f": {description}")

    def escalate_to_manager(self, member_id, reason):
        if member_id:
            _member(self.db, member_id)
        return self._queue("escalate", {"member_id": (member_id or "").upper(), "reason": reason}, f"Escalate to a manager: {reason}")

    def call(self, name: str, args: dict) -> tuple[str, bool]:
        """Run a tool. Returns (JSON text for Claude, is_error)."""
        fn = getattr(self, name, None) if any(t["name"] == name for t in TOOL_DEFS) else None
        if fn is None:
            return json.dumps({"error": f"Unknown tool {name}"}), True
        try:
            return json.dumps(fn(**args), default=str), False
        except ToolError as e:
            return json.dumps({"error": str(e)}), True
        except TypeError as e:
            return json.dumps({"error": f"Bad arguments: {e}"}), True


def apply(db_path: Path, action: dict, today: date) -> str:
    """Carry out an approved action on the database. Only a person's approval calls this."""
    db = sqlite3.connect(db_path)
    try:
        return _apply(db, action, today)
    finally:
        db.close()


def _apply(db: sqlite3.Connection, action: dict, today: date) -> str:
    t, mid = action["type"], action.get("member_id")
    with db:
        # Re-check at approval time: the account may have changed since the proposal was made.
        if t in ("refund", "fee_waiver"):
            row = db.execute("SELECT amount, status FROM payments WHERE payment_id=?", (action["payment_id"],)).fetchone()
            if not row or row[1] == "refunded":
                raise ToolError(f"{action['payment_id']} has already been refunded or waived, so nothing was changed.")
            if t == "refund":
                done_before = -(db.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE refund_of=?", (action["payment_id"],)).fetchone()[0])
                if done_before + action["amount"] > row[0] + 0.005:
                    raise ToolError(f"Refunds of {action['payment_id']} would exceed what was paid, so nothing was changed.")
        if t == "email_change" and db.execute("SELECT 1 FROM members WHERE lower(email)=lower(?)", (action["new_email"],)).fetchone():
            raise ToolError(f"{action['new_email']} is now used by another account, so nothing was changed.")
        if t == "refund":
            n = db.execute("SELECT count(*) FROM payments").fetchone()[0] + 1
            db.execute("INSERT INTO payments VALUES (?,?,?,?,?,?,?,?)", (f"P{n:04d}", mid, str(today), -action["amount"], "refund", "paid", action["reason"], action["payment_id"]))
            if abs(action["amount"] - db.execute("SELECT amount FROM payments WHERE payment_id=?", (action["payment_id"],)).fetchone()[0]) < 0.01:
                db.execute("UPDATE payments SET status='refunded' WHERE payment_id=?", (action["payment_id"],))
            done = f"Refund of ${action['amount']:,.2f} recorded as {f'P{n:04d}'}."
        elif t == "fee_waiver":
            db.execute("UPDATE payments SET status='refunded', description=description || ' (waived)' WHERE payment_id=?", (action["payment_id"],))
            db.execute("INSERT INTO history VALUES (?,?,?,?)", (mid, str(today), "fee_waived", f"Fee {action['payment_id']} waived"))
            done = f"Fee {action['payment_id']} marked as waived."
        elif t == "freeze":
            n = db.execute("SELECT count(*) FROM freezes").fetchone()[0] + 1
            db.execute("INSERT INTO freezes VALUES (?,?,?,?,?,?)", (f"F{300 + n}", mid, action["start_date"], "", int(action["medical"]), f"scheduled ({action['weeks']} weeks)"))
            done = f"Freeze scheduled from {action['start_date']} for {action['weeks']} weeks."
        elif t == "cancellation":
            db.execute("UPDATE members SET status='cancelling', end_date=? WHERE member_id=?", (action["effective_date"], mid))
            done = f"Membership set to end on {action['effective_date']}."
        elif t == "email_change":
            db.execute("UPDATE members SET email=? WHERE member_id=?", (action["new_email"], mid))
            db.execute("INSERT INTO history VALUES (?,?,?,?)", (mid, str(today), "email_changed", f"Login email changed to {action['new_email']}"))
            done = f"Login email changed to {action['new_email']}."
        elif t == "incident_report":
            db.execute("INSERT INTO history VALUES (?,?,?,?)", (mid, str(today), "incident_logged", f"{action['incident_date']}: {action['description']}"))
            done = "Incident report logged."
        else:
            db.execute("INSERT INTO history VALUES (?,?,?,?)", (mid or "", str(today), "escalated", action["reason"]))
            done = "Sent to a manager."
    return done
