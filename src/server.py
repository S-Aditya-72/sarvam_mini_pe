"""Minimal asynchronous WebSocket echo server for the Sarvam Mini PS Dev track.

Protocol/streaming prototype only: echoes source PCM; it does not translate.
"""
import asyncio
import json
import os
import time
from http import HTTPStatus
import websockets
from websockets.exceptions import ConnectionClosed

FRAME_SECONDS = 0.080
FRAME_BYTES = 3840  # 24 kHz * 80 ms * 2 bytes/sample, mono PCM16
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "8000"))
STARTUP_DELAY = float(os.getenv("ECHO_DELAY_SECONDS", "0.20"))

async def process_request(path_or_connection, request_or_headers=None):
    """Health route compatible with websockets 12 and newer APIs."""
    legacy_api = isinstance(path_or_connection, str)
    path = path_or_connection if legacy_api else request_or_headers.path
    if path == "/health":
        status, reason, body = HTTPStatus.OK, "OK", b'{"status":"ok"}'
    elif path != "/ws":
        status, reason, body = HTTPStatus.NOT_FOUND, "Not Found", b"not found"
    else:
        return None

    headers = [("Content-Type", "application/json" if status == HTTPStatus.OK else "text/plain"),
               ("Content-Length", str(len(body)))]
    if legacy_api:
        # websockets <= 12 expects (status, headers, body).
        return status, headers, body
    # websockets >= 14 expects an HTTP Response object.
    from websockets.datastructures import Headers
    from websockets.http11 import Response
    return Response(status, reason, Headers(headers), body)


async def handle_session(ws):
    session_id = None
    queue = asyncio.Queue()
    input_ended = asyncio.Event()

    async def reader():
        nonlocal session_id
        async for message in ws:
            if isinstance(message, bytes):
                if len(message) != FRAME_BYTES:
                    raise ValueError(f"Expected {FRAME_BYTES}-byte frame, got {len(message)}")
                # Queue quickly; output pacing must not block socket ingestion.
                await queue.put(message)
            else:
                obj = json.loads(message)
                typ = obj.get("type")
                if typ == "session_start":
                    session_id = obj["session_id"]
                    if obj.get("sample_rate") != 24000 or obj.get("encoding") != "pcm_s16le":
                        raise ValueError("Expected 24 kHz pcm_s16le")
                elif typ == "input_end":
                    input_ended.set()
                    await queue.put(None)
                    return
                else:
                    raise ValueError(f"Unexpected client message: {typ}")
        if not input_ended.is_set():
            await queue.put(None)

    async def writer():
        first = await queue.get()
        if first is None:
            await ws.send(json.dumps({"type": "session_complete", "session_id": session_id}))
            return
        await asyncio.sleep(STARTUP_DELAY)
        next_send = time.monotonic()
        frame = first
        while frame is not None:
            now = time.monotonic()
            if now < next_send:
                await asyncio.sleep(next_send - now)
            await ws.send(frame)
            next_send = max(next_send + FRAME_SECONDS, time.monotonic())
            frame = await queue.get()
        await ws.send(json.dumps({"type": "session_complete", "session_id": session_id}))

    reader_task = asyncio.create_task(reader())
    writer_task = asyncio.create_task(writer())
    try:
        done, pending = await asyncio.wait(
            {reader_task, writer_task}, return_when=asyncio.FIRST_EXCEPTION
        )
        for task in done:
            exc = task.exception()
            if exc:
                raise exc
        await asyncio.gather(*pending)
    except (ConnectionClosed, asyncio.CancelledError):
        pass
    except Exception as exc:
        try:
            await ws.close(code=1008, reason=str(exc)[:120])
        except Exception:
            pass
    finally:
        for task in (reader_task, writer_task):
            if not task.done():
                task.cancel()
        await asyncio.gather(reader_task, writer_task, return_exceptions=True)

async def main():
    async with websockets.serve(
        handle_session, HOST, PORT, process_request=process_request,
        max_size=None, ping_interval=20
    ):
        print(f"WebSocket server: ws://{HOST}:{PORT}/ws")
        print(f"Health endpoint: http://{HOST}:{PORT}/health")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
