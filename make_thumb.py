"""신앙 서적 리뷰 썸네일 (1280x720, 2560x1440으로 그린 뒤 축소)."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

W, H = 2560, 1440
FD = "/usr/share/fonts/opentype/noto/"
def F(n, s): return ImageFont.truetype(FD + n, s, index=1)
SKY, CREAM, MUTED = (150, 196, 228), (248, 245, 238), (175, 188, 204)
NAVY = (8, 14, 26)

def make(no, title, hook, author, photo, out, focus=0.5, pw=0.62, bright=1.0):
    base = Image.new("RGB", (W, H), NAVY)
    # 오른쪽 사진 (전체 높이, 가로 pw 비율)
    ph = Image.open(photo).convert("RGB")
    PW = int(W * pw); r = max(PW / ph.width, H / ph.height)
    ph = ph.resize((int(ph.width * r) + 1, int(ph.height * r) + 1), Image.LANCZOS)
    top = int((ph.height - H) * focus); left = (ph.width - PW) // 2
    ph = ph.crop((left, top, left + PW, top + H))
    ph = ImageEnhance.Brightness(ph).enhance(bright)
    ph = ImageEnhance.Color(ph).enhance(0.9)
    base.paste(ph, (W - PW, 0))
    # 왼쪽으로 갈수록 남색으로 — 글자 영역 확보
    g = Image.new("L", (W, 1))
    x0 = W - PW
    for x in range(W):
        t = (x - x0) / (PW * 0.55)
        a = 255 if t <= 0 else int(255 * max(0.0, 1 - t) ** 1.6)
        g.putpixel((x, 0), a)
    g = g.resize((W, H))
    base = Image.composite(Image.new("RGB", (W, H), NAVY), base, g)
    # 아래 살짝 어둡게
    v = Image.new("L", (1, H))
    for y in range(H): v.putpixel((0, y), int(120 * max(0, (y - H * 0.7) / (H * 0.3)) ** 1.5))
    base = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), base, v.resize((W, H)))

    d = ImageDraw.Draw(base)
    X = 150
    # 배지
    bf = F("NotoSansCJK-Bold.ttc", 62); bt = f"신앙 서적 리뷰  #{no}"
    bw = d.textlength(bt, font=bf)
    d.rounded_rectangle((X, 150, X + bw + 90, 270), radius=60, fill=SKY)
    d.text((X + 45, 210), bt, font=bf, fill=NAVY, anchor="lm")
    # 제목 (큰 글씨, 그림자)
    lines = title.split("\n"); size = 300 if len(lines) == 1 else 215
    tf = F("NotoSerifCJK-Black.ttc", size)
    while max(d.textlength(l, font=tf) for l in lines) > W * 0.56:
        size -= 10; tf = F("NotoSerifCJK-Black.ttc", size)
    y = 330
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    yy = y
    for l in lines:
        sd.text((X + 8, yy + 10), l, font=tf, fill=(0, 0, 0, 200)); yy += int(size * 1.12)
    sh = sh.filter(ImageFilter.GaussianBlur(14)); base.paste(sh, (0, 0), sh); d = ImageDraw.Draw(base)
    for l in lines:
        d.text((X, y), l, font=tf, fill=CREAM); last = d.textbbox((X, y), l, font=tf)[3]; y += int(size * 1.12)
    # 강조 선
    y = last + 45; d.rectangle((X, y, X + 140, y + 12), fill=SKY); y += 60
    # 한 줄 훅
    hf = F("NotoSansCJK-Bold.ttc", 92)
    for l in hook.split("\n"):
        d.text((X, y), l, font=hf, fill=SKY); y += 120
    # 저자
    d.text((X, H - 150), author, font=F("NotoSansCJK-Medium.ttc", 64), fill=MUTED, anchor="lm")
    base.resize((1280, 720), Image.LANCZOS).save(out, quality=92)

if __name__ == "__main__":
    # 사용법: python3 make_thumb.py 번호 "제목" "훅 1줄\n훅 2줄" "저자  ·  연도" 사진.jpg 출력.jpg [focus]
    a = sys.argv; nl = lambda s: s.replace("\\n", "\n")
    make(int(a[1]), nl(a[2]), nl(a[3]), a[4], a[5], a[6], focus=float(a[7]) if len(a) > 7 else 0.5)
