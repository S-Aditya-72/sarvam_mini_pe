# Part A — Problem understanding and streaming protocol

## Objective
Translate live, naturally code-mixed Hindi speech into English speech while the speaker is still talking. Output is irreversible, so the system must balance translation quality, intent/entity fidelity and latency. Hindi SOV order means the final verb can reverse the meaning of an earlier prefix; numbers, names, negation and self-corrections are high-risk.

## KPIs and gates
Translation quality 12; intent accuracy 18; entity accuracy 18; latency 16; audio naturalness 6. The three final gates are container/interface compliance, fine-tuning evidence (weights/logs/pair manifests and before/after scores), and a valid frozen Part A dataset. Failure of a gate zeros the 70 final KPI points. The report/presentation are graded separately.

## Protocol walkthrough
1. Accept WebSocket at `:8000/ws` and health check `GET /health` → HTTP 200 on port 8000.
2. Receive `session_start` JSON (`pcm_s16le`, mono 24 kHz, `hi`→`en`).
3. Receive binary input frames of 3,840 bytes = 80 ms, preserving order. Client never waits for server; server must read continuously and avoid blocking ingestion on output generation.
4. On `input_end`, use `valid_samples` to ignore zero padding, flush the model and finish within 30 seconds.
5. Emit only binary English PCM frames (≤1 second each), then exactly one `session_complete`. No server messages may follow.
6. One session per connection; accept within 10 seconds; keep up with incoming frames so no scheduled frame is delayed by more than one second.

## Correction example
For “पाँच लाख… नहीं नहीं, पाँच करोड़”, the transcript preserves both spoken values, but the translation should assert the final corrected value only. The system should delay committing a high-risk amount while correction cues are still plausible; it must never speak both values as alternatives if the speaker corrected themselves.

## Wait-k / AL convention
Use `g(i)=min(τ, k+i−1)` (standard wait-k convention) for target token i; this makes the first target token wait until k source tokens have arrived. State convention because some starter descriptions use `k+i`. Report AL with quality, and also LAAL because AL may be biased by output-length mismatch. For the illustrative appendix sentence “मैंने कल अपना पुराना बैंक खाता बंद करवा दिया” (9 source words), target “I got my old bank account closed yesterday” (8 target words), wait-3 schedule is `g=[3,4,5,6,7,8,9,9]`; using the convention in the prior draft gives AL ≈2.625 source-word units. Recompute with the exact evaluation implementation before final claims.

## Dev-track status
The container health check and echo protocol tests passed: 382 frames in and 382 out; one `session_complete`; no messages observed after completion. First output was ~0.23 s; wall time ~30.7–35.7 s depending on pacing. These are echo-prototype metrics only. No translation model, model latency, translation quality, or entity accuracy has been evaluated.
