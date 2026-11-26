# Case study: a member help assistant that cites its sources

**Built with:** Claude Opus 5.5 (API), Python, structured outputs, prompt caching, Claude Sonnet 5.5 as a separate grader. Built with Claude Code: I set the requirements and the tests and reviewed the results; Claude Code wrote most of the code.
**Data:** a fictional climbing gym (Ridgeline Climbing Co.) with 10 policy documents. No real customer data.

## The problem
A member-facing assistant is only useful if members can trust it. The usual failure is not a wrong price. It's the assistant inventing a helpful-sounding rule, exception or promise that the business never made.

## What I built
- An assistant that answers only from the policy documents, and for every answer returns the policy it used with a word-for-word quote.
- Three kinds of response: **answer**, **hand off** to the membership team (anything needing account access, a refund decision or an injury report), or **decline** (off-topic requests).
- A test suite of **31 questions**: simple lookups, price calculations, questions the policies don't cover, account and payment requests, an injury, a privacy request, a prompt-injection attempt and off-topic questions.
- Every reply is scored on five checks. Code checks the response type, checks that every quote really appears in the cited policy, and checks that the right policy was cited. A separate model checks that the required facts are present and that nothing is claimed that the policies don't support.

## How I made sure the test itself was right
- A simulated perfect assistant scores 100%; a blank one scores 0%.
- Re-grading the same replies twice gave identical results.
- In the first full run, 3 of the 7 failures were the grader being wrong (for example, counting "I've passed this to the membership team" as an invented claim). I fixed the grading rules, logged the change, and re-graded the stored replies, so both prompt versions are judged by the same rules.

## Results (3 full runs of each version)

| | Version 1 | Version 2 |
|---|---|---|
| Passed every check | 29, 26, 28 of 31 (avg 89%) | 30, 31, 31 of 31 (avg 99%) |
| Claims not supported by the policies | 10 across 3 runs | 1 across 3 runs |
| Required facts given | 100% | 100% |
| Quotes found in the cited policy | 100% | 100% |
| Hand-offs to staff per run | 6 to 7 | 6 to 7 |
| Average reply length | 78 words | 64 words |

- **What changed:** every version 1 failure was the assistant adding something extra the policies don't say, such as suggesting a late injury report or hinting that a family-account holder could ask about another member. Version 2 adds one instruction: only state what the policies say, and when a situation falls outside them, say so and point to the membership team.
- **What didn't get worse:** version 2 didn't avoid mistakes by handing off more, and it gave every required fact.
- **Cost and speed:** about 0.9 US cents per answer and a median reply time of 3 to 4 seconds. 99% of the input was served from the prompt cache.

## Limits
- 31 questions and 3 runs per version: the direction was the same in every run, but treat the percentages as indicative.
- The grader is strict on purpose. Even small extras like "just ask at the front desk" count as unsupported.
- Single questions only, not long conversations. The gym and its policies are fictional.
