# Case study: a back-office agent that proposes, and a person approves

**Built with:** Claude Opus 5.5 (API) with tool use, strict tool schemas, structured final output, prompt caching, Python and SQLite; Claude Sonnet 5.5 as a separate grader. Built with Claude Code: I set the requirements, the procedures and the tests and reviewed the results; Claude Code wrote most of the code.
**Data:** the same fictional climbing gym (Ridgeline) with 23 fictional members, their payments, bookings, freezes and check-ins. No real customer data.

## The problem
The member help assistant hands account questions to staff: refunds, failed-payment fees, freezes, cancellations, injuries. Each one means opening the account, checking several records against the policies, and writing a careful reply. An agent can do the legwork, but it must never change an account on its own or act on instructions hidden in a member's email.

## What I built
- An agent that works one hand-off ticket. It chooses its own look-ups from 7 read-only tools (find member, profile, payments, bookings, freezes, check-ins, account notes). The database is opened read-only.
- 7 proposal tools (refund, fee waiver, freeze, cancellation, email change, incident report, escalate). Code checks every proposal: the payment belongs to the member, the refund isn't more than was paid, the dates and freeze length are valid. Valid proposals are queued; **nothing changes until a staff member clicks Approve**. Approval re-checks the account, so the same refund can't go through twice.
- Its output for staff: the member, whether the sender is allowed to see the account, a short summary, a draft reply, and word-for-word quotes from the policies it relied on.
- **22 test tickets**, each with traps: a charge already refunded, a fee already waived this year, a freeze over the yearly limit, a request from the wrong email address, a parent cancelling a child's membership, an injury reported late with a question about costs, and a message pretending to be a manager's approval.

## How each run is checked
Code checks the member, the identity decision, the proposed actions (exact amounts and dates), that every quote is in the cited policy, and that no private detail leaked. A separate model checks the reply against the account records and the proposed actions. A simulated perfect agent scores 22/22; a blank one 0/22. Re-grading the same replies twice gave 5 and 6 of 22 for version 1, and 15 and 15 for version 2. Every change to the grader is logged, and the grader was not changed after seeing version 2's results.

## Results (same grader for both versions)

| | Version 1 | Version 2 |
|---|---|---|
| Right member and identity decision | 22 of 22 | 22 of 22 |
| Right actions proposed | 21 of 22 | 22 of 22 |
| Quotes found, no private details leaked | 22 of 22 | 22 of 22 |
| Draft reply correct and supported | 5 to 6 of 22 | 15 of 22 |

- **Version 1** got the decisions right but padded the replies with things nobody had said: refund timings, confirmation emails, and "please see a doctor" right after saying it couldn't give medical advice. In one ticket it proposed a freeze the member hadn't asked for.
- **Version 2** adds five general rules from that review: only state what the policies and records say, describe only what's proposed, offer options instead of choosing for the member, no medical advice, cite the right document.
- **Remaining failures:** I reviewed all 7. Five are real (for example, "We've put through a refund" when the refund was still waiting for approval and a manager's sign-off), and two look like grader mistakes.
- **Cost and speed:** about 4 US cents per ticket, median 4 tool calls and 13 seconds; 93% of input tokens came from the prompt cache.

## Limits
- One run per version on 22 tickets, so treat the numbers as indicative.
- The draft reply still needs a person to read it. That is the design: staff approve every action and edit the reply before it's sent.
- Fictional gym, policies and members. Single tickets, not ongoing email threads.
