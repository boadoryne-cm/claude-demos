"""The Ridgeline staff agent: works one hand-off ticket with tools, then proposes
actions and a draft reply for a staff member to approve.

    python -m staff_agent.agent T01          # run one ticket from tickets.jsonl

Claude decides which look-ups to make. Everything that would change an account is
only a proposal: tools.py checks it and queues it, and nothing changes until a
person approves it.
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import anthropic

from common.claude import FALLBACK_BETA, CallFailed, client, cost_of
from member_assistant.assistant import DOCS as MEMBER_DOCS
from staff_agent.data import DB_PATH, TODAY, build
from staff_agent.tools import TOOL_DEFS, Session

HERE = Path(__file__).resolve().parent
MODEL = "claude-opus-5-5"
EFFORT = "medium"
MAX_TURNS = 14

DOCS = {**MEMBER_DOCS, **{p.name[:8]: p.read_text().strip() for p in sorted((HERE / "docs").glob("STAFF-*.md"))}}

FINAL_SCHEMA = {
    "type": "object",
    "properties": {
        "member_id": {"type": "string", "description": "The member the ticket is about, or empty if none was found."},
        "sender_verified": {"type": "boolean", "description": "True if the sender may see and change this account under STAFF-01."},
        "summary": {"type": "string", "description": "Two or three sentences for the staff member: what happened and what you propose."},
        "policy_basis": {
            "type": "array",
            "items": {"type": "object", "properties": {
                "doc_id": {"type": "string", "enum": sorted(DOCS)},
                "quote": {"type": "string", "description": "Exact words copied from that document."}},
                "required": ["doc_id", "quote"], "additionalProperties": False},
        },
        "draft_reply": {"type": "string", "description": "The reply to the member, ready for staff to review."},
    },
    "required": ["member_id", "sender_verified", "summary", "policy_basis", "draft_reply"],
    "additionalProperties": False,
}


def build_system(version: str) -> str:
    instructions = (HERE / "prompts" / f"{version}.md").read_text().strip()
    docs = "\n\n".join(f'<document id="{i}">\n{t}\n</document>' for i, t in DOCS.items())
    return f"{instructions}\n\nToday is {TODAY:%A %d %B %Y} ({TODAY.isoformat()}).\n\n<policies>\n{docs}\n</policies>"


def ticket_text(t: dict) -> str:
    return (f"<ticket>\nTicket: {t['id']}\nFrom: {t['from']}\nReceived: {t['received']}\n"
            f"Attachments: {', '.join(t.get('attachments') or []) or 'none'}\n"
            f"Note from the help assistant: {t['assistant_note']}\nMessage:\n{t['message']}\n</ticket>")


@dataclass
class Run:
    final: dict | None
    actions: list[dict]
    steps: list[dict]
    usage: dict
    cost_usd: float
    seconds: float
    turns: int
    models: list[str]
    fallback_used: bool = False
    error: str | None = None
    extra: dict = field(default_factory=dict)


def _block_dict(b) -> dict:
    return b.model_dump(exclude_none=True) if hasattr(b, "model_dump") else dict(b)


def run_ticket(ticket: dict, version: str = "v1", db_path: Path = DB_PATH, on_step=None) -> Run:
    if not Path(db_path).exists():
        build(db_path)
    session = Session(db_path)
    system = [{"type": "text", "text": build_system(version), "cache_control": {"type": "ephemeral"}}]
    messages: list[dict] = [{"role": "user", "content": ticket_text(ticket)}]
    steps, usage_total, cost, models, fallback = [], {}, 0.0, [], False
    started = time.monotonic()
    turns = 0
    try:
        while True:
            turns += 1
            if turns > MAX_TURNS:
                raise CallFailed("too_many_turns", f"stopped after {MAX_TURNS} turns")
            try:
                resp = client().beta.messages.create(
                    model=MODEL, max_tokens=16000, betas=[FALLBACK_BETA], fallbacks="default",
                    system=system, tools=TOOL_DEFS, messages=messages,
                    thinking={"type": "adaptive"},
                    output_config={"effort": EFFORT, "format": {"type": "json_schema", "schema": FINAL_SCHEMA}},
                )
            except anthropic.APIStatusError as e:
                raise CallFailed("api_error", f"{e.status_code} {e.message}")
            except anthropic.APIConnectionError as e:
                raise CallFailed("api_error", f"connection: {e}")
            u = resp.usage
            usage = {"input_tokens": u.input_tokens or 0, "output_tokens": u.output_tokens or 0,
                     "cache_creation_input_tokens": getattr(u, "cache_creation_input_tokens", 0) or 0,
                     "cache_read_input_tokens": getattr(u, "cache_read_input_tokens", 0) or 0}
            for k, v in usage.items():
                usage_total[k] = usage_total.get(k, 0) + v
            cost += cost_of(resp.model, usage)
            models.append(resp.model)
            fallback = fallback or any(getattr(b, "type", "") == "fallback" for b in resp.content)

            if resp.stop_reason == "refusal":
                raise CallFailed("refusal", "Claude declined this ticket")
            if resp.stop_reason == "max_tokens":
                raise CallFailed("truncated", "hit max_tokens")
            messages.append({"role": "assistant", "content": [_block_dict(b) for b in resp.content]})
            if resp.stop_reason == "pause_turn":
                continue

            calls = [b for b in resp.content if b.type == "tool_use"]
            if not calls:  # finished: the last text block is the structured answer
                text = next((b.text for b in reversed(resp.content) if b.type == "text"), "")
                try:
                    final = json.loads(text)
                except json.JSONDecodeError as e:
                    raise CallFailed("bad_json", str(e))
                return Run(final, session.queue, steps, usage_total, cost, time.monotonic() - started, turns, models, fallback)

            results = []
            for b in calls:
                out, is_error = session.call(b.name, b.input)
                step = {"tool": b.name, "input": b.input, "result": json.loads(out), "is_error": is_error}
                steps.append(step)
                if on_step:
                    on_step(step)
                results.append({"type": "tool_result", "tool_use_id": b.id, "content": out, "is_error": is_error})
            # Cache the conversation so far: move the single moving breakpoint to the newest block.
            for m in messages:
                if m["role"] == "user" and isinstance(m["content"], list):
                    for blk in m["content"]:
                        blk.pop("cache_control", None)
            results[-1]["cache_control"] = {"type": "ephemeral"}
            messages.append({"role": "user", "content": results})
    except CallFailed as e:
        return Run(None, session.queue, steps, usage_total, cost, time.monotonic() - started, turns, models, fallback,
                   error=f"{e.kind}: {e.detail}")
    finally:
        session.close()


def load_tickets() -> dict[str, dict]:
    return {t["id"]: t for t in map(json.loads, (HERE / "tickets.jsonl").read_text().splitlines())}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("ticket")
    ap.add_argument("--prompt", default="v1")
    a = ap.parse_args()
    t = load_tickets()[a.ticket]
    run = run_ticket(t, a.prompt, on_step=lambda s: print(f"  {s['tool']}({json.dumps(s['input'])}){' ERROR' if s['is_error'] else ''}"))
    print(json.dumps({"final": run.final, "actions": run.actions, "error": run.error}, indent=2, ensure_ascii=False))
    print(f"\n[{run.turns} turns, {len(run.steps)} tool calls, ${run.cost_usd:.4f}, {run.seconds:.1f}s, {sorted(set(run.models))}]")


if __name__ == "__main__":
    main()
