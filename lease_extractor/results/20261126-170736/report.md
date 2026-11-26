# Lease extraction results

Run at 2026-11-26 17:07. Model: claude-opus-5-5 (effort high). 1 leases, 17 fields each.

**Fields correct: 17/17 (100%)**

- Wrong values flagged for review by the checks: 0/0
- Wrong values that slipped through unflagged: 0
- Correct values flagged anyway (extra review work): 1
- Deliberate conflicts flagged: 2/2
- Calls that failed (not scored): 0

| Field | Correct |
|---|---|
| landlord | 1/1 |
| tenant | 1/1 |
| premises | 1/1 |
| permitted_use | 1/1 |
| commencement_date | 1/1 |
| term_months | 1/1 |
| expiry_date | 1/1 |
| annual_rent | 1/1 |
| rent_review_type | 1/1 |
| fixed_review_percent | 1/1 |
| number_of_options | 1/1 |
| option_term_months | 1/1 |
| security_type | 1/1 |
| security_amount | 1/1 |
| outgoings_percent | 1/1 |
| break_clause | 1/1 |
| break_notice_months | 1/1 |

| Lease | Correct | Flags raised |
|---|---|---|
| L07-ironbark-strength.md | 17/17 | 5 |

## Correct values that were flagged

- L07 option_term_months = `60`: check: Claude: Option exercise notice is at least 3 months before the end of the term. The exercise deadline depends on the correct expiry date, which is in conflict (see the term/expiry issue).

## Cost and speed

- $0.039 total, $0.039 per lease
- 13s per lease on average
- Models that answered: ['claude-opus-5-5']; fallbacks used: 0

Labels were written together with the fictional leases. Eight leases is a small sample, so treat percentages as indicative.
