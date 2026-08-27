# -*- coding: utf-8 -*-
"""교육 프로그램 12장으로 짧은 소개 클립 제작 -> 약 48초

  python tools/make_edu_clip.py

중간 파일은 SLIDE_WORK 환경변수 경로에 만든다(구글드라이브 밖 로컬).
자막은 Pillow 로 PNG 를 만들어 얹는다. drawtext 는 한글 폰트 경로 문제가
잦고 자간·그림자 조정이 어렵다.
"""
import os, subprocess, sys, io
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

W, H, FPS = 1280, 720, 25
HOLD, XF = 3.5, 0.8                    # 컷 길이, 크로스페이드
WORK = os.environ.get('SLIDE_WORK', 'temp')
FB = "C:/Windows/Fonts/malgunbd.ttf"
FR = "C:/Windows/Fonts/malgun.ttf"
BGM = 'Docs/새로제작이미지/로봇대회/Warm Horizons.mp3'

GOLD_HI, GOLD, GOLD_LO = (247, 232, 176), (214, 170, 78), (160, 112, 38)
INK = (232, 238, 248)

# (이미지, 분류, 프로그램명, 한 줄 설명, 움직임)
CUTS = [
    ('edu-korean.jpg',       '미래 세대 교육',   '아동 · 청소년 국어 교육', '읽고, 생각하고, 의견을 나누며',      'in'),
    ('edu-english.jpg',      '미래 세대 교육',   '아동 · 청소년 영어 교육', '다른 언어로 넓히는 세계',            'right'),
    ('edu-math.jpg',         '미래 세대 교육',   '아동 · 청소년 수학 교육', '사고력과 창의적 탐구',              'in'),
    ('edu-maker.jpg',        '미래 세대 교육',   '메이커 · 창작 교실',     '직접 만들며 배우는 즐거움',          'left'),
    ('senior-choir.jpg',     '평생 교육',        '중장년 · 시니어 합창',   '노래로 만나는 세대',                'in'),
    ('senior-painting.jpg',  '평생 교육',        '시니어 회화 수업',       '표현의 즐거움과 일상의 여유',        'right'),
    ('wellness-skincare.jpg','평생 교육',        '웰니스 · 스킨케어',      '생활 속 건강 관리와 자기 돌봄',      'in'),
    ('senior-health.jpg',    '평생 교육',        '시니어 건강 수업',       '무리 없는 운동으로 건강한 일상',      'left'),
    ('youth-mentoring.jpg',  '스포츠 · 자기계발', '청소년 일대일 멘토링',   '가까이에서 함께 고민하며',           'in'),
    ('group-workshop.jpg',   '스포츠 · 자기계발', '그룹 자기계발 워크숍',   '협업 속에서 자라는 가능성',          'right'),
    ('sports-badminton.jpg', '스포츠 · 자기계발', '생활운동 수업',         '함께 움직이며 건강해지는 몸과 마음',  'in'),
    ('pilates-yoga.jpg',     '스포츠 · 자기계발', '필라테스 · 요가',        '호흡과 자세로 되찾는 균형',          'left'),
]


# ─────────────────────────────────────────────
# 자막 · 타이틀 이미지
# ─────────────────────────────────────────────
def gold_grad(size, h):
    g = Image.new("RGB", (1, h))
    gp = g.load()
    for i in range(h):
        t = i / max(1, h - 1)
        a, b, u = (GOLD_HI, GOLD, t / .45) if t < .45 else (GOLD, GOLD_LO, (t - .45) / .55)
        gp[0, i] = tuple(int(a[k] + (b[k] - a[k]) * u) for k in range(3))
    return g.resize(size, Image.BILINEAR)


def caption(kind, name, desc, path):
    """왼쪽 아래에 얹을 자막 (분류 · 이름 · 설명)"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # 아래쪽 그라데이션 (글자가 사진에 묻히지 않게)
    for y in range(H - 260, H):
        a = int(215 * ((y - (H - 260)) / 260) ** 1.5)
        d.line([(0, y), (W, y)], fill=(5, 8, 16, a))

    x, base = 74, H - 74
    f_desc = ImageFont.truetype(FR, 23)
    f_name = ImageFont.truetype(FB, 42)
    f_kind = ImageFont.truetype(FB, 19)

    d.text((x, base), desc, font=f_desc, fill=(*INK, 225), anchor='ls')
    d.text((x, base - 44), name, font=f_name, fill=(255, 255, 255, 255), anchor='ls')
    # 분류는 금색 + 앞에 짧은 선
    d.line([(x, base - 104), (x + 26, base - 104)], fill=(*GOLD, 230), width=2)
    d.text((x + 38, base - 97), kind, font=f_kind, fill=(*GOLD_HI, 235), anchor='ls')
    im.save(path)


def title_card(path):
    im = Image.new("RGB", (W, H), (5, 8, 16))
    px = im.load()
    import math
    for y in range(H):
        for x in range(0, W, 2):
            dd = math.hypot(x - W/2, y - H*0.45) / math.hypot(W*0.62, H*0.66)
            t = max(0.0, 1 - dd) ** 1.8
            c = (int(3 + 16*t), int(6 + 26*t), int(11 + 46*t))
            px[x, y] = c
            if x + 1 < W: px[x+1, y] = c
    im = im.filter(ImageFilter.GaussianBlur(2)).convert("RGBA")

    S = 3
    m = Image.new("L", (W*S, H*S), 0)
    d = ImageDraw.Draw(m)
    f = ImageFont.truetype(FB, 62*S)
    txt = "배움에는 정해진 나이가 없습니다"
    bb = d.textbbox((0, 0), txt, font=f)
    d.text(((W*S - (bb[2]-bb[0]))/2 - bb[0], H*S*0.46 - (bb[3]+bb[1])/2), txt, font=f, fill=255)
    mask = m.resize((W, H), Image.LANCZOS)
    plate = Image.new("RGB", (W, H), (0, 0, 0))
    plate.paste(gold_grad((W, 76), 76), (0, int(H*0.46) - 38))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(plate, (0, 0), mask)
    glow = layer.filter(ImageFilter.GaussianBlur(11))
    glow.putalpha(glow.getchannel("A").point(lambda v: int(v*.5)))
    im = Image.alpha_composite(Image.alpha_composite(im, glow), layer)

    d2 = ImageDraw.Draw(im)
    f2 = ImageFont.truetype(FR, 25)
    sub = "미래 세대부터 시니어까지, 하나의 캠퍼스 안에서"
    d2.text((W/2, H*0.46 + 66), sub, font=f2, fill=(150, 164, 188, 235), anchor='ms')
    im.convert("RGB").save(path)


def kenburns(mode, dur):
    Z = 1.16
    bw, bh = int(W*Z)//2*2, int(H*Z)//2*2
    mx, my = bw - W, bh - H
    pos = {
        'in':    (f"({mx})*(t/{dur})",   f"({my})*(t/{dur})"),
        'left':  (f"({mx})*(1-t/{dur})", f"({my})/2"),
        'right': (f"({mx})*(t/{dur})",   f"({my})/2"),
    }[mode]
    return (f"scale={bw}:{bh}:force_original_aspect_ratio=increase,crop={bw}:{bh},"
            f"crop={W}:{H}:'{pos[0]}':'{pos[1]}',"
            f"scale=in_range=full:out_range=tv,format=yuv420p,setrange=tv,setsar=1,fps={FPS}")


def main():
    os.makedirs(f'{WORK}/edu', exist_ok=True)
    title_card(f'{WORK}/edu/title.png')

    dur = HOLD + XF
    clips = []
    for i, (img, kind, name, desc, mode) in enumerate(CUTS):
        p = f'assets/img/{img}'
        if not os.path.exists(p):
            print('  건너뜀:', img); continue
        cap = f'{WORK}/edu/cap{i:02d}.png'
        caption(kind, name, desc, cap)
        out = f'{WORK}/edu/c{i:02d}.mp4'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                        '-loop', '1', '-t', str(dur), '-i', p,
                        '-loop', '1', '-t', str(dur), '-i', cap,
                        '-filter_complex',
                        f"[0:v]{kenburns(mode, dur)}[bg];"
                        f"[1:v]format=rgba,fade=t=in:st=0.25:d=0.5:alpha=1[cp];"
                        f"[bg][cp]overlay=0:0:format=auto,format=yuv420p[v]",
                        '-map', '[v]', '-c:v', 'libx264', '-preset', 'veryfast',
                        '-crf', '18', '-pix_fmt', 'yuv420p', out], check=True)
        clips.append(out)
        print(f'  {i+1:2d}/12  {name}')

    # ── 타이틀 + 컷들 이어 붙이기 ──
    TITLE_LEN = 3.2
    inputs = ['-loop', '1', '-t', str(TITLE_LEN + XF), '-i', f'{WORK}/edu/title.png']
    for c in clips:
        inputs += ['-i', c]
    NORM = f"scale=in_range=full:out_range=tv,format=yuv420p,setrange=tv,setsar=1,fps={FPS}"
    fc = [f"[0:v]scale={W}:{H},setsar=1,fps={FPS},format=yuv420p,setrange=tv,"
          f"fade=t=in:st=0:d=0.6[v0]"]
    prev, off = 'v0', TITLE_LEN
    for i in range(len(clips)):
        fc.append(f"[{i+1}:v]{NORM}[c{i}]")
        fc.append(f"[{prev}][c{i}]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]")
        prev = f'x{i}'
        off += HOLD
    total = off + XF
    fc.append(f"[{prev}]fade=t=out:st={total-1.4:.2f}:d=1.4[v]")
    open(f'{WORK}/edu/fc.txt', 'w').write(';'.join(fc))

    print('\n영상 합성')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y'] + inputs +
                   ['-filter_complex_script', f'{WORK}/edu/fc.txt', '-map', '[v]',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                    '-pix_fmt', 'yuv420p', f'{WORK}/edu/video.mp4'], check=True)

    print('배경음악 결합')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                    '-i', f'{WORK}/edu/video.mp4', '-i', BGM,
                    '-filter_complex',
                    f"[1:a]highpass=f=50,volume=-8dB,afade=t=in:st=0:d=2,"
                    f"afade=t=out:st={total-3:.2f}:d=3[a]",
                    '-map', '0:v', '-map', '[a]', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    '-movflags', '+faststart', f'{WORK}/edu_clip.mp4'], check=True)
    print(f'완료: {WORK}/edu_clip.mp4  (약 {total:.1f}초)')


if __name__ == '__main__':
    main()
