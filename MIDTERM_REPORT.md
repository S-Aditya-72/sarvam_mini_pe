# Inter IIT Tech Meet 15.0 — Sarvam Mini PS
## Real-time Hindi-to-English speech-to-speech translation | Dev track submission report

### Summary
This submission package documents the streaming interface prototype, research-led data design, six user-recorded clips and a reproducible annotation layout. The Dev server currently implements an echo protocol only; it is not a Hindi-to-English translator. The clips’ transcript and word times in this package are drafts based on the intended scripts and duration-weighted estimates, not verified against the waveforms. Those items must not be represented as fully audited.

### Part A — Problem and protocol
The target is live code-mixed Hindi speech to English speech. Word order, irreversible output, entities and self-corrections make the task harder than offline translation. KPIs are translation quality (12), intent accuracy (18), entity accuracy (18), latency (16) and audio naturalness (6). Final gates require a valid container, fine-tuning evidence and a valid frozen Part A dataset.

The server listens at `:8000/ws`; `GET /health` returns HTTP 200 on port 8000. It accepts `session_start`, 80 ms mono PCM16 24 kHz frames (3,840 bytes), and `input_end` with `valid_samples`. It must keep reading during output generation, finish within 30 seconds after input_end, emit output frames no longer than one second, send exactly one `session_complete`, and send nothing after it. The client never waits for the server. For amount corrections such as “पाँच लाख… नहीं नहीं, पाँच करोड़”, preserve the entire spoken sequence in the transcript but assert only the final intended amount in translation.

### Part B — Research synthesis
STACL motivates wait-k as a simple prefix-to-prefix baseline (Ma et al., 2019); information-transport policies model when additional source information is needed (Zhang & Feng, 2022). SimulEval offers a common server/client evaluation setup (Ma et al., 2020). AL alone can mislead when output length differs; LAAL is a useful companion (Papi et al., 2022). IndicVoices demonstrates the scale and diversity of Indian-language speech but each subset’s licence and domain must still be checked (Javed et al., 2024). MuST-C shows the value of aligned speech/transcript/translation data; FLEURS provides multilingual coverage but does not replace conversational code-mixed evaluation. SeamlessM4T, Whisper and XLS-R are useful research references for multilingual speech representation/translation, not allowed inference-time substitutes for the competition checkpoint.

**Proposed idea:** entity-risk buffering. Delay committing audio around names, amounts, negation and correction markers, while allowing low-risk clauses to stream. Test it against wait-k=2/3/4 on exact entity match, intent preservation and AL/LAAL. This is a hypothesis, not a measured result.

### Part C — Dataset plan
Proposed ceiling allocation (not claimed as already collected): 100 h licensed redistributable real speech, 50 h consented volunteer speech, 50 h synthetic Hindi with generation metadata. Start with a 6–10 h pilot; split by speaker/source (80/10/10) and ensure test speakers/templates do not leak into training. Pipeline: licence/consent and checksums → mono PCM16 24 kHz conversion → verbatim transcript → human correction → word alignment → literal/fluent translations → entity and schema validation → frozen JSONL manifest. Clips must be ≤60 seconds, source metadata complete and all times within audio duration. After mid-term, English supervised target audio must use Bulbul v3, `shubh`, `en-IN`, 24 kHz, with separately aligned English words. Final inference may not use an external ASR/MT/LLM/TTS cascade.

Failure modes include transcription normalization of code-switches, incorrect digits/amounts, loss of negation, treating an abandoned correction as final, alignment drift, synthetic speaker bias, speaker leakage and unverified redistribution licences.

### Part D — Six recordings
Six mono 24 kHz clips are included. The transcript and translation manifests contain drafts based on the intended recording scripts, not a verified acoustic transcription. Hindi word intervals are duration-weighted initial estimates; the boundary audit sheet has 30+ sample rows marked `PENDING_MANUAL_AUDIO_CHECK`. Do not claim those checks are completed. The reference entity ledger lists names, phone digits, amounts, dates, times, conditions and negations to verify. Model entity accuracy remains unevaluated because no translation output is connected.

### Part E — Dev track
Docker health and WebSocket echo tests were run from the user’s machine. The health endpoint returned `HTTP 200 OK`. Each run returned 382 input frames and 382 output frames, exactly one `session_complete`, and no observed messages after completion. First output was about 0.23 s. Realtime run wall time was 35.686 s; fast runs were about 30.72 s. These timings are echo-prototype measurements and must not be presented as translation latency. Backpressure is addressed by queuing input separately from output pacing, but disconnect/malformed-frame stress tests remain outstanding.

### Limitations and immediate blockers
1. The server echoes audio unchanged; no translation model or fine-tuning is included.
2. The six transcript drafts, translations and all estimated timestamps must be listened to and corrected. At least 30 boundaries must be genuinely hand-checked; the included audit is not complete.
3. No English Bulbul training pairs, fine-tuned weights, training logs or before/after scores are included.
4. Public-data licences/consent must be documented before any real corpus is redistributed.

This package is a reproducible prototype/research draft, not evidence that the full final-round model or all gates are satisfied.
