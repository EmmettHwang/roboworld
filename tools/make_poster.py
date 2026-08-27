# -*- coding: utf-8 -*-
"""국제 로봇 페스티벌 포스터 생성 -> assets/img/robot-festival.png

사진을 쓰지 않고 브랜드 톤(다크 네이비 + 골드)으로 직접 그린다.
난수는 시드를 고정해 매번 같은 결과가 나오도록 한다.
"""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1600, 1200
S = 2                                   # 슈퍼샘플링 배율
FB = "C:/Windows/Fonts/malgunbd.ttf"
FR = "C:/Windows/Fonts/malgun.ttf"

GOLD_HI  = (247, 232, 176)
GOLD_MID = (214, 170, 78)
GOLD_LO  = (160, 112, 38)
GOLD_DIM = (138, 106, 52)
INK      = (223, 229, 239)
MUTED    = (122, 136, 160)

rnd = random.Random(20260827)

# ─────────────────────────────────────────────────────────
# 1. 배경 : 다크 네이비 라디얼 그라데이션
# ─────────────────────────────────────────────────────────
bg = Image.new("RGB", (W, H), (0, 0, 0))
px = bg.load()
cx, cy = W * 0.5, H * 0.40
maxd = math.hypot(W * 0.68, H * 0.72)
for y in range(H):
    for x in range(W):
        d = math.hypot(x - cx, y - cy) / maxd
        t = max(0.0, 1.0 - d) ** 1.75
        px[x, y] = (int(3 + 18 * t), int(6 + 30 * t), int(12 + 54 * t))
bg = bg.filter(ImageFilter.GaussianBlur(3))

# ─────────────────────────────────────────────────────────
# 2. 회로 패턴 : 직각으로 꺾이는 선 + 노드
# ─────────────────────────────────────────────────────────
circuit = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
dc = ImageDraw.Draw(circuit)

def trace(x, y, steps, horiz):
    """직각으로 꺾이며 뻗어나가는 회로 한 줄"""
    pts = [(x, y)]
    for _ in range(steps):
        seg = rnd.randint(60, 190) * S
        if horiz:
            x += seg * rnd.choice((1, -1))
        else:
            y += seg * rnd.choice((1, -1))
        x = max(-40 * S, min(W * S + 40 * S, x))
        y = max(-40 * S, min(H * S + 40 * S, y))
        pts.append((x, y))
        horiz = not horiz
    return pts

for i in range(26):
    sx = rnd.randint(-30, W + 30) * S
    sy = rnd.randint(-30, H + 30) * S
    pts = trace(sx, sy, rnd.randint(3, 6), rnd.random() < .5)
    a = rnd.randint(26, 62)
    dc.line(pts, fill=(*GOLD_MID, a), width=rnd.choice((1, 1, 2)) * S, joint="curve")
    for p in pts[1:-1]:
        if rnd.random() < .45:
            r = rnd.choice((3, 4, 5)) * S
            dc.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=(*GOLD_MID, min(255, a + 55)))

# 별처럼 흩어진 점
for _ in range(150):
    x, y = rnd.randint(0, W) * S, rnd.randint(0, H) * S
    r = rnd.choice((1, 1, 2)) * S
    dc.ellipse([x-r, y-r, x+r, y+r], fill=(*GOLD_HI, rnd.randint(20, 70)))

circuit = circuit.resize((W, H), Image.LANCZOS)
canvas = Image.alpha_composite(bg.convert("RGBA"), circuit)

# ─────────────────────────────────────────────────────────
# 3. 궤도선 : 화면을 가로지르는 큰 호
# ─────────────────────────────────────────────────────────
orbit = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
do = ImageDraw.Draw(orbit)
for (ox, oy, rw, rh, a0, a1, alpha, wd) in [
    (-320, -180,  2300, 1500,  -8, 128, 40, 2),
    (-120,  120,  1980, 1420,  22, 152, 30, 1),
    ( 260, -420,  1500, 1900, 100, 240, 26, 1),
]:
    do.arc([ox*S, oy*S, (ox+rw)*S, (oy+rh)*S], start=a0, end=a1,
           fill=(*GOLD_MID, alpha), width=wd*S)
orbit = orbit.resize((W, H), Image.LANCZOS)
canvas = Image.alpha_composite(canvas, orbit)

# ─────────────────────────────────────────────────────────
# 4. 텍스트 헬퍼
# ─────────────────────────────────────────────────────────
def measure(txt, font, tracking=0):
    d = ImageDraw.Draw(Image.new("L", (8, 8)))
    ws = [d.textlength(c, font=font) for c in txt]
    return sum(ws) + tracking * (len(txt) - 1), ws

def draw_tracked(draw, txt, font, cx_, y, tracking=0, fill=255):
    _, ws = measure(txt, font, tracking)
    total = sum(ws) + tracking * (len(txt) - 1)
    x = cx_ - total / 2
    for c, w in zip(txt, ws):
        draw.text((x, y), c, font=font, fill=fill)
        x += w + tracking

def gold_layer(txt, size, cy_, tracking=0, bold=True, glow=8,
               top=GOLD_HI, mid=GOLD_MID, bot=GOLD_LO):
    """세로 금색 그라데이션이 채워진 텍스트 레이어"""
    m = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(m)
    f = ImageFont.truetype(FB if bold else FR, size * S)
    bb = d.textbbox((0, 0), txt, font=f)
    draw_tracked(d, txt, f, W * S / 2, cy_ * S - (bb[3] + bb[1]) / 2, tracking * S, 255)
    mask = m.resize((W, H), Image.LANCZOS)

    h = size + 12
    g = Image.new("RGB", (1, h)); gp = g.load()
    for i in range(h):
        t = i / max(1, h - 1)
        a, b, u = (top, mid, t / .45) if t < .45 else (mid, bot, (t - .45) / .55)
        gp[0, i] = tuple(int(a[k] + (b[k] - a[k]) * u) for k in range(3))
    plate = Image.new("RGB", (W, H), (0, 0, 0))
    plate.paste(g.resize((W, h), Image.BILINEAR), (0, cy_ - h // 2))

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(plate, (0, 0), mask)
    if glow:
        gl = layer.filter(ImageFilter.GaussianBlur(glow))
        gl.putalpha(gl.getchannel("A").point(lambda v: int(v * .5)))
        layer = Image.alpha_composite(
            Image.alpha_composite(Image.new("RGBA", (W, H), (0,0,0,0)), gl), layer)
    return layer

def flat_layer(txt, size, cy_, tracking=0, bold=False, color=INK):
    m = Image.new("L", (W * S, H * S), 0)
    d = ImageDraw.Draw(m)
    f = ImageFont.truetype(FB if bold else FR, size * S)
    bb = d.textbbox((0, 0), txt, font=f)
    draw_tracked(d, txt, f, W * S / 2, cy_ * S - (bb[3] + bb[1]) / 2, tracking * S, 255)
    mask = m.resize((W, H), Image.LANCZOS)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(Image.new("RGB", (W, H), color), (0, 0), mask)
    return layer

# ─────────────────────────────────────────────────────────
# 5. 타이틀 블록
# ─────────────────────────────────────────────────────────
for L in [
    flat_layer("INTERNATIONAL", 30, 176, tracking=17, bold=True, color=GOLD_DIM),
    gold_layer("국제 로봇 페스티벌", 116, 274, tracking=-2, glow=13),
    flat_layer("ROBOT FESTIVAL", 44, 366, tracking=13, bold=True, color=(176, 138, 74)),
]:
    canvas = Image.alpha_composite(canvas, L)

# 구분선
rule = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dr = ImageDraw.Draw(rule)
dr.line([(W/2 - 250, 412), (W/2 + 250, 412)], fill=(*GOLD_LO, 130), width=1)
dr.polygon([(W/2, 405), (W/2 + 9, 412), (W/2, 419), (W/2 - 9, 412)], fill=(*GOLD_MID, 210))
canvas = Image.alpha_composite(canvas, rule)

canvas = Image.alpha_composite(canvas, flat_layer(
    "충남 청양 · 로보월드캠퍼스", 34, 460, tracking=3, bold=True, color=INK))
canvas = Image.alpha_composite(canvas, flat_layer(
    "매년 개최 추진", 24, 502, tracking=6, color=(150, 164, 188)))

# ─────────────────────────────────────────────────────────
# 6. 공동개최 배지
# ─────────────────────────────────────────────────────────
badge_txt = "우송대학교 공동개최"
bf = ImageFont.truetype(FB, 25)
bw, _ = measure(badge_txt, bf, 1)
bx0, by0 = (W - (bw + 64)) / 2, 530
bx1, by1 = bx0 + bw + 64, by0 + 50
badge = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
db = ImageDraw.Draw(badge)
db.rounded_rectangle([bx0*S, by0*S, bx1*S, by1*S], radius=25*S,
                     fill=(*GOLD_MID, 22), outline=(*GOLD_MID, 120), width=2*S)
badge = badge.resize((W, H), Image.LANCZOS)
canvas = Image.alpha_composite(canvas, badge)
canvas = Image.alpha_composite(canvas, flat_layer(
    badge_txt, 25, int((by0 + by1) / 2), tracking=1, bold=True, color=GOLD_HI))

# ─────────────────────────────────────────────────────────
# 7. 중앙 엠블럼 : 동심 궤도 + 로봇 헤드 실루엣
# ─────────────────────────────────────────────────────────
em = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
de = ImageDraw.Draw(em)
ECX, ECY = W * S / 2, 800 * S
K = 1.30                                   # 엠블럼 전체 배율

# 동심원 궤도
for r, a, w in ((176, 55, 2), (140, 34, 1), (206, 26, 1)):
    rr = r * K
    de.ellipse([ECX-rr*S, ECY-rr*S*0.60, ECX+rr*S, ECY+rr*S*0.60],
               outline=(*GOLD_MID, a), width=w*S)
# 궤도 위 노드
for ang, rb in ((18, 176), (96, 206), (200, 176), (288, 206), (150, 140)):
    rad = math.radians(ang); rr = rb * K
    nx, ny = ECX + rr*S*math.cos(rad), ECY + rr*S*0.60*math.sin(rad)
    nr = 7*S
    de.ellipse([nx-nr, ny-nr, nx+nr, ny+nr], fill=(*GOLD_HI, 190))

# 로봇 헤드 (둥근 사각 + 눈 + 안테나)
hw, hh = 88*K, 76*K
de.rounded_rectangle([ECX-hw*S, ECY-hh*S, ECX+hw*S, ECY+hh*S],
                     radius=int(30*K)*S, outline=(*GOLD_MID, 215), width=5*S)
de.rounded_rectangle([ECX-58*K*S, ECY-30*K*S, ECX+58*K*S, ECY+16*K*S],
                     radius=int(16*K)*S, outline=(*GOLD_LO, 150), width=3*S)
for ex in (-30*K, 30*K):
    de.ellipse([ECX+ex*S-15*K*S, ECY-16*K*S, ECX+ex*S+15*K*S, ECY+14*K*S],
               fill=(*GOLD_HI, 235))
de.line([(ECX, ECY-hh*S), (ECX, ECY-hh*S-34*K*S)], fill=(*GOLD_MID, 200), width=5*S)
de.ellipse([ECX-14*K*S, ECY-hh*S-58*K*S, ECX+14*K*S, ECY-hh*S-30*K*S], fill=(*GOLD_HI, 240))
# 입 그릴
for gx in range(-34, 35, 17):
    de.line([(ECX+gx*K*S, ECY+34*K*S), (ECX+gx*K*S, ECY+52*K*S)],
            fill=(*GOLD_LO, 175), width=4*S)

em = em.resize((W, H), Image.LANCZOS)
glow = em.filter(ImageFilter.GaussianBlur(11))
glow.putalpha(glow.getchannel("A").point(lambda v: int(v * .55)))
canvas = Image.alpha_composite(canvas, glow)
canvas = Image.alpha_composite(canvas, em)

# ─────────────────────────────────────────────────────────
# 8. 하단 4개 프로그램 카드
# ─────────────────────────────────────────────────────────
CARDS = [
    ("로봇 배틀 아레나", "ROBOT BATTLE",    "자율 로봇 1:1 대결", "battle"),
    ("AI 챌린지",       "AI CHALLENGE",    "알고리즘 문제 해결", "ai"),
    ("로보틱스 엑스포",  "ROBOTICS EXPO",   "기업 · 연구 전시",   "expo"),
    ("메이커 워크숍",    "MAKER WORKSHOP",  "관람객 제작 체험",   "maker"),
]
CARD_TOP, CARD_H = 960, 196
GAP, MARGIN = 22, 92
CARD_W = (W - MARGIN*2 - GAP*3) / 4

cards = Image.new("RGBA", (W*S, H*S), (0, 0, 0, 0))
dcd = ImageDraw.Draw(cards)

def icon(d, kind, cx_, cy_, s):
    """카드 아이콘 (기하 도형)"""
    g = (*GOLD_MID, 225)
    if kind == "battle":                       # 링 + 마주 선 두 유닛
        d.ellipse([cx_-s, cy_-s*0.62, cx_+s, cy_+s*0.62], outline=g, width=3*S)
        for sx in (-0.46, 0.46):
            d.rounded_rectangle([cx_+s*sx-s*0.20, cy_-s*0.30,
                                 cx_+s*sx+s*0.20, cy_+s*0.24], radius=int(s*0.09), fill=g)
    elif kind == "ai":                          # 노드 네트워크
        hub = (cx_, cy_)
        pts = [(cx_+s*math.cos(math.radians(a)), cy_+s*0.72*math.sin(math.radians(a)))
               for a in (200, 270, 340, 60, 130)]
        for p in pts:
            d.line([hub, p], fill=(*GOLD_LO, 170), width=2*S)
        for p in pts:
            d.ellipse([p[0]-s*0.13, p[1]-s*0.13, p[0]+s*0.13, p[1]+s*0.13], fill=g)
        d.ellipse([cx_-s*0.20, cy_-s*0.20, cx_+s*0.20, cy_+s*0.20], fill=(*GOLD_HI, 240))
    elif kind == "expo":                        # 육각형 그리드
        for ox, oy in ((-0.52, -0.30), (0.52, -0.30), (0, 0.42)):
            p = [(cx_+ox*s + s*0.36*math.cos(math.radians(60*k+30)),
                  cy_+oy*s + s*0.36*math.sin(math.radians(60*k+30))) for k in range(6)]
            d.polygon(p, outline=g, width=2*S)
    else:                                       # maker : 렌치 + 기어
        d.ellipse([cx_-s*0.62, cy_-s*0.62, cx_+s*0.62, cy_+s*0.62], outline=g, width=3*S)
        for k in range(8):
            a = math.radians(45*k)
            d.line([(cx_+s*0.62*math.cos(a), cy_+s*0.62*math.sin(a)),
                    (cx_+s*0.92*math.cos(a), cy_+s*0.92*math.sin(a))], fill=g, width=3*S)
        d.ellipse([cx_-s*0.22, cy_-s*0.22, cx_+s*0.22, cy_+s*0.22],
                  outline=(*GOLD_HI, 235), width=3*S)

f_ko = ImageFont.truetype(FB, 26*S)
f_en = ImageFont.truetype(FB, 14*S)
f_de = ImageFont.truetype(FR, 17*S)

for i, (ko, en, desc, kind) in enumerate(CARDS):
    x0 = MARGIN + i * (CARD_W + GAP)
    x1 = x0 + CARD_W
    dcd.rounded_rectangle([x0*S, CARD_TOP*S, x1*S, (CARD_TOP+CARD_H)*S], radius=16*S,
                          fill=(14, 24, 42, 210), outline=(*GOLD_MID, 78), width=2*S)
    ccx = (x0 + x1) / 2 * S
    icon(dcd, kind, ccx, (CARD_TOP + 52) * S, 30 * S)

    for txt, f, yy, col in ((ko, f_ko, CARD_TOP+104, (*GOLD_HI, 245)),
                            (en, f_en, CARD_TOP+137, (*GOLD_DIM, 220)),
                            (desc, f_de, CARD_TOP+165, (*INK, 190))):
        tr = 4*S if f is f_en else 0
        ws = [dcd.textlength(c, font=f) for c in txt]
        total = sum(ws) + tr*(len(txt)-1)
        bb = dcd.textbbox((0, 0), txt, font=f)
        x = ccx - total/2
        y = yy*S - (bb[3]+bb[1])/2
        for c, w in zip(txt, ws):
            dcd.text((x, y), c, font=f, fill=col); x += w + tr

cards = cards.resize((W, H), Image.LANCZOS)
canvas = Image.alpha_composite(canvas, cards)

# ─────────────────────────────────────────────────────────
# 9. 비네팅 + 저장
# ─────────────────────────────────────────────────────────
vig = Image.new("L", (W, H), 0)
ImageDraw.Draw(vig).ellipse([-int(W*0.22), -int(H*0.30),
                             int(W*1.22), int(H*1.30)], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(190))
dark = Image.new("RGB", (W, H), (2, 4, 9))
out = Image.composite(canvas.convert("RGB"), dark, vig)

out.save("assets/img/robot-festival.png")
print("saved assets/img/robot-festival.png", out.size)
