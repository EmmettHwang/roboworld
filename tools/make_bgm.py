# -*- coding: utf-8 -*-
"""소개영상 배경음악 합성 -> temp/bgm.wav

작곡가 음원이 아니라 코드로 합성한 앰비언트 패드다.
나레이션 뒤에 낮게 깔리는 용도로만 쓴다.
"""
import numpy as np, wave, math

SR = 48000
DUR = 223.0
t = np.arange(int(SR * DUR)) / SR

# ── 코드 진행 : I - V - vi - IV (희망적이고 열린 느낌) ──
# C major 기준, 8마디 x 4 = 한 바퀴 32초
ROOT = 130.81          # C3
PROG = [
    (1.0,   [0, 4, 7, 11]),      # Cmaj7
    (1.498, [0, 4, 7, 10]),      # G7  (5도)
    (1.682, [0, 3, 7, 10]),      # Am7 (6도)
    (1.335, [0, 4, 7, 11]),      # Fmaj7 (4도)
]
BAR = 8.0              # 코드 하나당 8초

def semi(n):
    return 2 ** (n / 12)

out = np.zeros_like(t)

# ── 1. 패드 : 코드를 길게 깔아 준다 ──
for i in range(int(DUR / BAR) + 1):
    ratio, ivs = PROG[i % len(PROG)]
    base = ROOT * ratio
    s, e = i * BAR, (i + 1) * BAR
    idx = (t >= s) & (t < e + 2.0)          # 다음 코드와 살짝 겹치게
    if not idx.any():
        continue
    local = t[idx] - s
    # 부드러운 페이드 인·아웃 (겹치는 구간에서 자연스럽게 이어짐)
    env = np.minimum(local / 2.2, 1.0) * np.minimum(np.maximum((BAR + 2.0 - local) / 2.4, 0), 1.0)
    voice = np.zeros_like(local)
    for k, iv in enumerate(ivs):
        f = base * semi(iv)
        # 배음을 조금 섞어 신스 패드 질감
        voice += (np.sin(2*np.pi*f*local) * 0.55
                  + np.sin(2*np.pi*f*2*local) * 0.26
                  + np.sin(2*np.pi*f*3*local) * 0.13) / (k + 1.6)
        # 아주 느린 디튠으로 코러스감
        voice += np.sin(2*np.pi*(f*1.0015)*local) * 0.22 / (k + 1.8)
    out[idx] += voice * env * 0.30

# ── 2. 아르페지오 : 잔잔하게 반짝이는 상단 ──
NOTE = 0.5
for n in range(int(DUR / NOTE)):
    s = n * NOTE
    bar_i = int(s // BAR) % len(PROG)
    ratio, ivs = PROG[bar_i]
    iv = ivs[[0, 2, 1, 3, 2, 1][n % 6]]
    f = ROOT * ratio * semi(iv) * 4        # 2옥타브 위
    idx = (t >= s) & (t < s + NOTE * 2.4)
    if not idx.any():
        continue
    local = t[idx] - s
    env = np.exp(-local * 2.4) * (1 - np.exp(-local * 60))
    out[idx] += np.sin(2*np.pi*f*local) * env * 0.115

# ── 3. 서브 베이스 : 바닥을 받쳐 준다 ──
for i in range(int(DUR / BAR) + 1):
    ratio, _ = PROG[i % len(PROG)]
    f = ROOT * ratio / 2
    s, e = i * BAR, (i + 1) * BAR
    idx = (t >= s) & (t < e + 1.0)
    if not idx.any():
        continue
    local = t[idx] - s
    env = np.minimum(local / 1.5, 1.0) * np.minimum(np.maximum((BAR + 1.0 - local) / 1.5, 0), 1.0)
    out[idx] += np.sin(2*np.pi*f*local) * env * 0.12

# ── 4. 전체 곡선 : 도입은 조용하게, 끝은 여운 ──
shape = np.ones_like(t)
shape *= np.minimum(t / 6.0, 1.0)                       # 페이드 인
shape *= np.minimum(np.maximum((DUR - t) / 8.0, 0), 1)  # 페이드 아웃
# 아주 느린 물결로 생동감
shape *= 0.86 + 0.14 * np.sin(2*np.pi*t/47.0)
out *= shape

# ── 5. 정규화 ──
out = out / (np.abs(out).max() + 1e-9) * 0.82
# 부드러운 하이컷 (딱딱한 배음 정리)
b = 0.16
filt = np.copy(out)
for _ in range(2):
    filt[1:] = filt[1:] * (1 - b) + filt[:-1] * b
out = filt

pcm = (out * 32767).astype(np.int16)
with wave.open("temp/bgm.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"saved temp/bgm.wav  {DUR:.1f}s")
