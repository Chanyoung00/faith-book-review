#!/usr/bin/env python3
"""신앙 서적 리뷰 (새 양식) — 기독교 사상사 양식을 따른 2K 롱폼 생성기
전체 화면 사진 + 천천히 움직이는 카메라 + 카드 1장 = 1문장(한/영) + 낮은 오르골 찬송가
사용법: python3 make_book.py cards_01.py [--frames]
"""
import os, sys, json, subprocess, importlib.util, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BASE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("cards", sys.argv[1]); C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
EP, BOOK, PARTS, CARDS = C.EP, C.BOOK, C.PARTS, C.CARDS
CREDITS = getattr(C, "CREDITS", {}); ORIG = getattr(C, "ORIG", None); MUSIC = getattr(C, "MUSIC", {"hymn": "amazing_grace", "seed": EP})
LONG = getattr(C, "LONG", {})
IMG = f"{BASE}/img/{EP:02d}"; WD = f"{BASE}/work{EP:02d}"; os.makedirs(WD, exist_ok=True)

W, H, FPS = 2560, 1440, 30
FD = "/usr/share/fonts/opentype/noto/"
def F(name, size): return ImageFont.truetype(FD + name, size, index=1)
ACC, CREAM, MUTED = (156, 196, 226), (244, 241, 234), (200, 206, 214)     # 포인트색: 은은한 하늘빛 (리뷰 시리즈 표식)
SERIES = f"신앙 서적 리뷰 #{EP}  ·  Faith Book Review"

# ---------- 카드 길이 ----------
def card_dur(c):
    no, bg, part, ko, en, kind = c
    n = len(ko.replace("\n", "").replace(" ", ""))
    d = 3.0 + 0.155 * n
    if kind == "title": d = 6.5
    if kind == "book": d = 8.0
    if kind == "label": d = 5.0
    if no in LONG: d = LONG[no]
    return round(min(max(d, 4.8), 9.5), 2)
DURS = [card_dur(c) for c in CARDS]; TOTAL = round(sum(DURS), 2)

# ---------- 배경 (사상사와 같은 시네마 톤: 채도↓, 어둡게, 비네팅) ----------
def cover(im, w, h):
    r = max(w / im.width, h / im.height); im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2; return im.crop((l, t, l + w, t + h))
def tone(im):
    im = ImageEnhance.Color(im).enhance(0.55)
    a = np.asarray(im).astype(np.float32) / 255
    a = a * np.array([1.0, 0.99, 0.96])
    a = 0.05 + a * 0.52
    y = np.linspace(-1, 1, a.shape[0])[:, None]; x = np.linspace(-1, 1, a.shape[1])[None, :]
    vig = np.clip(1 - 0.42 * (x ** 2 * 0.8 + y ** 2), 0.35, 1)[..., None]
    band = 1 - 0.38 * np.exp(-((y / 0.42) ** 2))[..., None] * np.exp(-((x / 0.9) ** 2))[..., None]
    return Image.fromarray((np.clip(a * vig * band, 0, 1) * 255).astype(np.uint8))
def prep_bg(name):
    out = f"{WD}/bg_{name}.png"
    if os.path.exists(out): return out
    TW, TH = 3840, 2160
    if name == "ORIG" and not (ORIG and os.path.exists(f"{IMG}/{ORIG['file']}")):
        return prep_bg(ORIG.get("fallback", "oldbook"))      # 원본 책 사진이 아직 없으면 임시 배경
    if name == "ORIG":                      # 원어 원본 책: 흐린 어두운 배경 위에 실제 책(표지/속표지)을 가운데
        src = Image.open(f"{IMG}/{ORIG['file']}")
        if src.mode in ("L", "LA", "1"):    # 흑백 스캔은 옛 종이 빛깔로
            from PIL import ImageOps
            src = ImageOps.colorize(src.convert("L"), black=(38, 28, 20), white=(232, 220, 194))
        src = src.convert("RGB")
        back = tone(cover(src, TW, TH).filter(ImageFilter.GaussianBlur(40)))
        back = ImageEnhance.Brightness(back).enhance(0.55)
        r = min(TH * 0.64 / src.height, TW * 0.62 / src.width, 3.0); bh = int(src.height * r)
        bk = src.resize((int(src.width * r), bh), Image.LANCZOS)
        if r > 1.5: bk = bk.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
        bk = ImageEnhance.Color(bk).enhance(0.85)
        x, y = (TW - bk.width) // 2, int(TH * 0.09) + (int(TH * 0.64) - bh) // 2
        sh = Image.new("L", (TW, TH), 0); ImageDraw.Draw(sh).rectangle((x + 30, y + 40, x + bk.width + 30, y + bh + 40), fill=200)
        back = Image.composite(Image.new("RGB", (TW, TH), (0, 0, 0)), back, sh.filter(ImageFilter.GaussianBlur(50)))
        back.paste(bk, (x, y)); back.save(out); return out
    im = cover(Image.open(f"{IMG}/{name}.jpg").convert("RGB"), TW, TH)
    tone(im).save(out); return out

# ---------- 자막 ----------
def en_wrap(d, en, fe, maxw=1900):
    words, lines, cur = en.split(" "), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=fe) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w_
    lines.append(cur); return lines
def text_png(c, path):
    no, bg, part, ko, en, kind = c
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if kind == "title":
        f1 = F("NotoSerifCJK-Black.ttc", 160); f2 = F("NotoSerifCJK-Regular.ttc", 52); f0 = F("NotoSansCJK-Medium.ttc", 44)
        d.text((W // 2, H // 2 - 160), f"신앙 서적 리뷰  #{EP}", font=f0, fill=ACC, anchor="mm")
        d.line([(W // 2 - 60, H // 2 - 110), (W // 2 + 60, H // 2 - 110)], fill=ACC, width=3)
        d.text((W // 2, H // 2 + 5), ko, font=f1, fill=CREAM, anchor="mm")
        d.text((W // 2, H // 2 + 145), en, font=f2, fill=MUTED, anchor="mm")
    elif kind == "book":                    # 원본 책 아래 캡션
        fk = F("NotoSerifCJK-Bold.ttc", 60); fe = F("NotoSerifCJK-Regular.ttc", 42)
        d.text((W // 2, H - 250), ko, font=fk, fill=CREAM, anchor="mm")
        d.text((W // 2, H - 180), en, font=fe, fill=MUTED, anchor="mm")
    else:
        lines = ko.split("\n")
        size = {"q": 78, "quote": 84, "final": 92, "label": 86}[kind]; fname = "NotoSerifCJK-Bold.ttc"
        while size > 52 and max(d.textlength(l, font=F(fname, size)) for l in lines) > 2000: size -= 2
        fk = F(fname, size); fe = F("NotoSerifCJK-Regular.ttc", 46); lh = int(size * 1.48)
        en_lines = en_wrap(d, en, fe)
        total = len(lines) * lh + 56 + len(en_lines) * 64
        y = (H - total) // 2 + 10
        for i, l in enumerate(lines):
            col = ACC if (kind == "label" and i == 0) else CREAM
            d.text((W // 2, y + lh // 2), l, font=fk, fill=col, anchor="mm"); y += lh
        y += 20; d.line([(W // 2 - 40, y), (W // 2 + 40, y)], fill=ACC, width=3); y += 36
        for l in en_lines:
            d.text((W // 2, y + 32), l, font=fe, fill=MUTED, anchor="mm"); y += 64
    sh = im.filter(ImageFilter.GaussianBlur(14)); s2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s2.putalpha(sh.getchannel("A").point(lambda a: int(a * 0.85)))
    Image.alpha_composite(s2, im).save(path)

# ---------- 고정 요소: 시리즈 표시 + 책 제목 + 읽기 진행 바 + 사진 출처 ----------
def chrome_png(part, bg, path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((90, 80), SERIES, font=F("NotoSansCJK-Medium.ttc", 34), fill=ACC + (200,), anchor="lm")
    d.text((W - 90, 80), f"『{BOOK['ko']}』 {BOOK['author_ko']}", font=F("NotoSansCJK-Medium.ttc", 32), fill=(190, 198, 208, 170), anchor="rm")
    x0, x1, yb = 760, 1800, 1335; n = len(PARTS)
    X = lambda i: x0 + (x1 - x0) * i / (n - 1)
    d.line([(x0, yb), (x1, yb)], fill=ACC + (110,), width=3)
    fs = F("NotoSansCJK-Medium.ttc", 26)
    for i, lab in enumerate(PARTS):
        d.line([(X(i), yb - 9), (X(i), yb + 9)], fill=ACC + (150,), width=2)
        d.text((X(i), yb + 34), lab, font=fs, fill=(200, 206, 214, 175 if i != part else 235), anchor="mm")
    if part is not None:
        d.line([(x0, yb), (X(part), yb)], fill=ACC + (235,), width=5)
        d.ellipse([X(part) - 11, yb - 11, X(part) + 11, yb + 11], fill=ACC + (255,))
    cr = ORIG.get("credit") if bg == "ORIG" else (f"Photo: {CREDITS[bg]} / Unsplash" if bg in CREDITS else None)
    if cr: d.text((W - 60, H - 50), cr, font=F("NotoSansCJK-Regular.ttc", 22), fill=(190, 190, 190, 150), anchor="rm")
    im.save(path)

def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def shots():
    out = []
    for i, c in enumerate(CARDS):
        if out and out[-1]["bg"] == c[1] and out[-1]["part"] == c[2]: out[-1]["idx"].append(i)
        else: out.append({"bg": c[1], "part": c[2], "idx": [i]})
    return out

def render_shot(k, s):
    D = round(sum(DURS[i] for i in s["idx"]), 3); N = int(round(D * FPS))
    out = f"{WD}/shot{k:02d}.mp4"
    if os.path.exists(out):                 # 이미 끝까지 렌더된 장면은 다시 만들지 않음
        r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip()
        if r.isdigit() and int(r) == N: return out
    bg = prep_bg(s["bg"]); ch = f"{WD}/chrome_{k}.png"; chrome_png(s["part"], s["bg"], ch)
    inputs = ["-loop", "1", "-framerate", str(FPS), "-t", f"{D}", "-i", bg, "-loop", "1", "-framerate", str(FPS), "-t", f"{D}", "-i", ch]
    z = f"1+0.07*on/{N}" if k % 2 == 0 else f"1.07-0.07*on/{N}"
    if s["bg"] == "ORIG": z = f"1+0.035*on/{N}"
    fc = [f"[0]scale=3840:2160,zoompan=z='{z}':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s={W}x{H}:fps={FPS},format=rgba[b0]",
          "[1]format=rgba[cr]", "[b0][cr]overlay=0:0[v0]"]
    t, last = 0.0, "v0"
    for j, i in enumerate(s["idx"]):
        tp = f"{WD}/t{i+1:02d}.png"; text_png(CARDS[i], tp)
        inputs += ["-loop", "1", "-framerate", str(FPS), "-t", f"{D}", "-i", tp]
        a, b = t + 0.25, t + DURS[i] - 0.75
        fc.append(f"[{j+2}]format=rgba,fade=in:st={a:.2f}:d=0.8:alpha=1,fade=out:st={b:.2f}:d=0.7:alpha=1[x{j}]")
        fc.append(f"[{last}][x{j}]overlay=0:0[v{j+1}]"); last = f"v{j+1}"; t += DURS[i]
    fc.append(f"[{last}]fade=in:st=0:d=0.6,fade=out:st={D-0.6:.2f}:d=0.6,format=yuv420p[out]")
    out = f"{WD}/shot{k:02d}.mp4"
    run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", "[out]", "-frames:v", str(N),
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), out])
    return out

def make_music(path):
    sys.path.insert(0, "/home/claude")
    from make_review import music
    return music(path, TOTAL, MUSIC)

def final(out, limit=94_000_000):
    vid, wav = f"{WD}/video.mp4", f"{WD}/m.wav"
    # 소리 깨짐 방지: 최고점 -2dB 이하로 맞춘 뒤 AAC 320k 48kHz
    run(["ffmpeg", "-y", "-i", wav, "-af", "loudnorm=I=-20:TP=-2:LRA=11,aresample=48000", "-ar", "48000", f"{WD}/m2.wav"])
    vb = int(min(14000, (limit * 8 / TOTAL) / 1000 - 360))
    common = ["-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-b:v", f"{vb}k", "-maxrate", f"{vb*2}k", "-bufsize", f"{vb*4}k",
              "-g", "15", "-bf", "2", "-flags", "+cgop", "-pix_fmt", "yuv420p", "-r", str(FPS)]
    run(["ffmpeg", "-y", "-i", vid, *common, "-pass", "1", "-passlogfile", f"{WD}/pass", "-an", "-f", "mp4", "/dev/null"])
    run(["ffmpeg", "-y", "-i", vid, "-i", f"{WD}/m2.wav", *common, "-pass", "2", "-passlogfile", f"{WD}/pass",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", out])
    return vb

if __name__ == "__main__":
    if "--frames" in sys.argv:
        for i, c in enumerate(CARDS):
            tp = f"{WD}/t{i+1:02d}.png"; text_png(c, tp); ch = f"{WD}/ch.png"; chrome_png(c[2], c[1], ch)
            b = Image.open(prep_bg(c[1])).resize((W, H)).convert("RGBA")
            Image.alpha_composite(Image.alpha_composite(b, Image.open(ch)), Image.open(tp)).convert("RGB").save(f"{WD}/prev{i+1:02d}.jpg", quality=80)
        print("cards", len(CARDS), "total", TOTAL); sys.exit()
    out = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else f"/home/claude/review_v2_{EP:02d}.mp4"
    from concurrent.futures import ThreadPoolExecutor
    S = shots()
    with ThreadPoolExecutor(4) as ex: parts = list(ex.map(lambda ks: render_shot(*ks), enumerate(S)))
    with open(f"{WD}/list.txt", "w") as f: f.writelines(f"file '{p}'\n" for p in parts)
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{WD}/list.txt", "-c", "copy", f"{WD}/video.mp4"])
    title = make_music(f"{WD}/m.wav")
    vb = final(out)
    print(json.dumps({"out": out, "bytes": os.path.getsize(out), "total": TOTAL, "kbps": vb, "music": title}, ensure_ascii=False))
