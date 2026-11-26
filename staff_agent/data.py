"""The fictional Ridgeline members database the staff agent works against.

    python -m staff_agent.data            # writes staff_agent/ridgeline.db

Every member here exists to test one situation in tickets.py. TODAY is fixed so
results don't change with the calendar.
"""
from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
DB_PATH = HERE / "ridgeline.db"
TODAY = date(2026, 11, 26)  # a Thursday

SCHEMA = """
CREATE TABLE members (
  member_id TEXT PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT UNIQUE, phone TEXT,
  plan TEXT, status TEXT, start_date TEXT, end_date TEXT, billing_day INTEGER, price REAL,
  concession INTEGER, account_holder_id TEXT, birth_year INTEGER
);
CREATE TABLE payments (
  payment_id TEXT PRIMARY KEY, member_id TEXT, date TEXT, amount REAL, kind TEXT, status TEXT,
  description TEXT, refund_of TEXT
);
CREATE TABLE bookings (
  booking_id TEXT PRIMARY KEY, member_id TEXT, class_name TEXT, class_start TEXT, price_paid REAL,
  status TEXT, cancelled_at TEXT, payment_id TEXT
);
CREATE TABLE freezes (
  freeze_id TEXT PRIMARY KEY, member_id TEXT, start_date TEXT, end_date TEXT, medical INTEGER, status TEXT
);
CREATE TABLE checkins (member_id TEXT, at TEXT);
CREATE TABLE history (member_id TEXT, date TEXT, event TEXT, detail TEXT);
"""

#            id       first     last      email                          plan       status       start         end           day  price  conc holder
MEMBERS = [
    ("M1001", "Sam", "Lee", "sam.lee@example.com", "monthly", "active", "2025-03-14", None, 14, 99, 0, None),
    ("M1002", "Priya", "Shah", "priya.shah@example.com", "monthly", "active", "2024-06-03", None, 3, 99, 0, None),
    ("M1003", "Tom", "Becker", "tom.becker@example.com", "monthly", "active", "2025-01-09", None, 9, 99, 0, None),
    ("M1004", "Mia", "Chen", "mia.chen@example.com", "annual", "active", "2026-11-22", "2027-11-21", None, 990, 0, None),
    ("M1005", "Jack", "Wilson", "jack.wilson@example.com", "annual", "active", "2026-11-20", "2027-11-19", None, 990, 0, None),
    ("M1006", "Olivia", "Brown", "olivia.brown@example.com", "annual", "active", "2026-03-01", "2027-02-28", None, 990, 0, None),
    ("M1007", "Noah", "Taylor", "noah.taylor@example.com", "annual", "active", "2026-05-10", "2027-05-09", None, 990, 0, None),
    ("M1008", "Grace", "Kim", "grace.kim@example.com", "monthly", "active", "2025-08-20", None, 20, 99, 0, None),
    ("M1009", "Liam", "Nguyen", "liam.nguyen@example.com", "monthly", "active", "2025-02-01", None, 1, 99, 0, None),
    ("M1010", "Ava", "Martin", "ava.martin@example.com", "monthly", "active", "2025-10-07", None, 7, 99, 0, None),
    ("M1011", "Ethan", "Ross", "ethan.ross@example.com", "monthly", "active", "2024-12-12", None, 12, 99, 0, None),
    ("M1012", "Zoe", "Clark", "zoe.clark@example.com", "monthly", "active", "2026-02-17", None, 17, 84.15, 1, None),
    ("M1013", "Ben", "Harris", "ben.harris@example.com", "monthly", "active", "2025-05-22", None, 22, 99, 0, None),
    ("M1014", "Chloe", "Wright", "chloe.wright@example.com", "monthly", "active", "2025-07-02", None, 2, 99, 0, None),
    ("M1015", "Daniel", "Wright", "dan.wright@example.com", "monthly", "active", "2025-07-02", None, 2, 99, 0, None),
    ("M1016", "Karen", "Lopez", "karen.lopez@example.com", "monthly", "active", "2025-09-05", None, 5, 99, 0, None),
    ("M1017", "Leo", "Lopez", "karen.lopez+leo@example.com", "monthly", "active", "2025-09-05", None, 5, 84.15, 1, "M1016"),
    ("M1018", "Ruby", "Adams", "ruby.adams@example.com", "monthly", "active", "2025-11-28", None, 28, 99, 0, None),
    ("M1019", "Henry", "Scott", "henry.scott@example.com", "monthly", "active", "2026-01-25", None, 25, 99, 0, None),
    ("M1020", "Isla", "Turner", "isla.turner@example.com", "monthly", "suspended", "2025-04-15", None, 15, 99, 0, None),
    ("M1021", "Oscar", "Hall", "oscar.hall@example.com", "annual", "active", "2026-07-15", "2027-07-14", None, 990, 0, None),
    ("M1022", "Ella", "King", "ella.king@example.com", "monthly", "active", "2025-06-30", None, 30, 99, 0, None),
    ("M1023", "Max", "Young", "max.young@example.com", "monthly", "active", "2025-08-14", None, 14, 99, 0, None),
]
BIRTH = {"M1017": 2010}

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]


def _monthly_dates(start: date, day: int, until: date) -> list[date]:
    """Billing dates from the later of start or 12 months ago, up to and including `until`."""
    out, y, m = [], until.year - 1, until.month
    while (y, m) <= (until.year, until.month):
        d = date(y, m, min(day, 28) if m == 2 else min(day, 30) if m in (4, 6, 9, 11) else day)
        if start <= d <= until:
            out.append(d)
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def build(path: Path = DB_PATH) -> Path:
    path = Path(path)
    if path.exists():
        path.unlink()
    db = sqlite3.connect(path)
    db.executescript(SCHEMA)
    pay, n = [], [0]

    def p(mid, d, amount, kind, status, desc, refund_of=None):
        n[0] += 1
        pid = f"P{n[0]:04d}"
        pay.append((pid, mid, str(d), amount, kind, status, desc, refund_of))
        return pid

    failed = {("M1002", "2026-11-03"), ("M1003", "2026-06-09"), ("M1003", "2026-11-09"), ("M1020", "2026-11-15")}
    for mid, first, last, email, plan, status, start, end, day, price, conc, holder in MEMBERS:
        db.execute("INSERT INTO members VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                   (mid, first, last, email, f"0400 000 {mid[-3:]}", plan, status, start, end, day, price,
                    conc, holder, BIRTH.get(mid)))
        if plan == "annual":
            p(mid, start, price, "annual", "paid", "Annual membership")
        else:
            for d in _monthly_dates(date.fromisoformat(start), day, TODAY):
                label = f"Monthly membership - {MONTHS[d.month - 1]} {d.year}"
                if (mid, str(d)) in failed:
                    p(mid, d, price, "membership", "failed", label + " (direct debit declined)")
                else:
                    p(mid, d, price, "membership", "paid", label)

    # M1001 Sam: charged twice on 14 November, nothing refunded yet.
    p("M1001", "2026-11-14", 99, "membership", "paid", "Monthly membership - November 2026")
    # M1002 Priya: failed 3 Nov, updated card 4 Nov, retry paid 6 Nov with the fee. No waiver this year.
    p("M1002", "2026-11-06", 99, "membership", "paid", "Monthly membership - November 2026 (retry)")
    p("M1002", "2026-11-06", 10, "fee", "paid", "Failed payment fee")
    # M1003 Tom: same, but a fee was already waived in June.
    p("M1003", "2026-06-12", 99, "membership", "paid", "Monthly membership - June 2026 (retry)")
    p("M1003", "2026-06-12", 10, "fee", "refunded", "Failed payment fee (waived)")
    p("M1003", "2026-11-12", 99, "membership", "paid", "Monthly membership - November 2026 (retry)")
    p("M1003", "2026-11-12", 10, "fee", "paid", "Failed payment fee")
    # M1018 Ruby: paid for the lead course that Ridgeline cancelled.
    ruby = p("M1018", "2026-11-10", 150, "class", "paid", "Lead Climbing course (member price)")
    # M1019 Henry: paid for Learn to Belay, cancelled 14.5 hours before.
    henry = p("M1019", "2026-11-20", 40, "class", "paid", "Learn to Belay (member price)")
    # M1020 Isla: failed 15 Nov, fee added, retry on 18 Nov also failed -> suspended.
    p("M1020", "2026-11-15", 10, "fee", "unpaid", "Failed payment fee")
    p("M1020", "2026-11-18", 99, "membership", "failed", "Monthly membership - November 2026 (retry declined)")
    # M1023 Max: charged twice on 14 November, duplicate already refunded on 18 November.
    dup = p("M1023", "2026-11-14", 99, "membership", "refunded", "Monthly membership - November 2026")
    p("M1023", "2026-11-18", -99, "refund", "paid", "Refund of duplicate charge", dup)
    db.executemany("INSERT INTO payments VALUES (?,?,?,?,?,?,?,?)", pay)

    db.executemany("INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?)", [
        ("B501", "M1018", "Lead Climbing course", "2026-11-22 10:00", 150, "cancelled_by_ridgeline", "2026-11-20 16:00", ruby),
        ("B502", "M1019", "Learn to Belay", "2026-11-26 09:00", 40, "cancelled_by_member", "2026-11-25 18:30", henry),
        ("B503", "M1012", "Intro to Bouldering", "2026-03-01 18:00", 0, "attended", None, None),
    ])
    db.executemany("INSERT INTO freezes VALUES (?,?,?,?,?,?)", [
        ("F301", "M1008", "2026-04-01", "2026-05-31", 0, "completed"),
    ])
    db.executemany("INSERT INTO checkins VALUES (?,?)", [
        ("M1004", "2026-11-23 18:12"),
        ("M1005", "2026-11-20 17:40"), ("M1005", "2026-11-22 10:05"), ("M1005", "2026-11-24 19:30"),
        ("M1012", "2026-11-25 18:45"), ("M1013", "2026-11-21 11:20"),
        ("M1014", "2026-11-25 07:10"), ("M1015", "2026-11-24 06:55"), ("M1015", "2026-11-19 06:50"),
        ("M1017", "2026-11-01 16:30"), ("M1022", "2026-11-23 12:00"),
    ])
    db.executemany("INSERT INTO history VALUES (?,?,?,?)", [
        ("M1002", "2026-11-04", "payment_details_updated", "New Visa card added in the app"),
        ("M1003", "2026-06-10", "payment_details_updated", "New Mastercard added in the app"),
        ("M1003", "2026-06-12", "fee_waived", "Failed payment fee of $10 waived (card had expired)"),
        ("M1003", "2026-11-10", "payment_details_updated", "Bank account updated in the app"),
        ("M1020", "2026-11-18", "suspended", "Suspended after second failed direct debit"),
        ("M1023", "2026-11-18", "refund_issued", "Duplicate November charge refunded"),
    ])
    db.commit()
    db.close()
    return path


if __name__ == "__main__":
    print(build())
