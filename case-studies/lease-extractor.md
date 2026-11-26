# Case study: lease summaries with a checker

**Built with:** Claude Opus 5.5 (API), Python, structured outputs, rule-based checks. Built with Claude Code: I set the requirements and the tests and reviewed the results; Claude Code wrote most of the code.
**Data:** 8 fictional Australian commercial leases (retail, office, industrial, medical) and an answer key created for the test. No real leases.

## The problem
Property teams keep a lease register (tenant, expiry, rent, reviews, options, security, break rights). Reading each lease by hand is slow, and the risky parts hide in schedules, special conditions and later variations.

## What I built
- Claude reads the whole lease and fills 17 register fields. Every value comes with the clause it came from and a word-for-word quote, and Claude lists anything a person should check.
- Rule checks that need no answer key: each quote must exist in the lease, dates must match the term, rent must trace back to a figure in the lease, related settings must agree, and each value must appear in its own quote.
- Output as a CSV ready for Google Sheets, plus a review list of everything flagged.

Deliberate traps in the samples: a deed of variation that extends the term, rent stated only per month or per week, a rent-free period, a special condition that overrides the schedule rent, and a lease whose term and expiry date contradict each other.

## Results
- **136 of 136 fields correct** (8 leases × 17 fields), in two separate runs. The only difference between runs was the wording of one premises description.
- Every trap was handled: varied term and expiry used, monthly and weekly rent converted, the rent-free period ignored for base rent, the special-condition rent used. The contradictory term and expiry were flagged for review instead of being silently "fixed".
- **Claude raised useful points nobody asked for:** after the deed of variation, the bank guarantee may need extending to the new expiry date; and in another lease, the bank guarantee had been sized on the schedule rent rather than the lower rent that actually applies.
- **Cost and speed:** about 3.7 US cents and 11 seconds per lease.

## Testing the checker with planted mistakes
Because Claude got everything right, I tested the checks by planting one mistake at a time in its correct output (wrong rent, wrong dates, a made-up quote, swapped landlord and tenant, and so on).

| Checker version | Planted mistakes caught |
|---|---|
| First version | 46 of 74 |
| After adding "a value must appear in its own quote" | 70 of 74 |

The 4 misses were in places already flagged for review. The new rule added no false alarms; the only rule flags on correct values were intended (a calculated security amount and the deliberate conflict).

## What went wrong along the way
- The API rejected my first output format (17 separately typed fields) as too complex. I switched to one simple list of text values that the code converts and validates; conversion problems are flagged too.
- A blank test answer slipped past the first checker because empty values weren't flagged. I added a rule for required fields.

## Limits
- 8 leases, written together with their answer key, in clean text rather than scanned PDFs. A perfect score here means the set is too easy to separate one setup from another; harder and real-format documents are the next step.
- The checks catch inconsistencies, not every possible error. A person should still review the flagged items.
