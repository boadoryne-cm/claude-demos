# Member assistant results: prompt v2

Run at 2026-11-26 17:15. Assistant model: claude-opus-5-5 (effort medium). Judge: claude-sonnet-5-5 (grading rules v2).

**Passed all checks: 31/31 (100%)**

| Check | Result |
|---|---|
| Right action (answer / hand off / decline) | 31/31 (100%) |
| Quotes really in the cited document | 31/31 (100%) |
| Cited the right document | 31/31 (100%) |
| Required facts, no forbidden claims | 31/31 (100%) |
| No unsupported claims about Ridgeline | 31/31 (100%) |

Calls that failed (not scored): 0

| Question type | Passed |
|---|---|
| account | 2/2 |
| calculation | 3/3 |
| conditional | 3/3 |
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

- Assistant: $0.260 for 31 questions ($0.0084 each)
- Judge: $0.078
- Reply time: median 3.8s, slowest 7.9s
- Input served from cache: 99%
- Models that answered: {'claude-opus-5-5': 31}; fallbacks used: 0

With about 30 questions and one run each, differences under roughly 15 points between two prompt versions can be chance.
