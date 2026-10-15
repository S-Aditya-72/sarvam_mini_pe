"""Validate and convert source recordings to the required mono PCM16/24 kHz format."""
import argparse
import wave
from pathlib import Path
import audioop

def convert(src, dst):
    with wave.open(str(src), "rb") as wf:
        channels, width, rate = wf.getnchannels(), wf.getsampwidth(), wf.getframerate()
        frames = wf.readframes(wf.getnframes())
    if width != 2:
        frames = audioop.lin2lin(frames, width, 2)
    if channels == 2:
        frames = audioop.tomono(frames, 2, 0.5, 0.5)
    elif channels != 1:
        raise ValueError(f"Unsupported channel count: {channels}")
    if rate != 24000:
        frames, _ = audioop.ratecv(frames, 2, 1, rate, 24000, None)
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(dst), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(frames)
    return len(frames) / 2 / 24000

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("output")
    a = p.parse_args()
    print(f"duration_seconds={convert(a.input, a.output):.3f}")
