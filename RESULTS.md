# RESULTS.md — Docker / WebSocket protocol verification

## Environment
User-reported Windows PowerShell session, Docker container `sarvam-mini-ps-dev`, WebSocket `ws://127.0.0.1:8000/ws`.

## Health endpoint
`curl.exe -i http://localhost:8000/health` returned:
- `HTTP/1.1 200 OK`
- `Content-Type: application/json`
- Body: `{"status":"ok"}`
- Server: `Python/3.11 websockets/12.0`

## Client tests reported by user
| Run | Mode | Input frames | Output frames | First output | Wall time | Completion | Post-completion messages |
|---|---|---:|---:|---:|---:|---|---|
| 1 | paced | 382 | 382 | 0.232 s | 35.686 s | exactly 1 | none observed |
| 2 | `--fast` | 382 | 382 | 0.230 s | 30.720 s | exactly 1 | none observed |
| 3 | `--fast`, explicit URI | 382 | 382 | 0.235 s | 30.728 s | exactly 1 | none observed |
| 4 | `--fast`, explicit URI | 382 | 382 | 0.233 s | 30.719 s | exactly 1 | none observed |

The client note says: “Echo-prototype timing only; not translation quality or model latency.”

## Interpretation
The container health endpoint and basic WebSocket framing/completion checks passed in the reported tests. Matching input/output frame counts are expected for an echo server. The ~0.23 s first-output time is not evidence of simultaneous translation performance. The server returns source PCM unchanged; translation quality, intent accuracy, entity accuracy and audio naturalness are not evaluated.

## Remaining tests
- Disconnect during input/output, malformed JSON, invalid frame size, repeated `session_start`, and slow-client/backpressure cases.
- Confirm container starts within 10 s and repeated sessions satisfy the organiser harness.
- Full competition gate checks after the permitted checkpoint and reference client are released.
