# 2-slide "People who... are [hidden intent]" carousels (viral 24/10 format).
# Reuses the approved photos from images/psych_says/en_N.jpg and the same EN cover.
import os, sys
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC, OUT = f"{R}/images/psych_says", f"{R}/images/people_who"
W, H = 1080, 1023
Y = (236, 221, 30); K = (10, 10, 10); WH = (255, 255, 255)
PB = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf", s)

def wrap(d, words, font, maxw):
    lines, cur = [], []
    for w in words:
        t = cur + [w]
        if d.textlength(" ".join(x for x, _ in t), font=font) <= maxw: cur = t
        else: lines.append(cur); cur = [w]
    return lines + [cur]

def slide2(src_n, text, out):
    photo = Image.open(f"{SRC}/en_{src_n}.jpg").convert("RGB").crop((12, 110, 1068, 710))
    im = Image.new("RGB", (W, H), Y); d = ImageDraw.Draw(im)
    d.text((W/2, 56), "DID YOU KNOW?", font=PB(64), fill=K, anchor="mm")
    im.paste(photo, (12, 110))
    d.rectangle((12, 710, W-12, H), fill=K)
    words = [(w.strip("*"), w.startswith("*")) for w in text.split()]
    for size in (62, 58, 54, 50):
        f = PB(size); lines = wrap(d, words, f, 960)
        if len(lines) <= 3: break
    lh = int(size * 1.22); y0 = 710 + (313 - lh * len(lines)) / 2
    for i, ln in enumerate(lines):
        tw = d.textlength(" ".join(x for x, _ in ln), font=f); x = (W - tw) / 2; y = y0 + i * lh
        for w, kw in ln:
            d.text((x, y), w, font=f, fill=Y if kw else WH); x += d.textlength(w + " ", font=f)
    im.save(f"{OUT}/{out}", quality=93)

POSTS = [  # (photo from en_N, slide text)
 (1, "People who agree with everything you say are *managing* you."),
 (2, "People who stay calm in every argument already *won* before it started."),
 (4, "People who remember every detail you tell them are *collecting* you."),
 (3, "People who tell you other people's secrets are telling others *yours.*"),
 (5, "People who go quiet when you succeed were *competing* with you."),
 (6, "People who never ask for help don't *trust* anyone."),
]
os.makedirs(OUT, exist_ok=True)
for i, (n, t) in enumerate(POSTS, 1):
    slide2(n, t, f"pw_{i}.jpg")
Image.open(f"{SRC}/cover_en.jpg").save(f"{OUT}/cover_en.jpg", quality=95)
print("ok")
