"""Score every engine in results/ (plus Chrome's recordings/browser.json) against prompts.txt.

uv run spike/score.py > spike/results.md
"""

import json
from pathlib import Path

from wer import errors

HERE = Path(__file__).resolve().parent
BROWSER = HERE.parent / "recordings" / "browser.json"


def load() -> dict[str, dict[str, str]]:
    engines = {
        d.name: {f.stem: f.read_text().strip() for f in d.glob("*.txt")}
        for d in sorted((HERE / "results").glob("*"))
        if d.is_dir()
    }
    if BROWSER.exists():
        engines["browser"] = json.loads(BROWSER.read_text())
    return engines


def report(prompts: dict[str, str], engines: dict[str, dict[str, str]]) -> str:
    lines = ["| Engine | Clips | WER | Clips with 0 errors |", "| - | - | - | - |"]
    detail = []
    for name, got in engines.items():
        edits = words = perfect = 0
        for cid, ref in prompts.items():
            if cid not in got:
                continue
            e, n = errors(ref, got[cid])
            edits, words, perfect = edits + e, words + n, perfect + (e == 0)
            if e:
                detail.append(f"| {cid} | {name} | {e} | {got[cid]} |")
        clips = sum(cid in got for cid in prompts)
        # Pooled over words, not averaged per clip, so short clips don't dominate.
        rate = f"{edits / words:.1%}" if words else "—"
        lines.append(f"| {name} | {clips}/{len(prompts)} | {rate} | {perfect} |")
    misses = ["| Clip | Engine | Errors | Heard |", "| - | - | - | - |", *sorted(detail)]
    refs = [f"{cid}. {ref}" for cid, ref in prompts.items()]
    return "\n".join(["## Summary", "", *lines, "", "## Misses", "", *misses, "", "## Prompts", "", *refs, ""])


if __name__ == "__main__":
    texts = (HERE / "prompts.txt").read_text().splitlines()
    prompts = {f"{i:02d}": t for i, t in enumerate(texts, 1) if t}
    print(report(prompts, load()))
