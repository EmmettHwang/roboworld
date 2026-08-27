# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import statistics

im = Image.open("세계로봇대회.png").convert("RGB")
FB = "C:/Windows/Fonts/malgunbd.ttf"

# ---------- (1) 상단 부제 : 에디슨 사이언스 -> 로보월드 ----------
BOX = (150, 155, 910, 210)
region = im.crop(BOX)
# 강한 블러로 글자를 지우고 배경 톤만 남김
blur = region.filter(ImageFilter.GaussianBlur(16))
# 가장자리는 원본과 부드럽게 섞이도록 페더 마스크
mw, mh = region.size
mask = Image.new("L", (mw, mh), 0)
ImageDraw.Draw(mask).rectangle([10, 8, mw - 11, mh - 9], fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(7))
region.paste(blur, (0, 0), mask)
im.paste(region, BOX[:2])

d = ImageDraw.Draw(im)
sub = "매년 개최 · 이천 로보월드 캠퍼스타운 유치 추진"
f = ImageFont.truetype(FB, 32)
w = d.textlength(sub, font=f)
bb = d.textbbox((0, 0), sub, font=f)
cx, cy = 530, 183
x, y = cx - w / 2, cy - (bb[3] + bb[1]) / 2

# 부드러운 드롭섀도우 (별도 레이어 -> 블러 -> 합성)
sh = Image.new("L", im.size, 0)
ImageDraw.Draw(sh).text((x, y + 2), sub, font=f, fill=135)
sh = sh.filter(ImageFilter.GaussianBlur(1.7))
im.paste(Image.new("RGB", im.size, (10, 26, 54)), (0, 0), sh)

d = ImageDraw.Draw(im)
d.text((x, y), sub, font=f, fill=(255, 255, 255))
print(f"부제 재작성: 32px, 폭 {w:.0f}px")

# ---------- (2) 중앙 간판 : EDISON SCIENCE -> ROBOWORLD ----------
SIGN = (644, 346, 814, 363)
sx0, sy0, sx1, sy1 = SIGN
# 간판 파란색 표본 (글자 없는 좌·우 끝)
px = im.load()
samples = [px[x, y] for x in list(range(sx0 + 1, sx0 + 6)) + list(range(sx1 - 6, sx1 - 1))
           for y in range(sy0 + 3, sy1 - 2)]
blue = tuple(int(statistics.median(s[i] for s in samples)) for i in range(3))
d.rectangle([sx0 + 1, sy0 + 1, sx1 - 1, sy1 - 1], fill=blue)

txt = "ROBOWORLD CAMPUSTOWN"
fs = 14
while fs > 6:
    f2 = ImageFont.truetype(FB, fs)
    if d.textlength(txt, font=f2) <= (sx1 - sx0) - 14:
        break
    fs -= 1
tw = d.textlength(txt, font=f2)
b2 = d.textbbox((0, 0), txt, font=f2)
d.text(((sx0 + sx1) / 2 - tw / 2, (sy0 + sy1) / 2 - (b2[3] + b2[1]) / 2),
       txt, font=f2, fill=(248, 250, 255))
print(f"간판 재작성: {fs}px, 폭 {tw:.0f}px, 바탕 RGB{blue}")

im.save("web/assets/img/robot-competition.png")
im.crop((0, 120, 1100, 260)).save("temp/chk_top.png")
im.crop((600, 320, 860, 385)).resize((1040, 260)).save("temp/chk_sign.png")
print("saved")
