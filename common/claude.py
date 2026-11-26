"""One place for every Claude call in these demos.

- Reads ANTHROPIC_API_KEY from the environment or from ../.env (never printed).
- Asks for JSON that matches a schema (structured outputs), so parsing never guesses.
- Turns on server-side refusal fallbacks, as recommended for Claude Opus 5.5.
- Records tokens, cost, latency, stop reason and the model that actually answered.
- Raises CallFailed for anything that is not a usable answer (refusal, cut off,
  API error), so evaluations can keep plumbing failures apart from wrong answers.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

import anthropic

ROOT = Path(__file__).resolve().parent.parent

# USD per million tokens: input, output, cache write (5 min), cache read.
PRICES = {
    "claude-opus-5-5": (4.00, 20.00, 5.00, 0.20),
    "claude-sonnet-5-5": (2.00, 10.00, 2.50, 0.10),
    "claude-haiku-5-5": (0.10, 0.50, 0.125, 0.01),
}
FALLBACK_BETA = "server-side-fallback-2026-07-01"


def load_env() -> None:
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class CallFailed(Exception):
    """The call produced no usable answer. kind: refusal | truncated | api_error | bad_json"""

    def __init__(self, kind: str, detail: str, usage: dict | None = None):
        super().__init__(f"{kind}: {detail}")
        self.kind, self.detail, self.usage = kind, detail, usage or {}


@dataclass
class Result:
    data: dict
    model_asked: str
    model_served: str
    stop_reason: str
    usage: dict
    cost_usd: float
    seconds: float
    request_id: str | None = None
    fallback_used: bool = False
    extra: dict = field(default_factory=dict)


def cost_of(model: str, usage: dict) -> float:
    p = PRICES.get(model)
    if not p:
        return 0.0
    return (
        usage.get("input_tokens", 0) * p[0]
        + usage.get("output_tokens", 0) * p[1]
        + usage.get("cache_creation_input_tokens", 0) * p[2]
        + usage.get("cache_read_input_tokens", 0) * p[3]
    ) / 1_000_000


_client = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        load_env()
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit(
                "No Claude API key found. Copy .env.example to .env and put your key in it, "
                "or run with --fake to test without calling Claude."
            )
        _client = anthropic.Anthropic(max_retries=4, timeout=300)
    return _client


def call_json(*, model: str, system: str, user: str, schema: dict, effort: str = "medium",
              max_tokens: int = 16000, cache_system: bool = True) -> Result:
    """Send one request and return the parsed JSON answer."""
    system_blocks = [{"type": "text", "text": system}]
    if cache_system:
        system_blocks[0]["cache_control"] = {"type": "ephemeral"}
    started = time.monotonic()
    try:
        resp = client().beta.messages.create(
            model=model,
            max_tokens=max_tokens,
            betas=[FALLBACK_BETA],
            fallbacks="default",
            system=system_blocks,
            messages=[{"role": "user", "content": user}],
            output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
        )
    except anthropic.BadRequestError as e:
        raise CallFailed("api_error", f"400 {e.message}")
    except anthropic.AuthenticationError:
        raise SystemExit("Claude rejected the API key. Check the key in .env.")
    except anthropic.RateLimitError as e:
        raise CallFailed("api_error", f"rate limited after retries: {e.message}")
    except anthropic.APIStatusError as e:
        raise CallFailed("api_error", f"{e.status_code} {e.message}")
    except anthropic.APIConnectionError as e:
        raise CallFailed("api_error", f"connection: {e}")
    seconds = time.monotonic() - started

    u = resp.usage
    usage = {
        "input_tokens": u.input_tokens or 0,
        "output_tokens": u.output_tokens or 0,
        "cache_creation_input_tokens": getattr(u, "cache_creation_input_tokens", 0) or 0,
        "cache_read_input_tokens": getattr(u, "cache_read_input_tokens", 0) or 0,
    }
    fallback_used = any(getattr(b, "type", "") == "fallback" for b in resp.content) or any(
        getattr(it, "type", "") == "fallback_message" for it in (getattr(u, "iterations", None) or [])
    )
    cost = cost_of(resp.model, usage)

    if resp.stop_reason == "refusal":
        cat = getattr(getattr(resp, "stop_details", None), "category", None)
        raise CallFailed("refusal", f"category={cat}", usage)
    if resp.stop_reason == "max_tokens":
        raise CallFailed("truncated", f"hit max_tokens={max_tokens}", usage)
    text = next((b.text for b in resp.content if getattr(b, "type", "") == "text"), "")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise CallFailed("bad_json", str(e), usage)
    return Result(data, model, resp.model, resp.stop_reason, usage, cost, seconds,
                  getattr(resp, "_request_id", None), fallback_used)


def fake_result(data: dict, model: str = "fake") -> Result:
    """A stand-in answer for offline tests. Costs nothing and calls nothing."""
    return Result(data, model, model, "end_turn", {}, 0.0, 0.0)
