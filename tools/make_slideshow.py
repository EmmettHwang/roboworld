# -*- coding: utf-8 -*-
"""새 이미지로 소개영상 슬라이드쇼 제작

나레이션 타이밍에 맞춰 이미지를 배치하고 느린 팬·줌(켄번스)을 준다.
컷을 만든 뒤 크로스페이드로 이어 붙이고, 나레이션과 배경음악을 얹는다.

  python tools/make_slideshow.py            전체 (3분 42초)
  python tools/make_slideshow.py 52         앞 52초만 (샘플)

중간 파일은 SLIDE_WORK 환경변수 경로에 만든다.
구글드라이브 안에서 만들면 동기화가 끼어들어 파일이 사라지므로
반드시 로컬 임시 폴더를 지정한다.

켄번스는 zoompan 대신 crop 이동으로 구현했다. zoompan 은 프레임마다
전체를 다시 계산해 18배 느리다.
"""
import os, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

W, H, FPS = 1280, 720, 30
XF = 1.0                                  # 크로스페이드 길이
WORK = os.environ.get('SLIDE_WORK', 'temp')
VIDEO = 'Docs/로보월드캠퍼스_소개영상.mp4'          # 나레이션 + BGM 을 여기서 가져온다
TITLE = f'{WORK}/title_card.png'

# (시작초, 이미지, 움직임)  움직임: in / out / left / right / up / down
CUTS = [
    (  5.5, 'night-finale.jpg',        'in'),
    ( 10.5, 'campus-aerial-dome.jpg',  'in'),
    ( 17.8, 'exhibit-corridor.jpg',    'right'),
    ( 23.9, 'building-dusk.jpg',       'in'),
    ( 26.8, 'maker-class.jpg',         'left'),
    ( 33.5, 'edu-maker.jpg',           'in'),
    ( 40.7, 'campus-aerial-dome.jpg',  'out'),
    ( 46.5, 'fest-main.jpg',           'up'),
    # 교육 구간은 실제 영상. 국어 -> 영어 -> 수학 -> 메이커 순서가
    # 나레이션 흐름과 같아 그대로 얹는다. 20초 영상을 구간 길이에 맞춰 늘린다.
    ( 52.6, 'Docs/새로제작이미지/로봇대회/교육영상.mp4', 'video'),
    ( 82.8, 'senior-choir.jpg',        'left'),
    ( 86.9, 'senior-painting.jpg',     'in'),
    ( 91.0, 'wellness-skincare.jpg',   'right'),
    ( 95.3, 'senior-health.jpg',       'in'),
    (101.0, 'youth-mentoring.jpg',     'left'),
    (106.0, 'group-workshop.jpg',      'in'),
    (111.0, 'sports-badminton.jpg',    'right'),
    (114.5, 'pilates-yoga.jpg',        'in'),
    (117.7, 'hall-ai-robot.jpg',       'in'),
    (126.0, 'hall-space.jpg',          'out'),
    (136.5, 'hall-energy.jpg',         'in'),
    (145.0, 'fest-maker.jpg',          'left'),
    (150.5, 'museum-ocean.jpg',        'in'),
    (158.0, 'museum-dino.jpg',         'right'),
    (165.1, 'fest-main.jpg',           'in'),
    (174.5, 'local-street.jpg',        'left'),
    (179.0, 'local-cafe.jpg',          'in'),
    (183.3, 'jobs-event.jpg',          'right'),
    (188.0, 'jobs-ai-robot.jpg',       'in'),
    (193.0, 'campus-aerial-dome.jpg',  'in'),
    (200.0, 'fest-battle.jpg',         'out'),
    (208.5, 'night-finale.jpg',        'in'),
]
OUTRO = 217.0        # 로고 아웃트로 시작
TOTAL = 222.5


def kenburns(mode, dur):
    """켄번스 팬.

    crop 은 정수 픽셀로만 움직인다. 1280 폭에서 느리게 팬하면 프레임당
    1~2 픽셀씩 튀어 계단처럼 떨린다. 그래서 2배 해상도에서 잘라낸 뒤
    축소해 사실상 0.5픽셀 단위로 움직이게 한다.

    움직임이 과하면 멀미가 난다. 특히 컷마다 방향이 바뀌면 크로스페이드
    구간에서 두 이미지가 서로 다른 방향으로 움직여 어지럽다. 그래서
    기본값은 아주 미세한 확대 하나로 통일했다.

    KB_ZOOM   확대율 (1.0 이면 정지, 기본 1.05)
    KB_FORCE  'in' 이면 방향을 확대로 통일, 'still' 이면 완전 정지
    """
    Z = float(os.environ.get('KB_ZOOM', '1.05'))
    FORCE = os.environ.get('KB_FORCE', 'in')
    S = 2
    if FORCE == 'still' or Z <= 1.001:
        return (f"scale={W*S}:{H*S}:force_original_aspect_ratio=increase:flags=lanczos,"
                f"crop={W*S}:{H*S},scale={W}:{H}:flags=lanczos,"
                f"scale=in_range=full:out_range=tv,format=yuv420p,setrange=tv,"
                f"setsar=1,fps={FPS}")
    if FORCE in ('in', 'out', 'left', 'right', 'up', 'down'):
        mode = FORCE

    bw, bh = int(W*Z*S)//2*2, int(H*Z*S)//2*2
    cw, ch = W*S, H*S
    mx, my = bw - cw, bh - ch
    e = f"(1-cos(PI*min(t/{dur},1)))/2"          # ease-in-out
    r = f"(1-{e})"
    pos = {
        'in':    (f"({mx})*{e}",  f"({my})*{e}"),
        'out':   (f"({mx})*{r}",  f"({my})*{r}"),
        'left':  (f"({mx})*{r}",  f"({my})/2"),
        'right': (f"({mx})*{e}",  f"({my})/2"),
        'up':    (f"({mx})/2",    f"({my})*{r}"),
        'down':  (f"({mx})/2",    f"({my})*{e}"),
    }[mode]
    return (f"scale={bw}:{bh}:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop={bw}:{bh},crop={cw}:{ch}:'{pos[0]}':'{pos[1]}',"
            f"scale={W}:{H}:flags=lanczos,"
            f"scale=in_range=full:out_range=tv,format=yuv420p,setrange=tv,"
            f"setsar=1,fps={FPS}")


def build_clips(limit):
    os.makedirs(f'{WORK}/clips', exist_ok=True)
    clips, starts = [], []
    for i, (t0, src, mode) in enumerate(CUTS):
        if limit and t0 >= limit:
            break
        nxt = CUTS[i + 1][0] if i + 1 < len(CUTS) else OUTRO
        if limit:
            nxt = min(nxt, limit)
        dur = round(nxt - t0 + XF, 3)
        p = src if mode == 'video' else f'assets/img/{src}'
        if not os.path.exists(p):
            print(f'  건너뜀(파일 없음): {src}')
            continue
        out = f'{WORK}/clips/c{i:02d}.mp4'

        if mode == 'video':
            # 원본 길이를 구해 구간에 맞게 속도를 조절한다.
            r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                'format=duration', '-of', 'default=nw=1:nk=1', p],
                               capture_output=True, text=True)
            vlen = float(r.stdout.strip())
            ratio = dur / vlen                      # 1보다 크면 느리게
            vf = (f"setpts={ratio:.4f}*PTS,scale={W}:{H}:force_original_aspect_ratio=increase,"
                  f"crop={W}:{H},scale=in_range=full:out_range=tv,format=yuv420p,"
                  f"setrange=tv,setsar=1,fps={FPS}")
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                            '-i', p, '-an', '-vf', vf, '-t', str(dur),
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                            '-pix_fmt', 'yuv420p', out], check=True)
            print(f'  {t0:6.1f}s  [영상] {os.path.basename(src):22} {vlen:.1f}s -> {dur:.1f}s (x{1/ratio:.2f})')
        else:
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                            '-loop', '1', '-t', str(dur), '-i', p,
                            '-vf', kenburns(mode, dur),
                            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18',
                            '-pix_fmt', 'yuv420p', out], check=True)
            print(f'  {t0:6.1f}s  {src:26} {mode:6} {dur:5.2f}s')

        clips.append(out); starts.append(t0)
    return clips, starts


def main():
    limit = float(sys.argv[1]) if len(sys.argv) > 1 else None
    print('컷 생성')
    clips, starts = build_clips(limit)

    # ── 타이틀 카드 + 컷들을 크로스페이드로 연결 ──
    inputs = ['-loop', '1', '-t', str(starts[0] + XF), '-i', TITLE]
    for c in clips:
        inputs += ['-i', c]

    # JPEG 은 풀레인지(yuvj420p)로 나온다. xfade 는 두 입력의 픽셀 포맷이
    # 정확히 같아야 해서, 색범위를 TV 로 맞춰 주지 않으면 -22 로 거부한다.
    NORM = f"scale=in_range=full:out_range=tv,format=yuv420p,setrange=tv,setsar=1,fps={FPS}"
    fc = [f"[0:v]scale={W}:{H},setsar=1,fps={FPS},format=yuv420p,setrange=tv,"
          f"fade=t=in:st=0:d=0.7[v0]"]
    prev = 'v0'
    for i in range(len(clips)):
        fc.append(f"[{i+1}:v]{NORM}[c{i}]")
        fc.append(f"[{prev}][c{i}]xfade=transition=fade:duration={XF}"
                  f":offset={starts[i]:.3f}[x{i}]")
        prev = f'x{i}'
    open(f'{WORK}/fc.txt', 'w').write(';'.join(fc))

    print('\n영상 합성')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y'] + inputs +
                   ['-filter_complex_script', f'{WORK}/fc.txt', '-map', f'[{prev}]',
                    '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
                    '-pix_fmt', 'yuv420p', f'{WORK}/video_only.mp4'], check=True)

    # ── 로고 아웃트로 이어 붙이기 (전체 제작일 때만) ──
    src = f'{WORK}/video_only.mp4'
    if not limit:
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                        '-i', src, '-ss', str(OUTRO), '-i', VIDEO,
                        '-filter_complex',
                        f"[0:v]format=yuv420p,setrange=tv[a];"
                        f"[1:v]scale={W}:{H},setsar=1,fps={FPS},format=yuv420p,setrange=tv[b];"
                        f"[a][b]concat=n=2:v=1:a=0[v]",
                        '-map', '[v]', '-c:v', 'libx264', '-preset', 'medium',
                        '-crf', '20', '-pix_fmt', 'yuv420p',
                        f'{WORK}/with_outro.mp4'], check=True)
        src = f'{WORK}/with_outro.mp4'

    # ── 기존 영상의 오디오(나레이션 + BGM) 입히기 ──
    print('오디오 결합')
    out = f'{WORK}/slideshow.mp4'
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                    '-i', src, '-i', VIDEO,
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest',
                    '-movflags', '+faststart', out], check=True)
    print(f'완료: {out}')


if __name__ == '__main__':
    main()
