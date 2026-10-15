"""Test client: stream a mono 24 kHz PCM16 WAV as real-time 80 ms frames."""
import argparse
import asyncio
import json
import time
import wave
import websockets
from websockets.exceptions import ConnectionClosed

FRAME_BYTES = 3840
FRAME_SECONDS = 0.080

async def run(uri, wav_path, realtime=True):
    with wave.open(wav_path, "rb") as wf:
        assert wf.getnchannels() == 1, "WAV must be mono"
        assert wf.getsampwidth() == 2, "WAV must be 16-bit PCM"
        assert wf.getframerate() == 24000, "WAV must be 24 kHz"
        raw = wf.readframes(wf.getnframes())
    # Zero-pad final frame to 80 ms; valid_samples excludes padding.
    valid_samples = len(raw) // 2
    frames = [raw[i:i+FRAME_BYTES] for i in range(0, len(raw), FRAME_BYTES)]
    if frames and len(frames[-1]) < FRAME_BYTES:
        frames[-1] += b"\x00" * (FRAME_BYTES - len(frames[-1]))
    session_id = "mini-ps-test"
    sent = received = 0
    started = time.monotonic()
    async with websockets.connect(uri, max_size=None) as ws:
        await ws.send(json.dumps({
            "type": "session_start", "session_id": session_id,
            "sample_rate": 24000, "encoding": "pcm_s16le",
            "source_language": "hi", "target_language": "en"
        }))
        async def sender():
            nonlocal sent
            for frame in frames:
                await ws.send(frame)
                sent += 1
                if realtime:
                    await asyncio.sleep(FRAME_SECONDS)
            await ws.send(json.dumps({
                "type": "input_end", "session_id": session_id,
                "valid_samples": valid_samples
            }))
        send_task = asyncio.create_task(sender())
        first_output = None
        completion_count = 0
        completion_seen_at = None
        async for message in ws:
            if isinstance(message, bytes):
                if completion_count:
                    raise RuntimeError("Protocol violation: audio received after session_complete")
                received += 1
                if first_output is None:
                    first_output = time.monotonic() - started
            else:
                obj = json.loads(message)
                if obj.get("type") == "session_complete":
                    completion_count += 1
                    completion_seen_at = time.monotonic()
                    if completion_count > 1:
                        raise RuntimeError("Protocol violation: duplicate session_complete")
                    break
                else:
                    raise RuntimeError(f"Protocol violation: unexpected server text frame: {obj}")
        await send_task
        if completion_count != 1:
            raise RuntimeError(f"Expected exactly one session_complete, got {completion_count}")
        # The protocol says no messages may follow session_complete. Keep the
        # connection open briefly to detect an immediately-following extra frame.
        try:
            extra = await asyncio.wait_for(ws.recv(), timeout=0.25)
            raise RuntimeError(f"Protocol violation: message after session_complete: {type(extra).__name__}")
        except (asyncio.TimeoutError, ConnectionClosed):
            # A clean server close immediately after session_complete is valid.
            pass
    elapsed = time.monotonic() - started
    print(json.dumps({
        "session_id": session_id, "input_frames": sent,
        "output_frames": received, "first_output_seconds": round(first_output or 0, 3),
        "wall_seconds": round(elapsed, 3), "echo_delay_seconds": round((first_output or 0), 3),
        "session_complete_count": completion_count,
        "no_messages_after_completion": True,
        "note": "Echo-prototype timing only; not translation quality or model latency."
    }, indent=2))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("wav")
    p.add_argument("--uri", default="ws://127.0.0.1:8000/ws")
    p.add_argument("--fast", action="store_true", help="Send without real-time pacing")
    a = p.parse_args()
    asyncio.run(run(a.uri, a.wav, realtime=not a.fast))
