# Sarvam Mini PS — Dev Track Prototype

This repository contains six short recordings and a minimal asynchronous WebSocket echo server.
**Important:** the server is a protocol/streaming prototype. It echoes source PCM; it does not
translate Hindi to English and is not a competition-ready final model.

## Protocol implemented
- One WebSocket connection per session.
- Receives `session_start` JSON, then 80 ms binary PCM16 mono 24 kHz frames (3,840 bytes).
- Reads incoming frames into an `asyncio.Queue` so socket ingestion is not blocked by output pacing.
- After a configurable startup delay, echoes frames at an 80 ms cadence.
- On `input_end`, drains queued audio and sends one `session_complete` JSON message.
- `GET /health` and WebSocket `/ws` are served on port 8000. This was verified in the user-run Docker test.

## Setup
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python src/server.py
```

## Convert audio to required format
```bash
python src/audio_utils.py "recordings/raw/your-recording.wav" "recordings/processed/clip01.wav"
```
The included WhatsApp originals are MP4 containers. Extract/convert those with ffmpeg, e.g.:
```bash
ffmpeg -i "recordings/raw/clip.mp4" -ac 1 -ar 24000 -sample_fmt s16 "recordings/processed/clip01.wav"
```
The WAVs already in `recordings/processed/` were converted to mono PCM16 at 24 kHz for this bundle.

## Run a client test
```bash
python src/client.py "recordings/processed/WhatsApp Audio 2026-10-15 at 12.48.11 PM.wav"
```
The client reports frame counts and first-output time. These are local echo-prototype measurements,
not translation quality or model latency.

## Docker
Build and run from the repository root:
```bash
docker build -t sarvam-mini-ps-dev .
docker run --rm --name sarvam-mini-ps-dev -p 8000:8000 sarvam-mini-ps-dev
```
In a second terminal, verify health:
```bash
curl -i http://localhost:8000/health
```
Expected: `HTTP/1.1 200 OK` and `{"status":"ok"}`. Then test the container (not the host process):
```bash
python src/client.py "recordings/processed/WhatsApp Audio 2026-10-15 at 12.48.11 PM.wav" --uri ws://127.0.0.1:8000/ws --fast
```
Confirm `input_frames == output_frames`, `session_complete_count == 1`, and `no_messages_after_completion == true`. Stop the container with Ctrl+C. The Docker build and container checks must be run on a machine with Docker installed.

## Known limitations / next steps
- No translation model is connected; audio is echoed unchanged.
- Docker build and container-level tests must be run on a machine with Docker installed.
- Error handling is intentionally minimal; test disconnects, malformed frames and backpressure.
- Echo latency is not simultaneous translation latency.

## Submission status
See `MIDTERM_REPORT.md`, `PART_B_RESEARCH.md`, `PART_C_DATASET_PLAN.md`, and `REFERENCES.md`. **Important:** transcript drafts and word timings are unverified; the boundary audit is pending. The server is an echo prototype, not a translator.
