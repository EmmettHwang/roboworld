# -*- coding: utf-8 -*-
import asyncio, json, subprocess, os, sys, io, wave, array, math
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import edge_tts

VOICE = "ko-KR-SunHiNeural"     # 친절하고 밝은 여성 (Friendly, Positive)
SR, TOTAL = 48000, 217.2
segs = json.load(open("temp/script.json", encoding="utf-8"))

def dur(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                        "-of","default=nw=1:nk=1", path], capture_output=True, text=True)
    return float(r.stdout.strip())

async def synth(text, rate, out):
    c = edge_tts.Communicate(text, VOICE, rate=rate)
    await c.save(out)

def to_wav(mp3, wav):
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",mp3,
                    "-ac","1","-ar",str(SR),"-c:a","pcm_s16le",wav], check=True)

async def main():
    # 각 세그먼트의 가용 시간 = 다음 세그먼트 시작까지
    for i, s in enumerate(segs):
        nxt = segs[i+1]["t"] if i+1 < len(segs) else 211.0
        s["avail"] = nxt - s["t"] - 0.22

    results = []
    for i, s in enumerate(segs):
        mp3, wav = f"temp/tts/s{i:02d}.mp3", f"temp/tts/s{i:02d}.wav"
        rate, d = -4, None
        for attempt in range(4):
            await synth(s["text"], f"{rate:+d}%", mp3)
            d = dur(mp3)
            if d <= s["avail"]:
                break
            need = d / s["avail"]                       # 필요한 배속
            rate = min(30, int(round((need * (1 + rate/100) - 1) * 100)) + 1)
        to_wav(mp3, wav)
        results.append((i, s["t"], d, rate, d <= s["avail"]))
        flag = "OK " if d <= s["avail"] else "OVER"
        print(f"{flag} {i+1:2d} t={s['t']:6.2f} avail={s['avail']:5.2f} len={d:5.2f} rate={rate:+d}%  {s['text'][:28]}")

    # ---- 무음 트랙에 배치 ----
    n = int(TOTAL * SR)
    buf = array.array("h", [0]) * 1
    buf = array.array("h", bytes(n * 2))
    for i, s in enumerate(segs):
        with wave.open(f"temp/tts/s{i:02d}.wav", "rb") as w:
            frames = array.array("h"); frames.frombytes(w.readframes(w.getnframes()))
        off = int(s["t"] * SR)
        for k, v in enumerate(frames):
            p = off + k
            if p >= n: break
            x = buf[p] + v
            buf[p] = 32767 if x > 32767 else (-32768 if x < -32768 else x)

    with wave.open("temp/narration.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(buf.tobytes())
    print("\n=> temp/narration.wav", round(n/SR,2), "sec")

asyncio.run(main())
