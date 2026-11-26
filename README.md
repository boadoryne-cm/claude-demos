# Claude demos: help assistant, lease extractor and staff agent

Three small, tested demos of Claude doing real work, with the checks that show how well it does it.
Everything uses fictional data: a made-up climbing gym and made-up Australian commercial leases.

## 1. Member help assistant (`member_assistant/`)
A help assistant for a fictional gym's members. It answers only from 10 policy documents,
quotes the exact policy wording it relied on, hands account and payment questions to staff,
and declines off-topic requests.

- `docs/` the 10 policies. `prompts/v1.md` the assistant's instructions.
- `cases.jsonl` 31 test questions (written by `make_cases.py`): simple lookups, calculations,
  traps where the policies are silent, account requests, an injury, privacy, a prompt injection,
  and off-topic questions.
- `evaluate.py` runs every question and scores each reply five ways:
  right action, quotes really in the document, right document cited (all checked by code),
  required facts present, and no claims the policies don't support (checked by a separate
  Claude Sonnet 5.5 grader, so the model isn't grading itself).

## 2. Lease extractor (`lease_extractor/`)
Reads a lease and fills a lease register: parties, dates, rent, reviews, options, security,
outgoings and break rights. Every value comes with its clause and a word-for-word quote.

- `leases/` 8 fictional leases (written by `make_leases.py`) with deliberate traps:
  a deed of variation, rent stated per month or per week, a rent-free period, a special
  condition overriding the schedule, and a term that contradicts the expiry date.
- `checks.py` rule checks that need no answer key: quotes must exist in the lease,
  dates must match the term, rent must trace to a figure, settings must be consistent.
- `evaluate.py` scores against `labels.py` and reports how many wrong values the checks caught.
  It writes `register.csv` (import into Google Sheets) and `review_queue.csv`.

## 3. Staff back-office agent (`staff_agent/`)
Picks up the help assistant's hand-offs. Claude chooses its own look-ups in a fictional members
database, then proposes actions and drafts a reply. Nothing changes until a person approves it.

- `docs/STAFF-01-...md` the membership team's procedures (identity checks, which refunds staff can
  approve, fee waivers, freezes, injuries). `data.py` builds the SQLite database of 23 members.
- `tools.py` 7 read-only look-ups (the database is opened read-only) and 7 proposal tools. Code
  checks every proposal and queues it; `apply()` is the only thing that writes, re-checks the
  account at approval time, and is only called when a person approves.
- `tickets.jsonl` 22 hand-off tickets (written by `make_tickets.py`), each with the right member,
  identity decision, actions with exact amounts and dates, facts the reply must give, and leaks to avoid.
- `evaluate.py` scores six checks: member, identity decision, actions, quotes, no leaked details
  (code) and the reply against the account records (Claude Sonnet 5.5 grader).
  `--regrade DIR` re-scores stored outputs; `CHANGELOG.md` logs every change to the test.

## Demo page (`web/`)

A web page for showing all three demos: every answer appears next to the source document with the quoted words highlighted.

```
python -m web.server        # then open http://localhost:8000
```

- **Member help assistant:** type a question or pick a sample. "Ask Claude" makes a live call; "Show the answer from the tested run" replays a saved answer for free.
- **Lease register:** pick a sample lease. "Read this lease with Claude" runs it live (10-20 s); "Show the tested run" is free. Click any row to jump to the words it came from.
- **Staff agent:** pick a ticket. "Run the agent" works it live (15-40 s); "Show the tested run" is free. Click a step to see what the agent looked up; Approve applies the proposal to a demo copy of the database, rebuilt each time the server starts.
- Live calls are capped at 40 per server start (`DEMO_MAX_CALLS` to change). The top bar shows calls made and money spent.
- Shortcuts: `/#lease=L07&field=expiry_date` opens a lease's tested run on one field; `/#ask=2` shows the tested answer to sample question 2; `/#ticket=T08&step=2` opens a ticket's tested run on one step.
- In GitHub Codespaces, VS Code offers to open the forwarded port 8000 in the browser. The port stays private to your GitHub login unless you change it.

## Running it

```
# first time only, on a new computer:
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env        # then put your own Anthropic API key in .env (ignored by git)
                            # in Codespaces, add ANTHROPIC_API_KEY as a Codespaces secret instead

# offline tests, no cost:
.venv/bin/python -m pytest -q
.venv/bin/python -m member_assistant.evaluate --fake oracle
.venv/bin/python -m staff_agent.make_tickets && .venv/bin/python -m staff_agent.data   # tickets and database

# real runs:
.venv/bin/python -m member_assistant.evaluate --prompt v2 --limit 3   # quick check
.venv/bin/python -m member_assistant.evaluate --prompt v2             # all 31
.venv/bin/python -m member_assistant.compare                          # v1 vs v2 across saved runs
.venv/bin/python -m lease_extractor.evaluate                          # all 8 leases
.venv/bin/python -m staff_agent.evaluate --prompt v2                  # all 22 tickets
# one question or one lease:
.venv/bin/python -m member_assistant.assistant --prompt v2 "Can I freeze my membership?"
.venv/bin/python -m lease_extractor.extract lease_extractor/leases/L07-ironbark-strength.md
.venv/bin/python -m staff_agent.agent T08 --prompt v2
```

In Codespaces, leave out `.venv/bin/` and run `pip install -r requirements.txt` once.

Results land in each project's `results/` folder with a `report.md`.

Model: Claude Opus 5.5 for the assistant, the extractor and the agent, Claude Sonnet 5.5 as the grader.
Refusal fallbacks are turned on (`fallbacks: "default"`). Expected cost: under $1 for a full
assistant run, about 30 cents for all 8 leases, about $1 for all 22 agent tickets with grading.
