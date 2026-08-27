# 제작 도구 · 재작업 가이드

소개영상과 웹사이트 자산을 만들 때 쓴 스크립트입니다.
영상 나레이션을 다시 녹음하거나, 로고·포스터를 수정할 때 사용합니다.

| 파일 | 역할 |
| ------ | ------ |
| `stt.py` | 영상 오디오에서 나레이션 받아쓰기 (faster-whisper) |
| `script.json` | 나레이션 문장 + 발화 시작 시각 (여기를 고쳐서 대본 수정) |
| `tts_build.py` | 문장별 TTS 합성 → 타이밍에 맞춰 배치 |
| `make_logo.py` | RWC 로고 이미지 생성 (아웃트로용 · 웹용) |
| `make_title.py` | 도입부 제안 타이틀 카드 생성 |
| `make_bgm.py` | 배경음악 합성 (현재 미사용 — 외부 음원을 씀) |
| `make_slideshow.py` | 사이트 이미지로 소개영상 재구성 |
| `make_poster.py` | 브랜드 톤 그래픽 포스터 생성 (현재 사이트 미사용) |

---

## 준비

스크립트는 **프로젝트 루트에서 실행**하며, 중간 산출물은 `temp/` 에 쌓입니다.

```bash
mkdir -p temp/tts

# 필요 패키지 (이 PC 의 base 파이썬에 설치되어 있음)
python -m pip install faster-whisper edge-tts
```

`ffmpeg` / `ffprobe` 가 PATH 에 있어야 합니다.

> **재작업 소스는 완성본입니다.**
> 촬영 원본은 보관하지 않습니다. `Docs/로보월드캠퍼스_소개영상.mp4` 를 그대로 소스로 씁니다.
> 오디오만 새로 깔면 나레이션을 다시 만들 수 있습니다.
>
> ⚠️ **완성본에는 이미 도입부 타이틀 카드(0:00~0:05)와 로고 아웃트로가 들어 있습니다.**
> 나레이션만 바꾼다면 타이틀 카드를 다시 붙이지 말고 오디오만 교체하세요.
> 타이틀 카드까지 다시 만들려면 `-ss 5.5` 로 앞부분을 잘라내고 시작합니다.

---

## 1. 나레이션 받아쓰기

```bash
ffmpeg -i "Docs/로보월드캠퍼스_소개영상.mp4" -vn -ac 1 -ar 16000 temp/audio16k.wav
python tools/stt.py                 # -> temp/transcript.json
```

`medium` 모델을 CPU(int8)로 돌립니다. 3분 37초 기준 수 분 걸립니다.
첫 실행 때 모델을 내려받습니다(약 1.5GB, `~/.cache/huggingface`).

---

## 2. 대본 수정 후 TTS 합성

`tools/script.json` 의 `text`(문장)와 `t`(발화 시작 시각, 초)를 고칩니다.

```bash
python tools/tts_build.py           # -> temp/narration.wav
```

- 목소리: `ko-KR-SunHiNeural` (여성 · Friendly/Positive), 기본 속도 −4%
- 문장이 배정된 구간을 넘치면 **발화 속도를 자동으로 올려** 맞춥니다
- 실행 로그에 문장별 `avail`(가용 시간) / `len`(합성 길이) / `rate`(속도)가 찍힙니다
- `rate` 가 `+10%` 를 넘으면 급하게 들리므로, 그 문장의 `t` 를 앞당기거나
  다음 문장의 `t` 를 늦춰 여유를 주세요

---

## 3. 로고 이미지 생성

```bash
python tools/make_logo.py           # -> temp/outro_logo.png
```

같은 스크립트를 살짝 바꿔 세 가지를 뽑습니다.

| 용도 | 방법 |
| ------ | ------ |
| 아웃트로 배경만 | 합성 부분을 `bg.save("temp/outro_bg.png")` 로 교체 |
| 아웃트로 로고만 (투명) | `out = Image.new("RGBA", (W,H), (0,0,0,0))` 로 시작 |
| 웹 로고 (투명·크롭) | 위와 같이 하고 `out.crop((330,175,950,545))` 저장 |

폰트는 Windows 기본 `malgunbd.ttf` / `malgun.ttf` 를 씁니다.

---

## 4. 영상 합성

완성본은 이미 타이틀 카드와 로고를 갖고 있으므로, 보통은 **오디오만 교체**하면 됩니다.

```bash
ffmpeg -i "Docs/로보월드캠퍼스_소개영상.mp4" -i temp/narration.wav   -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest   "Docs/로보월드캠퍼스_소개영상_new.mp4"
```

### 타이틀 카드부터 다시 만들 때

`python tools/make_title.py` 로 `temp/title_card.png` 를 만든 뒤,
완성본에서 기존 타이틀 카드(앞 5.5초)를 잘라내고 새로 붙입니다.

```bash
ffmpeg -loop 1 -t 5.5 -i temp/title_card.png   -ss 5.5 -i "Docs/로보월드캠퍼스_소개영상.mp4" -i temp/narration.wav   -filter_complex "[0:v]fps=24,scale=1280:720,setsar=1,format=yuv420p,fade=in:st=0:d=0.7,fade=out:st=4.9:d=0.6[t];[1:v]fps=24,scale=1280:720,setsar=1,format=yuv420p[m];[t][m]concat=n=2:v=1:a=0[v];[2:a]afade=t=out:st=220.0:d=2.0,aresample=48000[a]"   -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p   -c:a aac -b:a 160k -movflags +faststart -shortest   "Docs/로보월드캠퍼스_소개영상_new.mp4"
```

### 원본에서 로고 아웃트로를 새로 얹을 때 (참고)

아래는 타이틀 카드가 없던 원본 기준 명령입니다.
로고는 **211.7초부터** 덮어씌웠습니다. (야경 씬이 페이드아웃되는 시점)

```bash
ffmpeg -i "Docs/로보월드캠퍼스_소개영상.mp4" -an \
  -loop 1 -i temp/outro_bg.png -loop 1 -i temp/outro_fg.png -i temp/narration.wav \
  -filter_complex "\
[1:v]format=rgba,fade=in:st=211.7:d=0.35:alpha=1[bg];\
[0:v][bg]overlay=0:0:shortest=1:enable='gte(t,211.7)'[b];\
[2:v]format=rgba,fade=in:st=212.3:d=1.2:alpha=1[fg];\
[b][fg]overlay=0:0:shortest=1:enable='gte(t,212.3)',format=yuv420p[v];\
[3:a]afade=t=out:st=214.5:d=2.0,aresample=48000[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 160k -movflags +faststart -shortest \
  "Docs/로보월드캠퍼스_소개영상_new.mp4"
```

> 입력과 출력 파일명이 같으면 ffmpeg 가 원본을 덮어써 깨집니다.
> 새 이름으로 뽑은 뒤 바꿔치기하세요.

### 웹용 경량 인코딩

```bash
ffmpeg -i "Docs/로보월드캠퍼스_소개영상.mp4" -c:v libx264 -preset slow -crf 27 \
  -vf scale=1280:720 -c:a aac -b:a 128k -movflags +faststart \
  assets/video/intro.mp4
```

---

## 5. 페스티벌 포스터 생성

```bash
python tools/make_poster.py          # -> assets/img/robot-festival.png
```

사진을 쓰지 않고 브랜드 톤(다크 네이비 + 골드)으로 직접 그립니다.
난수 시드를 고정해 두어 몇 번을 돌려도 같은 결과가 나옵니다.

| 바꿀 곳 | 위치 |
| -------- | ------ |
| 대회명 · 부제 | `# 5. 타이틀 블록` |
| 개최지 · 공동개최 기관 | `# 6. 공동개최 배지` 앞뒤 |
| 하단 4개 프로그램 카드 | `CARDS` 리스트 |
| 배경 회로 패턴 밀도 | `# 2. 회로 패턴` 의 `range(26)` |

카드 아이콘은 `icon()` 함수에서 기하 도형으로 그립니다
(`battle` / `ai` / `expo` / `maker`).

## 5-2. 배경음악 입히기

외부에서 받은 음원을 나레이션 아래에 깝니다.
`-12dB` 가 나레이션보다 7dB 낮은 수준으로, 홍보영상 표준입니다.

```bash
ffmpeg -i "Docs/로보월드캠퍼스_소개영상.mp4" -i "받은음원.mp3"   -filter_complex "[1:a]highpass=f=50,equalizer=f=800:t=q:w=1.4:g=-2,volume=-12dB,afade=t=in:st=0:d=2.5,afade=t=out:st=219.0:d=3.5[b];[0:a][b]amix=inputs=2:duration=first:normalize=0[a]"   -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart   "Docs/로보월드캠퍼스_소개영상_new.mp4"
```

| 설정 | 이유 |
| ------ | ------ |
| `highpass=50` | 영상에서 안 들리는 저역 제거 |
| `equalizer=800 -2dB` | 나레이션 명료도 확보 |
| `volume=-12dB` | 크게 = −8dB · 은은 = −16dB |
| `normalize=0` | 없으면 amix 가 볼륨을 반으로 나눔 |

레벨 확인은 나레이션이 없는 구간(예: 107~112초)을 재 봅니다.
BGM 만 들리는 구간이 −25dB 내외면 적절합니다.

## 5-3. 소개영상 재구성 (슬라이드쇼)

사이트에 쓰는 이미지로 소개영상을 다시 만든다.
나레이션·배경음악·로고 아웃트로는 기존 영상에서 그대로 가져온다.

```bash
# 중간 파일은 반드시 구글드라이브 밖에 만든다.
# 드라이브 안에서 만들면 동기화가 끼어들어 파일이 사라진다.
SLIDE_WORK=/c/Temp/slide KB_FORCE=still python tools/make_slideshow.py

# 앞 47초만 (샘플 확인용)
SLIDE_WORK=/c/Temp/slide KB_FORCE=still python tools/make_slideshow.py 47
```

컷 목록은 스크립트 상단 `CUTS` 에 있다. `(시작초, 파일, 움직임)` 형식이며
움직임 자리에 `video` 를 쓰면 이미지 대신 영상 클립을 넣고 구간 길이에
맞춰 속도를 조절한다.

### 움직임 설정

| 환경변수 | 뜻 |
| ---------- | ---- |
| `KB_FORCE=still` | 움직임 없음 (현재 설정) |
| `KB_FORCE=in` + `KB_ZOOM=1.05` | 아주 미세한 확대 |
| 지정 안 함 | `CUTS` 의 방향을 각각 사용 |

**켄번스는 과하면 멀미가 난다.** 컷마다 방향이 다르면 크로스페이드
구간에서 두 이미지가 서로 다른 방향으로 움직여 특히 어지럽다.
그래서 현재는 움직임을 끄고 크로스페이드만 쓴다.

### 알아 둘 것

- `crop` 은 정수 픽셀로만 움직인다. 1280 폭에서 느리게 팬하면 프레임당
  1~2 픽셀씩 튀어 떨린다. 2배 해상도에서 잘라 축소하면 해결된다.
- JPEG 은 풀레인지(`yuvj420p`)로 디코딩된다. `xfade` 는 두 입력의 픽셀
  포맷이 같아야 해서 `scale=in_range=full:out_range=tv` 로 맞춰야 한다.
- `zoompan` 은 프레임마다 전체를 다시 계산해 `crop` 이동보다 18배 느리다.

## 6. 웹사이트 이미지 추출

영상 프레임에서 뽑되, **화면에 박힌 자막을 피해야** 합니다.
자막은 씬 시작과 거의 동시에 뜨므로 깨끗한 프레임이 없습니다.
자막 윗부분만 16:9 로 크롭해서 씁니다.

```python
im.crop((200, 0, 1080, 495))    # 원본 1280x720 기준 · 자막 상단은 y=510부터
```

자막이 없는 씬(조감도 · 건물 · 야경 · 광장 등)은 원본 그대로 씁니다.

---

## 7. 결과 검증

수정한 영상은 **오디오를 다시 받아써서** 확인합니다.

```bash
ffmpeg -i "Docs/로보월드캠퍼스_소개영상.mp4" -vn -ac 1 -ar 16000 temp/verify16k.wav
# stt.py 의 입력 경로를 temp/verify16k.wav 로 바꿔 실행
```

로고 구간에 원본 로고가 비치는지는 밝기를 크게 올려 확인합니다.

```bash
ffmpeg -ss 211.5 -i "Docs/로보월드캠퍼스_소개영상.mp4" -frames:v 1 \
  -vf "eq=brightness=0.35:contrast=2.2" temp/check.jpg
```

웹사이트 렌더링은 headless Chrome 으로 확인합니다.
**창 최소 폭이 500px** 이라 그보다 좁게 지정해도 500px 로 렌더링되니 주의하세요.

```bash
chrome --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1440,12000 --virtual-time-budget=9000 \
  --screenshot=temp/full.png "file:///<절대경로>/index.html"
```

`.hero` 가 `min-height:100svh` 라 창 높이를 크게 주면 히어로도 같이 늘어납니다.
전체 캡처를 할 때는 `.hero{min-height:840px}` 를 임시로 덮어쓴 사본을 만들어 찍으세요.
