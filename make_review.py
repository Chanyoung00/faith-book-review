#!/usr/bin/env python3
"""신앙 서적 리뷰 영상 생성기 (16:9, 한/영)
사용: python3 make_review.py script.json out.mp4 [--frames]
- 한국어·영어 모두 \\n 으로 직접 지정한 의미 단위로만 줄을 나눔(자동 줄바꿈은 넘칠 때만, 단어 단위).
- '_' 는 끊으면 안 되는 띄어쓰기(화면에는 공백으로 보임).
- 장면의 "photo"(로컬 경로)가 있으면 왼쪽 사진 패널, 없으면 가운데 정렬 디자인 카드.
"""
import json, os, subprocess, sys, wave, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, XF = 2560, 1440, 30, 0.8  # 2K(QHD) 30fps, 장면은 0.8초 크로스페이드
S = W / 1920  # 1920 기준 좌표·글자 크기를 2K로 키우는 배율
def K(v): return int(round(v * S))
FD = "/usr/share/fonts/opentype/noto/"
def F(name, size): return ImageFont.truetype(FD + name, K(size), index=1)  # index 1 = KR
GOLD, CREAM, MUTED, ENC = (150, 196, 228), (244, 241, 234), (160, 172, 186), (196, 206, 218)  # GOLD=포인트색(하늘빛)
PW = K(820)  # 사진 패널 너비

# ---------- 줄바꿈 ----------
def _words(p): return [w.replace("_", " ") for w in p.split(" ") if w != ""]
def _greedy(d, words, f, maxw):
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines
def _balanced(d, p, f, maxw):
    words = _words(p); n = len(_greedy(d, words, f, maxw)); lo, hi = 1, maxw
    while lo < hi:
        mid = (lo + hi) // 2
        if len(_greedy(d, words, f, mid)) <= n: hi = mid
        else: lo = mid + 1
    return _greedy(d, words, f, lo)
def fit(d, text, name, size, maxw, minsize):
    """\\n 단위 줄 유지. 넘치면 글씨를 줄이고, 최소 크기에서도 넘칠 때만 단어 단위로 고르게 나눔."""
    paras = text.split("\n")
    while size > minsize:
        f = F(name, size)
        if all(d.textlength(p.replace("_", " "), font=f) <= maxw for p in paras): break
        size -= 2
    f = F(name, size)
    lines = []
    for p in paras:
        if d.textlength(p.replace("_", " "), font=f) <= maxw: lines.append(p.replace("_", " "))
        else: lines += _balanced(d, p, f, maxw)
    return lines, f

# ---------- 배경 ----------
def background():
    y = np.linspace(0, 1, H)[:, None]; x = np.linspace(0, 1, W)[None, :]
    top, bot = np.array([18, 30, 48]), np.array([7, 11, 20])
    img = top * (1 - y[..., None]) + bot * y[..., None]
    glow = np.exp(-(((x - .62) / .45) ** 2 + ((y - .35) / .45) ** 2))[..., None]
    img = img + glow * np.array([16, 34, 52])
    vig = 1 - 0.40 * (((x - .5) * 1.3) ** 2 + ((y - .5) * 1.5) ** 2)[..., None]
    img = np.clip(img * vig, 0, 255)
    return Image.fromarray(img.astype(np.uint8)).convert("RGBA")

def photo_panel(base, path):
    ph = Image.open(path).convert("RGB")
    r = max(PW / ph.width, H / ph.height); ph = ph.resize((int(ph.width * r + 1), int(ph.height * r + 1)), Image.LANCZOS)
    l, t = (ph.width - PW) // 2, (ph.height - H) // 2; ph = ph.crop((l, t, l + PW, t + H))
    a = np.asarray(ph).astype(np.float32) * 0.86  # 살짝 어둡게
    xs = np.linspace(0, 1, PW)[None, :, None]
    fade = np.clip((1 - xs) / 0.28, 0, 1) ** 1.2  # 오른쪽 끝을 배경으로 부드럽게
    bg = np.asarray(base.convert("RGB")).astype(np.float32)[:, :PW]
    a = a * fade + bg * (1 - fade)
    ys = np.linspace(0, 1, H)[:, None, None]  # 위·아래 글씨(머리말·사진 출처)가 잘 보이도록 어둡게
    a = a * (1 - 0.65 * np.clip((0.16 - ys) / 0.16, 0, 1)) * (1 - 0.6 * np.clip((ys - 0.88) / 0.12, 0, 1))
    base.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8)), (0, 0))

def book_card(base, d, meta):
    """책 표지를 따라 그리지 않은, 이 채널만의 타이포그래피 카드."""
    bx, by, bw, bh = K(170), K(170), K(480), K(700)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.rectangle([bx + K(18), by + K(22), bx + bw + K(18), by + bh + K(22)], fill=(0, 0, 0, 170))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(K(18))))
    d.rectangle([bx, by, bx + bw, by + bh], fill=(26, 44, 70))
    d.rectangle([bx, by, bx + K(22), by + bh], fill=(18, 32, 52))
    d.rectangle([bx + K(46), by + K(34), bx + bw - K(24), by + bh - K(34)], outline=GOLD, width=K(3))
    d.rectangle([bx + K(58), by + K(46), bx + bw - K(36), by + bh - K(46)], outline=(95, 130, 160), width=K(1))
    cx = bx + K(22) + (bw - K(22)) // 2
    tl, tf = fit(d, meta["book_ko"], "NotoSerifCJK-Black.ttc", 74, bw - K(140), 40)
    y = by + K(200) - len(tl) * tf.size * 0.6
    for ln in tl: d.text((cx, y), ln, font=tf, fill=CREAM, anchor="mm"); y += int(tf.size * 1.25)
    d.line([(cx - K(40), y + K(10)), (cx + K(40), y + K(10))], fill=GOLD, width=K(2))
    el, ef = fit(d, meta["book_en"], "NotoSerifCJK-Regular.ttc", 30, bw - K(140), 22)
    y += K(60)
    for ln in el: d.text((cx, y), ln, font=ef, fill=ENC, anchor="mm"); y += int(ef.size * 1.3)
    d.text((cx, by + bh - K(130)), meta["author_ko"], font=F("NotoSansCJK-Bold.ttc", 32), fill=GOLD, anchor="mm")
    d.text((cx, by + bh - K(88)), meta["author_en"], font=F("NotoSerifCJK-Regular.ttc", 24), fill=MUTED, anchor="mm")

def frame(sc, meta, idx):
    im = background(); d = ImageDraw.Draw(im)
    has_photo = bool(sc.get("photo")) and os.path.exists(sc["photo"])
    if sc.get("card"): book_card(im, d, meta); x0, x1 = PW + K(60), W - K(110)
    elif has_photo: photo_panel(im, sc["photo"]); d = ImageDraw.Draw(im); x0, x1 = PW + K(60), W - K(110)
    else: x0, x1 = K(230), W - K(230)
    tx = Image.new("RGBA", (W, H), (0, 0, 0, 0)); t = ImageDraw.Draw(tx)
    t.text((K(80), K(62)), f"신앙 서적 리뷰 #{meta['no']}  ·  Faith Book Review", font=F("NotoSansCJK-Medium.ttc", 28), fill=MUTED, anchor="lm")
    t.text((W - K(80), K(62)), f"{meta['book_ko']}  |  {meta['book_en']}", font=F("NotoSansCJK-Medium.ttc", 26), fill=(130, 145, 162), anchor="rm")
    if has_photo and sc.get("photo_credit"):
        t.text((K(40), H - K(40)), f"Photo: {sc['photo_credit']} / Unsplash", font=F("NotoSansCJK-Regular.ttc", 20), fill=(200, 195, 185), anchor="lm")
    cx, mw = (x0 + x1) // 2, x1 - x0
    blocks = []  # (lines, font, color, gap_after, line_ratio)
    if sc.get("label"):
        lab = sc["label"] + (f"   {sc['label_en']}" if sc.get("label_en") else "")
        blocks.append(([lab], F("NotoSansCJK-Bold.ttc", 38), GOLD, 54, 1.4))
    if sc.get("title"):
        l, f = fit(t, sc["title"], "NotoSerifCJK-Black.ttc", 104, mw, 64); blocks.append((l, f, CREAM, 26, 1.28))
    if sc.get("en"):
        l, f = fit(t, sc["en"], "NotoSerifCJK-Regular.ttc", 40, mw, 30); blocks.append((l, f, MUTED, 50, 1.4))
    if sc.get("body"):
        l, f = fit(t, sc["body"], "NotoSerifCJK-Bold.ttc" if sc.get("quote") else "NotoSansCJK-Bold.ttc", 60, mw, 40)
        blocks.append((l, f, CREAM, 40, 1.5))
    if sc.get("body_en"):
        l, f = fit(t, sc["body_en"], "NotoSerifCJK-Regular.ttc", 36, mw, 28); blocks.append((l, f, ENC, 30, 1.45))
    if sc.get("ref"): blocks.append(([sc["ref"]], F("NotoSansCJK-Bold.ttc", 30), GOLD, 0, 1.4))
    if sc.get("sub"):
        l, f = fit(t, sc["sub"], "NotoSansCJK-Medium.ttc", 44, mw, 32); blocks.append((l, f, CREAM, 20, 1.5))
    if sc.get("sub_en"):
        l, f = fit(t, sc["sub_en"], "NotoSerifCJK-Regular.ttc", 34, mw, 26); blocks.append((l, f, MUTED, 0, 1.45))
    lh = lambda f, r: int(f.size * r)
    total = sum(len(l) * lh(f, r) + K(g) for l, f, c, g, r in blocks)
    y = (H - total) // 2 + K(10)
    for i, (lines, f, c, g, r) in enumerate(blocks):
        for ln in lines:
            t.text((cx, y + lh(f, r) // 2), ln, font=f, fill=c, anchor="mm"); y += lh(f, r)
        if i == 0 and sc.get("label"):
            t.line([(cx - K(36), y + K(8)), (cx + K(36), y + K(8))], fill=GOLD, width=K(3))
        y += K(g)
    shadow = tx.filter(ImageFilter.GaussianBlur(K(8))); sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(shadow.getchannel("A").point(lambda a: a * 0.75))
    im.alpha_composite(sh); im.alpha_composite(tx)
    return im.convert("RGB")

# ---------- 음악: 피아노 찬송가 편곡 (저작권이 끝난 옛 찬송가 선율) ----------
# JSON "music": {"hymn": 아래 이름, "style": "hymn"|"arpeggio"|"ballad", "seed": 회차}
# 선율: (midi, 박) / 코드: 각 마디·박에서 시작하는 (박 위치, 코드 이름)
CH = {"C": [0, 4, 7], "D": [2, 6, 9], "E": [4, 8, 11], "F": [5, 9, 12], "G": [7, 11, 14], "A": [9, 13, 16], "B": [11, 15, 18],
      "Am": [9, 12, 16], "Em": [4, 7, 11], "Dm": [2, 5, 9], "Bm": [11, 14, 18], "F#m": [6, 9, 13]}
HYMNS = {
    # 나 같은 죄인 살리신 (Amazing Grace, NEW BRITAIN) — G장조 3/4
    "amazing_grace": dict(title="나 같은 죄인 살리신 (Amazing Grace)", key=0, bpm=(60, 72), mel=[
        (62, 1), (67, 2), (71, .5), (67, .5), (71, 2), (69, 1), (67, 2), (64, 1), (62, 2), (62, 1),
        (67, 2), (71, .5), (67, .5), (71, 2), (69, 1), (74, 2), (71, 1), (74, 2), (71, .5), (67, .5),
        (71, 2), (69, 1), (67, 2), (64, 1), (62, 2), (62, 1), (67, 2), (71, .5), (67, .5), (71, 2), (69, 1), (67, 2)],
        ch=[(0, "G"), (1, "G"), (4, "G"), (6, "D"), (7, "C"), (10, "G"), (13, "G"), (16, "G"), (18, "D"), (19, "G"),
            (22, "G"), (25, "G"), (27, "D"), (28, "C"), (31, "G"), (34, "G"), (37, "G"), (39, "D"), (40, "G")]),
    # 기뻐하며 경배하세 (Joyful, Joyful, We Adore Thee, HYMN TO JOY) — C장조로 적고 D장조로 연주 4/4
    "joyful": dict(title="기뻐하며 경배하세 (Joyful, Joyful)", key=2, bpm=(72, 84), mel=[
        (64, 1), (64, 1), (65, 1), (67, 1), (67, 1), (65, 1), (64, 1), (62, 1), (60, 1), (60, 1), (62, 1), (64, 1), (64, 1.5), (62, .5), (62, 2),
        (64, 1), (64, 1), (65, 1), (67, 1), (67, 1), (65, 1), (64, 1), (62, 1), (60, 1), (60, 1), (62, 1), (64, 1), (62, 1.5), (60, .5), (60, 2),
        (62, 1), (62, 1), (64, 1), (60, 1), (62, 1), (64, .5), (65, .5), (64, 1), (60, 1), (62, 1), (64, .5), (65, .5), (64, 1), (62, 1),
        (60, 1), (62, 1), (55, 2),
        (64, 1), (64, 1), (65, 1), (67, 1), (67, 1), (65, 1), (64, 1), (62, 1), (60, 1), (60, 1), (62, 1), (64, 1), (62, 1.5), (60, .5), (60, 2)],
        ch=[(0, "C"), (4, "G"), (8, "C"), (12, "C"), (14, "G"), (16, "C"), (20, "G"), (24, "C"), (28, "G"), (30, "C"),
            (32, "G"), (34, "C"), (36, "G"), (38, "C"), (40, "G"), (44, "C"), (46, "G"),
            (48, "C"), (52, "G"), (56, "C"), (60, "G"), (62, "C")]),
    # 만복의 근원 하나님 (Old Hundredth, Doxology) — G장조
    "doxology": dict(title="만복의 근원 하나님 (Old Hundredth)", key=0, bpm=(58, 70), mel=[
        (67, 2), (67, 1), (66, 1), (64, 1), (62, 1), (67, 1), (69, 1), (71, 3),
        (71, 2), (71, 1), (71, 1), (69, 1), (67, 1), (72, 1), (71, 1), (69, 3),
        (67, 2), (69, 1), (71, 1), (69, 1), (67, 1), (64, 1), (66, 1), (67, 3),
        (74, 2), (71, 1), (67, 1), (69, 1), (72, 1), (71, 1), (69, 1), (67, 3)],
        ch=[(0, "G"), (3, "D"), (4, "C"), (5, "G"), (6, "Em"), (7, "D"), (8, "G"),
            (11, "G"), (13, "Em"), (14, "G"), (15, "D"), (16, "Em"), (17, "C"), (18, "G"), (19, "D"),
            (22, "G"), (24, "D"), (25, "G"), (26, "D"), (27, "Em"), (28, "C"), (29, "D"), (30, "G"),
            (33, "G"), (35, "Em"), (36, "C"), (37, "D"), (38, "Am"), (39, "G"), (40, "D"), (41, "G")]),
    # 예수 사랑하심은 (Jesus Loves Me, BRADBURY) — C장조 4/4, 절 선율
    "jesus_loves_me": dict(title="예수 사랑하심은 (Jesus Loves Me)", key=0, bpm=(60, 72), mel=[
        (67, 1), (64, 1), (64, 1), (62, 1), (64, 1), (67, 1), (67, 2),
        (69, 1), (69, 1), (72, 1), (69, 1), (69, 1), (67, 1), (67, 2),
        (67, 1), (64, 1), (64, 1), (62, 1), (64, 1), (67, 1), (67, 2),
        (69, 1), (69, 1), (67, 1), (60, 1), (64, 1), (62, 1), (60, 2)],
        ch=[(0, "C"), (8, "F"), (10, "C"), (12, "C"), (16, "C"), (20, "C"), (24, "F"), (26, "C"), (28, "G"), (30, "C")]),
    # 고요한 밤 거룩한 밤 (Silent Night, STILLE NACHT) — C장조 6/8 (박 단위: 4분음표)
    "silent_night": dict(title="고요한 밤 거룩한 밤 (Silent Night)", key=0, bpm=(60, 72), mel=[
        (67, 1.5), (69, .5), (67, 1), (64, 3), (67, 1.5), (69, .5), (67, 1), (64, 3),
        (74, 2), (74, 1), (71, 3), (72, 2), (72, 1), (67, 3),
        (69, 2), (69, 1), (72, 1.5), (71, .5), (69, 1), (67, 1.5), (69, .5), (67, 1), (64, 3),
        (69, 2), (69, 1), (72, 1.5), (71, .5), (69, 1), (67, 1.5), (69, .5), (67, 1), (64, 3),
        (74, 2), (74, 1), (77, 1.5), (74, .5), (71, 1), (72, 3), (76, 3),
        (72, 1.5), (67, .5), (64, 1), (67, 1.5), (65, .5), (62, 1), (60, 6)],
        ch=[(0, "C"), (12, "G"), (18, "C"), (24, "F"), (30, "C"), (36, "F"), (42, "C"), (48, "G"), (54, "C"),
            (60, "C"), (63, "G"), (66, "C")]),
}

def music(path, dur, cfg=None, sr=48000):
    """낮은 음역 오르골 + 부드러운 저음 패드. 고음·날카로운 배음·잡음 없이 차분하고 묵직하게."""
    cfg = cfg or {}; rng = np.random.default_rng(int(cfg.get("seed", 1)) * 7919 + 7)
    hy = HYMNS.get(cfg.get("hymn"), HYMNS["amazing_grace"])
    key = hy["key"] + int(cfg.get("transpose", 0)) - 12          # 한 옥타브 낮게
    mel, chs = hy["mel"], hy["ch"]; L = sum(d for _, d in mel)
    best = None
    for k in range(1, 12):                                       # 느린 빠르기(50~62)로, 끝이 곡의 마침에 오도록
        bpm = (k * L + 4) * 60 / (dur - 3)
        if 48 <= bpm <= 62: best = (k, bpm); break
    if not best: k = max(1, round((dur - 3) * 55 / 60 / L)); best = (k, (k * L + 4) * 60 / (dur - 3))
    verses, bpm = best; spb = 60 / bpm
    n = int(sr * (dur + 1)); out = np.zeros(n)
    hzm = lambda m: 440 * 2 ** ((m + key - 69) / 12)
    def put(i0, y):
        if i0 >= n: return
        y = y[: n - i0]; out[i0:i0 + len(y)] += y
    def musicbox(m, start, vel):      # 오르골: 맑은 기본음 + 약한 2·3배음, 천천히 사라짐
        f = hzm(m); tt = np.arange(int(4.5 * sr)) / sr
        y = (np.sin(2*np.pi*f*tt) + 0.18*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*2.5) + 0.05*np.sin(2*np.pi*3*f*tt)*np.exp(-tt*4))
        y *= np.minimum(1, tt / 0.008) * np.exp(-tt * 0.9) * np.minimum(1, (4.5 - tt) / 0.5)
        put(int(start * sr), 0.22 * vel * y)
    def pad(ms, start, length, vel):  # 저음 패드: 부드럽게 들어왔다 나가는 사인파 화음
        tt = np.arange(int((length + 1.5) * sr)) / sr
        env = np.sin(np.pi * np.clip(tt / (length + 1.5), 0, 1)) ** 2
        y = sum(np.sin(2*np.pi*hzm(m)*tt) + 0.12*np.sin(2*np.pi*2*hzm(m)*tt) for m in ms)
        put(int((start - 0.6) * sr), 0.05 * vel * env * y)
    pts = [p for p, _ in chs] + [L]; spans = [(pts[i], pts[i + 1], chs[i][1]) for i in range(len(chs))]
    t0 = 1.5
    for v in range(verses):
        vs = t0 + v * L * spb; b = 0.0
        for m, d in mel:
            musicbox(m, vs + b * spb + float(rng.normal(0, 0.006)), 0.9 if v % 2 == 0 else 0.75); b += d
        for s, e, name in spans:
            r = CH[name][0] % 12
            pad([36 + r, 43 + r, 48 + CH[name][1] % 12], vs + s * spb, (e - s) * spb, 1.0)
            if v % 2 == 1:                       # 둘째 절마다 낮은 오르골 분산화음을 살짝
                for j, x in enumerate([48 + r, 55 + r, 60 + CH[name][1] % 12]):
                    if j * spb < (e - s) * spb: musicbox(x, vs + s * spb + j * spb, 0.35)
    end = t0 + verses * L * spb; fc = CH[chs[-1][1]]; r = fc[0] % 12
    pad([36 + r, 43 + r, 48 + fc[1] % 12], end, 3.5, 1.0); musicbox(60 + r, end, 0.7)
    # 부드러운 잔향(어두운 홀) — 고음을 깎아 따뜻하게
    ir_n = int(1.8 * sr); it = np.arange(ir_n) / sr
    ir = np.random.default_rng(5).normal(0, 1, ir_n) * np.exp(-it / 0.45)
    N = n + ir_n; fr = np.fft.rfftfreq(N, 1 / sr)
    IR = np.fft.rfft(ir, N) / np.sqrt(1 + (fr / 1800) ** 4)
    wet = np.fft.irfft(np.fft.rfft(out, N) * IR, N)[:n]
    mix = out / (np.max(np.abs(out)) + 1e-9) * 0.85 + wet / (np.max(np.abs(wet)) + 1e-9) * 0.18
    F_ = np.fft.rfft(mix); fr = np.fft.rfftfreq(n, 1 / sr)
    mix = np.fft.irfft(F_ / np.sqrt(1 + (fr / 4000) ** 4) * (1 - np.exp(-fr / 30)), n)   # 날카로운 고음 제거
    mix = mix[: int(sr * dur)]; t = np.arange(len(mix)) / sr
    mix *= np.minimum(1, np.minimum(t / 1.5, (dur - t) / 3.0)).clip(0, 1) ** 1.5
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.5
    st = np.stack([mix, np.roll(mix, 300) * 0.97], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((st * 32767).astype(np.int16).tobytes())
    return hy["title"]

def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def main(js, out, frames_only=False):
    meta = json.load(open(js, encoding="utf-8")); wd = os.path.splitext(out)[0] + "_work"; os.makedirs(wd, exist_ok=True)
    scenes = meta["scenes"]; durs = [float(s.get("dur", 10)) for s in scenes]
    imgs = []
    for i, sc in enumerate(scenes):  # 사진 내려받기 (실패하면 사진 없이 디자인 카드로)
        if sc.get("photo_url") and not (sc.get("photo") and os.path.exists(sc["photo"])):
            p = f"{wd}/photo{i:02d}.jpg"; u = sc["photo_url"] + ("&" if "?" in sc["photo_url"] else "?") + "w=1400&fit=max"
            r = subprocess.run(["curl", "-sSfL", "--max-time", "40", "-o", p, u], capture_output=True)
            try:
                if r.returncode == 0: Image.open(p).verify(); sc["photo"] = p
                else: print(f"[사진 실패] 장면 {i}: {r.stderr.decode()[:120]}", file=sys.stderr)
            except Exception as e: print(f"[사진 오류] 장면 {i}: {e}", file=sys.stderr)
    for i, sc in enumerate(scenes):
        p = f"{wd}/f{i:02d}.png"; frame(sc, meta, i).save(p); imgs.append(p)
        if frames_only: Image.open(p).save(f"{wd}/preview{i:02d}.jpg", quality=85)
    if frames_only: return
    T = sum(durs) - XF * (len(durs) - 1)
    music(f"{wd}/m.wav", T, meta.get("music"))
    cmd = ["ffmpeg", "-y"]
    for p, D in zip(imgs, durs): cmd += ["-loop", "1", "-framerate", str(FPS), "-t", str(D), "-i", p]
    fc, prev, off = [], "[0:v]", 0.0
    for i in range(1, len(imgs)):   # 장면 사이를 부드럽게 겹치며 넘어감
        off += durs[i - 1] - XF
        fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[x{i}]"); prev = f"[x{i}]"
    fc.append(f"{prev}fade=in:st=0:d=1.2,fade=out:st={T-1.8:.3f}:d=1.8,format=yuv420p[v]")
    # 유튜브 권장 업로드 설정: H.264 High, 30fps, 닫힌 GOP(15), AAC-LC 384kbps 48kHz 스테레오.
    # GitHub 파일 한도(100MB) 안에 들도록 영상 비트레이트를 계산(최대 16Mbps)해 2패스로 인코딩.
    vb = int(min(16000, (92_000_000 * 8 / T) / 1000 - 400))
    common = ["-filter_complex", ";".join(fc), "-map", "[v]", "-r", str(FPS), "-c:v", "libx264", "-profile:v", "high",
              "-preset", "medium", "-b:v", f"{vb}k", "-maxrate", f"{min(16000, vb * 2)}k", "-bufsize", f"{min(32000, vb * 4)}k",
              "-g", "15", "-bf", "2", "-flags", "+cgop", "-pix_fmt", "yuv420p", "-passlogfile", f"{wd}/pass"]
    run(cmd + common + ["-pass", "1", "-an", "-f", "mp4", "/dev/null"])
    run(cmd + ["-i", f"{wd}/m.wav"] + common + ["-map", f"{len(imgs)}:a", "-pass", "2", "-c:a", "aac", "-b:a", "384k",
               "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", out])
    print(f"완성: {out} ({os.path.getsize(out):,} bytes, {T:.1f}초)")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], "--frames" in sys.argv)
