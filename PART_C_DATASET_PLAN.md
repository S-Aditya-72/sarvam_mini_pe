# Part C — Dataset design and reproducible pipeline

## Proposed 200-hour ceiling (plan, not collected data)
- **100 h licensed real speech:** only corpus subsets whose exact licence explicitly permits redistribution and sharing with Sarvam; candidate discovery source: IndicVoices. Do not include a subset until licence/version and redistribution permission are archived.
- **50 h consented recordings:** volunteers, one speaker per clip, varied districts/accent, device, speaking rate, room and phone-like bandwidth; obtain consent and a reuse statement.
- **50 h synthetic Hindi:** generated from human-reviewed prompts covering everyday transactions, meetings, interviews, software work, service requests and code-mixed speech; log model/voice/version and every generated file as a distinct hour contribution.

This is a budget, not a claim that 200 hours have already been collected. Use clips ≤60 seconds; de-duplicate overlapping real source intervals. Split by speaker/source into 80/10/10 train/dev/test before generating derived records. Keep test speakers and templates out of training. A realistic initial pilot is 6–10 hours; expand only after the annotation audit passes.

## Annotation pipeline
1. Freeze source and licence metadata; compute SHA-256; record consent/licence and source interval.
2. Convert to mono PCM16 24 kHz WAV; reject clipping, empty/too-short audio, multiple speakers and >60 s clips.
3. Draft verbatim transcript following the problem’s IndicVoices Level 1 rules; keep fillers, repetitions, English code-switches and self-corrections; spell English words in Devanagari as spoken; numbers written as words.
4. Human-correct the transcript while replaying audio; maintain a correction log. Do not infer words from the intended script when the recording differs.
5. Produce word-level Hindi start/end times with a forced aligner or manual tool; human-check at least 30 boundaries in the audit sample and record corrected times/errors.
6. Create literal and fluent sentence-level English translations; preserve speaker intent, negation, conditionals, final corrected amounts, and lakh/crore units.
7. Run entity/intent validators for people, organisations, phone/account numbers, dates, amounts, negation and corrections. Human adjudication overrides automatic checks.
8. After the mid-term, synthesize target English only using Bulbul v3, voice `shubh`, `en-IN`, 24 kHz; archive exact settings and output. Align English words independently and validate missing/repeated TTS words.
9. Emit manifest JSONL and run schema checks: all source fields present; timings ordered, non-negative and within duration; stable IDs; audio and manifest checksums; byte-identical rebuild where possible.

## Data quality and failure modes
- **Code-switch normalization:** inconsistent spellings can fragment supervision; keep canonical transliteration rules.
- **Numbers/entities:** speech recognition can normalize or collapse digits; compare against a structured entity ledger.
- **Self-correction:** preserve both spoken abandoned and corrected values in transcript, but translation target should reflect final intended value.
- **Alignment drift:** pauses and disfluencies shift boundaries; estimate-only timestamps are not acceptable as final verified alignments.
- **Speaker leakage:** split by speaker and source, not random clips.
- **Synthetic bias:** TTS may overrepresent clean, formal voices; reserve real spontaneous/noisy speech for evaluation.
- **Licence/consent:** public availability is not proof of redistribution permission.
- **Final inference rule:** the submitted checkpoint itself must translate; no external ASR/MT/LLM/TTS cascade at inference.

## Pipeline
`licensed/consented sources → audio QC + de-duplication → verbatim transcript → human correction → word alignment + 30-boundary audit → literal/fluent English + entity ledger → manifest/schema validator → immutable dataset version`

## Open questions
1. Which Hindi-English code-switch patterns produce the largest intent loss in the target checkpoint?
2. Does entity-risk buffering help enough to justify its latency cost?
3. Which accent/noise slices are underrepresented after the first 10-hour pilot?
