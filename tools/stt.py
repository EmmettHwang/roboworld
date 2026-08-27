# -*- coding: utf-8 -*-
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from faster_whisper import WhisperModel

model = WhisperModel("medium", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    "temp/audio16k.wav", language="ko", beam_size=5,
    vad_filter=True, vad_parameters=dict(min_silence_duration_ms=400),
    condition_on_previous_text=False,
)
out = []
for s in segments:
    out.append({"start": round(s.start,2), "end": round(s.end,2), "text": s.text.strip()})
    print(f"[{s.start:7.2f} -> {s.end:7.2f}] {s.text.strip()}", flush=True)

with open("temp/transcript.json","w",encoding="utf-8") as f:
    json.dump({"duration": info.duration, "segments": out}, f, ensure_ascii=False, indent=2)
print("\n=== DONE:", len(out), "segments ===")
