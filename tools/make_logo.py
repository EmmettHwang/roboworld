# -*- coding: utf-8 -*-
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1280, 720
FB = "C:/Windows/Fonts/malgunbd.ttf"
FR = "C:/Windows/Fonts/malgun.ttf"

# ---------- 1. 배경: 다크네이비 라디얼 그라데이션 ----------
bg = Image.new("RGB", (W, H), (0, 0, 0))
px = bg.load()
cx, cy = W / 2, H * 0.47
maxd = math.hypot(W * 0.62, H * 0.62)
for y in range(H):
    for x in range(W):
        d = math.hypot(x - cx, y - cy) / maxd
        t = max(0.0, 1.0 - d) ** 1.9
        px[x, y] = (int(2 + 16 * t), int(4 + 26 * t), int(8 + 46 * t))
bg = bg.filter(ImageFilter.GaussianBlur(2))

# ---------- 2. 금색 그라데이션 채우기 헬퍼 ----------
def gold(box_h, top=(247, 232, 176), mid=(214, 170, 78), bot=(160, 112, 38)):
    g = Image.new("RGB", (1, box_h))
    gp = g.load()
    for i in range(box_h):
        t = i / max(1, box_h - 1)
        if t < 0.45:
            u = t / 0.45; a, b = top, mid
        else:
            u = (t - 0.45) / 0.55; a, b = mid, bot
        gp[0, i] = tuple(int(a[k] + (b[k] - a[k]) * u) for k in range(3))
    return g

def paint(mask, y0, y1, glow=0):
    """mask(L) 영역을 y0~y1 세로 금색 그라데이션으로 칠한 RGBA 이미지 반환"""
    h = max(1, y1 - y0)
    grad = gold(h).resize((W, h), Image.BILINEAR)
    canvas = Image.new("RGB", (W, H), (0, 0, 0))
    canvas.paste(grad, (0, y0))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(canvas, (0, 0), mask)
    if glow:
        gl = out.filter(ImageFilter.GaussianBlur(glow))
        gl.putalpha(gl.getchannel("A").point(lambda v: int(v * 0.55)))
        base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        base = Image.alpha_composite(base, gl)
        out = Image.alpha_composite(base, out)
    return out

# ---------- 3. 심볼 "RWC" + 궤도 + 스파클 ----------
S = 4  # 슈퍼샘플링
m = Image.new("L", (W * S, H * S), 0)
d = ImageDraw.Draw(m)

f_sym = ImageFont.truetype(FB, 150 * S)
sym = "RWC"
bb = d.textbbox((0, 0), sym, font=f_sym)
sw, sh = bb[2] - bb[0], bb[3] - bb[1]
sx = (W * S - sw) // 2 - bb[0] - 14 * S
sy = int(255 * S) - bb[1]
d.text((sx, sy), sym, font=f_sym, fill=255)
SYM_TOP, SYM_BOT = 210, 255 + 150

# 궤도(swoosh) + 구 : 별도 레이어에 그린 뒤 살짝 회전
sw_layer = Image.new("L", (W * S, H * S), 0)
ds = ImageDraw.Draw(sw_layer)
ox0, oy0 = sx - 40 * S, sy + bb[1] + int(sh * 0.26)
ox1, oy1 = sx + sw + 70 * S, sy + bb[1] + int(sh * 1.34)
ds.arc([ox0, oy0, ox1, oy1], start=-14, end=192, fill=255, width=13 * S)
sw_layer = sw_layer.rotate(-5, center=((ox0 + ox1) / 2, (oy0 + oy1) / 2), resample=Image.BILINEAR)
m.paste(sw_layer, (0, 0), sw_layer)

# 궤도 위 구(球) — 글자 위로 떠오르게
r = 27 * S
gcx, gcy = sx + int(sw * 0.50), int(222 * S)
d.ellipse([gcx - r, gcy - r, gcx + r, gcy + r], fill=255)

# 4방향 스파클
def sparkle(cxs, cys, rx, ry):
    d.polygon([(cxs, cys - ry), (cxs + rx * 0.30, cys - ry * 0.30),
               (cxs + rx, cys), (cxs + rx * 0.30, cys + ry * 0.30),
               (cxs, cys + ry), (cxs - rx * 0.30, cys + ry * 0.30),
               (cxs - rx, cys), (cxs - rx * 0.30, cys - ry * 0.30)], fill=255)
sparkle(sx + sw + 52 * S, sy + bb[1] + int(sh * 0.18), 24 * S, 52 * S)

mask_sym = m.resize((W, H), Image.LANCZOS)
layer_sym = paint(mask_sym, SYM_TOP - 30, SYM_BOT + 40, glow=9)

# ---------- 4. 한글 / 영문 워드마크 ----------
def text_layer(txt, font_path, size, cy_px, tracking=0, color_shift=None, glow=0):
    mm = Image.new("L", (W * S, H * S), 0)
    dd = ImageDraw.Draw(mm)
    f = ImageFont.truetype(font_path, size * S)
    if tracking:
        widths = [dd.textlength(ch, font=f) for ch in txt]
        total = sum(widths) + tracking * S * (len(txt) - 1)
        x = (W * S - total) / 2
        b = dd.textbbox((0, 0), txt, font=f)
        y = cy_px * S - (b[3] + b[1]) / 2
        for ch, w in zip(txt, widths):
            dd.text((x, y), ch, font=f, fill=255)
            x += w + tracking * S
    else:
        b = dd.textbbox((0, 0), txt, font=f)
        dd.text(((W * S - (b[2] - b[0])) / 2 - b[0], cy_px * S - (b[3] + b[1]) / 2),
                txt, font=f, fill=255)
    mk = mm.resize((W, H), Image.LANCZOS)
    return paint(mk, cy_px - size // 2 - 4, cy_px + size // 2 + 4, glow=glow), mk

layer_ko, _ = text_layer("로보월드캠퍼스", FB, 62, 462, tracking=-1, glow=6)

# 영문은 톤 다운
mm = Image.new("L", (W * S, H * S), 0)
dd = ImageDraw.Draw(mm)
f_en = ImageFont.truetype(FR, 30 * S)
en = "ROBOWORLD CAMPUS"
tr = 5 * S
ws = [dd.textlength(c, font=f_en) for c in en]
x = (W * S - (sum(ws) + tr * (len(en) - 1))) / 2
bb2 = dd.textbbox((0, 0), en, font=f_en)
y = 519 * S - (bb2[3] + bb2[1]) / 2
for c, w in zip(en, ws):
    dd.text((x, y), c, font=f_en, fill=255)
    x += w + tr
mask_en = mm.resize((W, H), Image.LANCZOS)
layer_en = Image.new("RGBA", (W, H), (0, 0, 0, 0))
layer_en.paste(Image.new("RGB", (W, H), (176, 138, 74)), (0, 0), mask_en)

# ---------- 5. 합성 ----------
out = bg.convert("RGBA")
for L in (layer_sym, layer_ko, layer_en):
    out = Image.alpha_composite(out, L)
out.convert("RGB").save("temp/outro_logo.png")
print("saved temp/outro_logo.png")
