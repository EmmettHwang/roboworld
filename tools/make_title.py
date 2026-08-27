# -*- coding: utf-8 -*-
"""소개영상 도입부 타이틀 카드 생성 -> temp/title_card.png"""
import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 배경 + 로고는 make_logo.py 결과를 재사용
if not os.path.exists("temp/outro_logo.png"):
    subprocess.run([sys.executable, "tools/make_logo.py"], check=True)

W, H = 1280, 720
FB = "C:/Windows/Fonts/malgunbd.ttf"
im = Image.open("temp/outro_logo.png").convert("RGB")

def gold_text(img, txt, font, cy, tracking=0, glow=6,
              top=(247,232,176), mid=(214,170,78), bot=(160,112,38)):
    S = 4
    m = Image.new("L", (W*S, H*S), 0)
    d = ImageDraw.Draw(m)
    f = ImageFont.truetype(font[0], font[1]*S)
    ws = [d.textlength(c, font=f) for c in txt]
    total = sum(ws) + tracking*S*(len(txt)-1)
    x = (W*S - total)/2
    bb = d.textbbox((0,0), txt, font=f)
    y = cy*S - (bb[3]+bb[1])/2
    for c, w in zip(txt, ws):
        d.text((x, y), c, font=f, fill=255); x += w + tracking*S
    mask = m.resize((W, H), Image.LANCZOS)

    h = font[1] + 10
    g = Image.new("RGB", (1, h)); gp = g.load()
    for i in range(h):
        t = i/max(1, h-1)
        a, b, u = (top, mid, t/0.45) if t < 0.45 else (mid, bot, (t-0.45)/0.55)
        gp[0, i] = tuple(int(a[k] + (b[k]-a[k])*u) for k in range(3))
    canvas = Image.new("RGB", (W, H), (0,0,0))
    canvas.paste(g.resize((W, h), Image.BILINEAR), (0, cy - h//2))
    layer = Image.new("RGBA", (W, H), (0,0,0,0))
    layer.paste(canvas, (0,0), mask)
    if glow:
        gl = layer.filter(ImageFilter.GaussianBlur(glow))
        gl.putalpha(gl.getchannel("A").point(lambda v: int(v*0.5)))
        base = Image.alpha_composite(Image.new("RGBA",(W,H),(0,0,0,0)), gl)
        layer = Image.alpha_composite(base, layer)
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")

# 상단 : 제안 문구
im = gold_text(im, "인구감소지역 청양군을 위한 제안", (FB, 38), cy=118, tracking=2, glow=7)

# 하단 : 부제 (톤 다운)
S = 4
m = Image.new("L", (W*S, H*S), 0)
d = ImageDraw.Draw(m)
f = ImageFont.truetype(FB, 27*S)
sub = "아이들이 돌아오는 청양군"
tr = 3*S
ws = [d.textlength(c, font=f) for c in sub]
x = (W*S - (sum(ws) + tr*(len(sub)-1)))/2
bb = d.textbbox((0,0), sub, font=f)
y = 600*S - (bb[3]+bb[1])/2
for c, w in zip(sub, ws):
    d.text((x, y), c, font=f, fill=255); x += w + tr
mask = m.resize((W, H), Image.LANCZOS)
layer = Image.new("RGBA", (W, H), (0,0,0,0))
layer.paste(Image.new("RGB", (W, H), (186, 150, 92)), (0,0), mask)
im = Image.alpha_composite(im.convert("RGBA"), layer).convert("RGB")

im.save("temp/title_card.png")
print("saved temp/title_card.png")
