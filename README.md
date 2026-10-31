# pipecat-ph

Pipecat plugins for Filipino (Taglish) voice agents.

**Status: planning.** Nothing here works yet. The first code lands only after the
spike below shows Taglish speech recognition is good enough to build on.

## What this will be

- A Taglish speech-to-text, LLM, text-to-speech pipeline on [Pipecat](https://github.com/pipecat-ai/pipecat).
- One phone transport that works from the Philippines today, using Pipecat's
  built-in Twilio Media Streams serializer.
- An adapter that sends transcripts to [relaydesk](https://github.com/JohnCarl-30/relaydesk)
  so calls become support tickets.
- A Langfuse eval set of Taglish calls with published accuracy numbers.
- A compliance README covering the SIM Registration Act, telco sender ID
  registration, and the Data Privacy Act.

## What this is not

Not an open-source Twilio for the Philippines. Numbers, carrier interconnect and
SMS routes cannot be open-sourced. You still buy those from Twilio or a local
aggregator. This repo is the software on top.

## Plan

1. **Spike.** Record 20 Taglish questions. Run them through Deepgram (Tagalog
   model) and ElevenLabs Scribe. Score word accuracy by hand. If neither clearly
   beats the browser `SpeechRecognition` API, stop here.
2. **Phone bot.** `uv add "pipecat-ai[websocket,deepgram,elevenlabs,openai]"`,
   follow the Pipecat phone-bot guide, answer one Twilio number.
3. **Relaydesk adapter.** Replace the LLM step with a processor that POSTs to
   relaydesk `/api/chat`, tagged `channel: phone`.
4. **Eval.** Turn the recordings plus four edge cases (misheard Taglish,
   interruption, no answer, asks for a human) into a Langfuse dataset and score
   each STT/TTS combination.
5. **Publish** results and the compliance notes.

## License

MIT
