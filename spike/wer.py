"""Word error rate for Taglish transcripts."""

import re


def normalize(text: str) -> list[str]:
    # Hyphens and apostrophes vary between engines ("mag-walk in", "magwalk in"), so join on them.
    text = re.sub(r"[-'’]", "", text.lower())
    return re.findall(r"\w+", text)


def errors(reference: str, hypothesis: str) -> tuple[int, int]:
    """Word-level edit distance and reference length."""
    ref, hyp = normalize(reference), normalize(hypothesis)
    row = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, row[0] = row[0], i
        for j, h in enumerate(hyp, 1):
            prev, row[j] = row[j], min(row[j] + 1, row[j - 1] + 1, prev + (r != h))
    return row[-1], len(ref)


def wer(reference: str, hypothesis: str) -> float:
    edits, n = errors(reference, hypothesis)
    return edits / n if n else float(edits > 0)
