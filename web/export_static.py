"""Build a static replay of the demo page from the saved tested runs.

    python -m web.export_static [output_dir]     # default: web/static

The result is plain files (index.html + case-study PDFs) that any static host can serve.
It never calls Claude and holds no API key: every answer is one recorded in results/.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from web import server

HERE = Path(__file__).resolve().parent


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "static"
    (out / "case-studies").mkdir(parents=True, exist_ok=True)
    init = server.api_init()
    init["samples"] = [s for s in init["samples"] if s["saved"]]
    answers = {s["q"]: server.api_ask({"question": s["q"], "saved": True}) for s in init["samples"]}
    leases = {lid: server.api_extract({"lease": lid, "saved": True}) for lid in init["leases"]}
    data = json.dumps({"init": init, "answers": answers, "leases": leases}, ensure_ascii=False).replace("</", "<\\/")
    html = (HERE / "index.html").read_text().replace("<script>\n", f"<script>window.STATIC = {data};</script>\n<script>\n", 1)
    (out / "index.html").write_text(html)
    for pdf in (server.ROOT / "case-studies").glob("*.pdf"):
        shutil.copy(pdf, out / "case-studies" / pdf.name)
    print(f"Wrote {out / 'index.html'} ({len(html) // 1024} KB) and {len(list((out / 'case-studies').glob('*.pdf')))} PDFs")


if __name__ == "__main__":
    main()
