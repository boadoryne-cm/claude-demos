"""Ridgeline member help assistant (fictional gym, demo only).

Usage:
    python -m member_assistant.assistant "How much is a casual visit?"
    python -m member_assistant.assistant --prompt v2 "Can I freeze my membership?"
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common.claude import call_json

HERE = Path(__file__).resolve().parent
MODEL = "claude-opus-5-5"
EFFORT = "medium"


def load_docs() -> dict[str, str]:
    """{'POL-01': text, ...} sorted by id so the cached prompt never changes order."""
    docs = {}
    for p in sorted((HERE / "docs").glob("POL-*.md")):
        docs[p.name[:6]] = p.read_text().strip()
    return docs


DOCS = load_docs()

SCHEMA = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": ["answer", "handoff", "decline"],
            "description": "answer: replied from the policies. handoff: passed to the membership team. decline: not something Ridgeline can help with.",
        },
        "reply": {"type": "string", "description": "The message shown to the member."},
        "sources": {
            "type": "array",
            "description": "Policy documents the reply relies on.",
            "items": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "enum": sorted(DOCS)},
                    "quote": {"type": "string", "description": "Exact words copied from that document."},
                },
                "required": ["doc_id", "quote"],
                "additionalProperties": False,
            },
        },
        "handoff_reason": {"type": "string", "description": "Why it was handed off. Empty if not handed off."},
    },
    "required": ["action", "reply", "sources", "handoff_reason"],
    "additionalProperties": False,
}


def build_system(prompt_version: str) -> str:
    instructions = (HERE / "prompts" / f"{prompt_version}.md").read_text().strip()
    docs = "\n\n".join(f'<document id="{i}">\n{t}\n</document>' for i, t in DOCS.items())
    return f"{instructions}\n\n<policies>\n{docs}\n</policies>"


def ask(question: str, prompt_version: str = "v1"):
    user = f"<member_message>\n{question}\n</member_message>"
    return call_json(model=MODEL, system=build_system(prompt_version), user=user,
                     schema=SCHEMA, effort=EFFORT, max_tokens=8000)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--prompt", default="v1")
    a = ap.parse_args()
    r = ask(a.question, a.prompt)
    print(json.dumps(r.data, indent=2, ensure_ascii=False))
    print(f"\n[{r.model_served}, {r.usage}, ${r.cost_usd:.4f}, {r.seconds:.1f}s]")


if __name__ == "__main__":
    main()
