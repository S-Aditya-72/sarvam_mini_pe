# Part B — Research notes (paper-grounded, compact)

## Q1. How should a streaming translator decide when to speak?
**Evidence.** STACL introduced prefix-to-prefix training and wait-k, which starts target generation after observing k source tokens; it offers a transparent latency/quality baseline (Ma et al., ACL 2019). Information-Transport-based Policy (Zhang & Feng, EMNLP 2022) instead learns read/write decisions around how source information changes target prediction. The IWSLT 2022 HW-TSC system shows wait-k can be used in SimulST, but uses synthetic translated training data and heuristic sentence breaking. These results are not direct proof for Hindi→English code-switching.
**Design choice.** Start with wait-3 as a reproducible baseline, then compare a risk-aware policy that waits longer around amounts, names, negation, and correction cues (“नहीं नहीं”, “मेरा मतलब”). Do not stream a provisional number as final when a correction is likely.
**Cheap experiment.** Replay the six clips at k=2,3,4 and with a correction-aware hold; measure first-output delay, AL/LAAL, and exact entity/intent preservation. The current echo server is only protocol-tested, so these model scores remain unmeasured.
**Open question.** Which correction cues can be detected robustly without causing excessive delay?
**Claim check.** A fixed wait-k is a useful baseline, not a guarantee of optimal Hindi-English latency or entity fidelity.
**Original idea.** Entity-risk buffering: maintain a short uncommitted hypothesis window only inside the model; delay the audio commit around high-risk spans and immediately release low-risk content. This must be implemented by the permitted checkpoint/decoder, not an external translator or text cascade.

## Q2. Which latency metric should be reported?
**Evidence.** SimulEval provides a client/server framework for measuring simultaneous translation with both quality and latency (Ma et al., EMNLP Demos 2020). Average Lagging (AL) is widely used, but Papi et al. (2022) show AL can reward over-generation and propose LAAL to correct length mismatch. A single first-audio timestamp is not enough to characterize end-to-end lag.
**Design choice.** Report AL and LAAL alongside first-output latency, finalization delay after input_end, real-time factor, and translation/intent/entity metrics. Use one explicit wait-k convention: target step i reads source position g(i)=min(|x|, k+i−1); state that this differs by one from formulations using k+i.
**Cheap experiment.** Use fixed references and the same clips to calculate AL/LAAL for k=2,3,4 and adaptive hold. Check target length mismatch manually before interpreting a lower AL as an improvement.
**Open question.** How should word-level source/target timing be aggregated when a target phrase reorders multiple Hindi words?
**Potential misleading claim checked.** “Lower latency always means better” is false: earlier speech may be wrong or require a take-back, which the interface forbids. Evaluate quality and latency jointly.

## Q3. What dataset design helps low-resource Indian code-mixed speech?
**Evidence.** IndicVoices (Javed et al., Findings ACL 2024) reports 7,348 hours across 22 Indian languages and a mix of read, extempore and conversational speech, highlighting speaker/district diversity. MuST-C (Di Gangi et al., NAACL 2019) demonstrates the value of aligned audio, transcripts and translations, but its TED-talk domain and language direction differ from spontaneous Hindi-English. FLEURS (Conneau et al., 2022) offers multilingual evaluation coverage but is not a substitute for conversational code-mixed data.
**Design choice.** Build domain-balanced records around natural speech and deliberately oversample difficult phenomena: code-switches, names, amounts in lakh/crore, phone/account digits, dates, negation, conditionals and self-corrections. Split by speaker and source, not random adjacent clips, to avoid leakage. Verify source redistribution rights before including any public corpus.
**Cheap experiment.** Create a 100-record audit slice stratified by accent, noise, code-switch density and entity type; compare transcript WER, entity exact match and translation intent preservation across strata.
**Open question.** What is the smallest real-speech slice that yields measurable gains over the supplied checkpoint?
**Potential misleading claim checked.** A large multilingual corpus is not automatically licensed for redistribution or representative of Hindi-English phone conversations; licence and domain must be verified separately.

## Q4. How should synthetic speech and word alignment be quality-controlled?
**Evidence.** SeamlessM4T (Seamless Communication et al., 2023) demonstrates multilingual speech/text translation across modalities and stresses the scale of aligned data; Whisper (Radford et al., ICML 2023) shows large weakly supervised multilingual ASR can be useful, but automatic transcripts still require auditing for names and numbers. XLS-R (Babu et al., 2021/2022) studies cross-lingual speech representations. These works support candidate tools/approaches, not a claim that their outputs meet this challenge’s licence or formatting constraints.
**Design choice.** Keep each record traceable to source audio, transcript, translation, model/voice, and alignment version. For English supervised targets after the mid-term, use only the mandated Bulbul v3 `shubh`, `en-IN`, 24 kHz settings; align English audio separately and filter skipped/repeated words. Never feed an external ASR/MT/LLM cascade into the final inference path.
**Cheap experiment.** Sample 30 word boundaries per clip, listen to each boundary, record original/corrected time and absolute error; check all names, digits, negations and correction spans separately. The current package has a boundary audit sheet prepared but the checks are still pending.
**Open question.** Can confidence-based filtering detect TTS pronunciation failures for Indian names and lakh/crore amounts before they enter training?
**Open question.** Does correction-aware buffering improve exact entity/intent scores enough to justify its additional lag on Hindi SOV clauses?

## Four cheap experiments and key open questions
1. Wait-k sweep (k=2/3/4): quality vs AL/LAAL; hold source and target references fixed.
2. Entity stress test: 100 synthetic prompts with amount/name/date/phone/negation/correction labels; evaluate exact match separately from BLEU.
3. Noise robustness: add noise/reverb only during training (augmentation does not add dataset hours under the statement); evaluate clean/noisy pairs with same transcript.
4. Alignment QA: human-audit 30 boundaries/clip and report median and 95th percentile absolute boundary error; never report estimated intervals as verified.
