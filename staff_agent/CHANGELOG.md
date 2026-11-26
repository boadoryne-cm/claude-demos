# Staff agent: changes to the test, logged so results stay comparable

## 2026-11-26: grader v2 and one expectation, after the first v1 run
- **Judge could not see the account.** Every account fact in a reply (dates, amounts, check-ins) was marked "unsupported", so 0/22 replies passed. The judge now receives the records the agent looked up. Also stopped counting direct consequences of a policy, record or proposed action as unsupported (the same rule the member assistant's grader adopted).
- **T14 expectation was too narrow.** Chloe asks about her husband's account. The agent treated the ticket as being about Daniel's account (M1015) and correctly marked her as not verified for it. Both readings are defensible, so either member is accepted, with the identity decision that matches it.
- The judge now also sees the date the ticket arrived and today's date.
- The v1 run's stored outputs were re-graded with these rules (`v1-...-regraded`). No agent output was changed.

## 2026-11-26: prompt v2
Written from the reviewed v1 failures (invented processes, unproposed promises, choosing for the member, medical advice, citing the wrong document). Each rule is general; none names a test ticket.

## 2026-11-26: grader v3, v2 results, approval fix
- **Judge v3:** the v2 judge sometimes listed statements as unsupported while calling them "largely supported" or "plausibly implied" in the same note (T02, T18). It now lists only what it judges unsupported. Checked by re-grading the same v1 outputs twice.
- **v2 prompt run (judge v3):** 15/22 passed every check, against 5–6/22 for v1 under the same judge. Actions 22/22 (v1: 21/22, T13 proposed a freeze nobody asked for). Re-grading the v2 outputs gave the same 15/22 and the same failing tickets. Manual review of the 7 failures: 5 are real (T03 fee timing, T09 promises to set up a freeze, T13 misreads the 7-day rule, T19 says the refund was already put through, T20 overstates POL-04) and 2 look like judge errors (T08, T14). The grader was not changed after seeing v2 results.
- **Approval re-checks (tools.apply):** approving the same refund twice recorded two refunds in the demo. `apply` now re-checks the payment and the new email at approval time and refuses if the account has changed; the demo server also removes a proposal once it is approved. Covered by `test_approval_rechecks_the_account`.
