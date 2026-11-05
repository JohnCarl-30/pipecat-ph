"""Transcribe recordings/NN.webm with every engine that has a key, caching to results/<engine>/NN.txt.

uv run --group spike --env-file .env spike/transcribe.py [engine ...]
"""

import os
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
CLIPS = ROOT / "recordings"
RESULTS = Path(__file__).resolve().parent / "results"


def deepgram(clip: Path, key: str) -> str:
    r = httpx.post(
        "https://api.deepgram.com/v1/listen",
        params={"model": "nova-3", "language": "tl", "smart_format": "true"},
        headers={"Authorization": f"Token {key}", "Content-Type": "audio/webm"},
        content=clip.read_bytes(),
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["results"]["channels"][0]["alternatives"][0]["transcript"]


def elevenlabs(clip: Path, key: str) -> str:
    r = httpx.post(
        "https://api.elevenlabs.io/v1/speech-to-text",
        headers={"xi-api-key": key},
        data={"model_id": "scribe_v2", "language_code": "fil"},
        files={"file": (clip.name, clip.read_bytes(), "audio/webm")},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["text"]


def assemblyai(clip: Path, key: str) -> str:
    api = httpx.Client(base_url="https://api.assemblyai.com/v2", headers={"authorization": key}, timeout=120)
    upload = api.post("/upload", content=clip.read_bytes()).raise_for_status().json()["upload_url"]
    # Tagalog is only on universal-2 per AssemblyAI's supported-languages page.
    job = api.post(
        "/transcript", json={"audio_url": upload, "speech_models": ["universal-2"], "language_code": "tl"}
    ).raise_for_status().json()
    while job["status"] not in ("completed", "error"):
        time.sleep(2)
        job = api.get(f"/transcript/{job['id']}").raise_for_status().json()
    if job["status"] == "error":
        raise RuntimeError(job.get("error"))
    return job["text"] or ""


def whisper(clip: Path, _key: str) -> str:
    import mlx_whisper  # uv run --group whisper; Apple Silicon only, runs locally for free

    return mlx_whisper.transcribe(str(clip), path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="tl")["text"]


ENGINES = {
    "deepgram": (deepgram, "DEEPGRAM_API_KEY"),
    "elevenlabs": (elevenlabs, "ELEVENLABS_API_KEY"),
    "assemblyai": (assemblyai, "ASSEMBLYAI_API_KEY"),
    "whisper": (whisper, None),
}


def main(names: list[str]) -> None:
    clips = sorted(CLIPS.glob("[0-9][0-9].webm"))
    if not clips:
        sys.exit(f"No clips in {CLIPS}. Record them with spike/record.html first.")
    for name in names or ENGINES:
        fn, env = ENGINES[name]
        key = os.environ.get(env, "") if env else ""
        if env and not key:
            print(f"{name}: skipped, {env} not set")
            continue
        out = RESULTS / name
        out.mkdir(parents=True, exist_ok=True)
        for clip in clips:
            dest = out / f"{clip.stem}.txt"
            if dest.exists():
                continue
            started = time.monotonic()
            try:
                dest.write_text(fn(clip, key).strip() + "\n")
            except Exception as e:  # one engine failing on one clip shouldn't stop the run
                print(f"{name} {clip.stem}: {e}")
                continue
            print(f"{name} {clip.stem}: {time.monotonic() - started:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1:])
