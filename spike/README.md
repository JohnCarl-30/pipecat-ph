# Spike: is Taglish speech recognition good enough?

Plan step 1. Twenty Taglish support questions, recorded once and sent through every engine:

| Engine | Setting | Cost |
| - | - | - |
| Chrome `SpeechRecognition` | `fil-PH`, captured while you record | free, the baseline |
| Deepgram | `nova-3`, `language=tl` | API credits |
| ElevenLabs Scribe | `scribe_v2`, `language_code=fil` | API credits |
| AssemblyAI | `universal-2`, `language_code=tl` (Tagalog is only on universal-2) | API credits |
| Whisper large-v3-turbo | `language=tl`, local through mlx-whisper | free, Apple Silicon |

If no paid engine clearly beats Chrome, stop here (see the main README).

## 1. Record (Chrome, about 10 minutes)

```sh
uv run python -m http.server 8765 -d spike
```

Open http://localhost:8765/record.html in Chrome and allow the microphone. Read each prompt the way you'd say it on a call, not slowly. Each Stop downloads `NN.webm`; the page also saves what Chrome heard. At the end, press **Download browser.json**, then:

```sh
mkdir -p recordings && mv ~/Downloads/[0-9][0-9].webm ~/Downloads/browser.json recordings/
```

`recordings/` is gitignored because it holds your voice.

## 2. Transcribe

Put the keys you have in `.env` (gitignored). Engines without a key are skipped.

```sh
uv run --group spike --env-file .env spike/transcribe.py              # every engine
uv run --group spike --group whisper spike/transcribe.py whisper      # local only, first run downloads ~1.6 GB
```

Results are cached in `spike/results/<engine>/NN.txt`, so a rerun only fills gaps. Delete a folder to redo that engine.

## 3. Score

```sh
cd spike && python3 score.py > results.md
```

`results.md` has word error rate per engine (pooled over words), every clip an engine got wrong, and the prompts. Read the misses by hand: the scorer counts "3 PM" vs "three PM" or "dyan" vs "diyan" as errors, and only you can say whether a miss would change what a support agent does.

Tests: `cd spike && python3 -m unittest test_wer`.
