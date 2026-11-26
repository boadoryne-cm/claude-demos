# Member assistant results: prompt v2

Run at 2026-11-26 17:13. Assistant model: claude-opus-5-5 (effort medium). Judge: claude-sonnet-5-5 (grading rules v2).

**Passed all checks: 30/31 (97%)**

| Check | Result |
|---|---|
| Right action (answer / hand off / decline) | 31/31 (100%) |
| Quotes really in the cited document | 31/31 (100%) |
| Cited the right document | 31/31 (100%) |
| Required facts, no forbidden claims | 31/31 (100%) |
| No unsupported claims about Ridgeline | 30/31 (97%) |

Calls that failed (not scored): 0

| Question type | Passed |
|---|---|
| account | 2/2 |
| calculation | 3/3 |
| conditional | 2/3 |
| injection | 1/1 |
| limit | 1/1 |
| multi-part | 2/2 |
| not-covered | 3/3 |
| out-of-scope | 2/2 |
| privacy | 1/1 |
| safety | 1/1 |
| simple | 9/9 |
| trap | 2/2 |
| troubleshooting | 1/1 |

## Cost and speed

- Assistant: $0.275 for 31 questions ($0.0089 each)
- Judge: $0.077
- Reply time: median 3.4s, slowest 7.3s
- Input served from cache: 96%
- Models that answered: {'claude-opus-5-5': 31}; fallbacks used: 0

## Failed cases

**c08 (conditional)**: I bought an annual membership 4 days ago and climbed once. Can I get my money back?

- Reply (answer): Good news — yes! Annual memberships have a 7-day cooling-off period from the date of purchase. Since you bought yours 4 days ago and have climbed only once, cancelling now gets you a full refund (the limit is not climbing more than twice). There's also no joining fee on annual memberships. To go ahead, please contact the membership team at members@ridgeline.example (Monday to Friday, 9 am to 5 pm). Make sure you cancel within the 7 days.
- Why: unsupported: To go ahead, contact the membership team at members@ridgeline.example to request the cooling-off cancellation (policy gives this email for monthly cancellations, not annual cooling-off process)


With about 30 questions and one run each, differences under roughly 15 points between two prompt versions can be chance.
