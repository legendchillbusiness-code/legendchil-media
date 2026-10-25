import os, cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
D = os.path.dirname(os.path.abspath(__file__))
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

def slide2(photo, header, text, out, focus=(0.5, 0.5)):
    im = Image.new("RGB", (W, H), Y); d = ImageDraw.Draw(im)
    d.text((W/2, 56), header, font=PB(64), fill=K, anchor="mm")
    ph = Image.open(f"{D}/{photo}").convert("RGB")
    ph = ImageOps.fit(ph, (1056, 600), Image.LANCZOS, centering=focus)
    im.paste(ph, (12, 110))
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
    im.save(f"{D}/{out}", quality=93)

def cover_pt(out):
    im = cv2.imread(f"{D}/cover_psychology_says.jpg")
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    mask = np.zeros(hsv.shape, np.uint8)
    roi = hsv[580:690, 190:880]
    m = (roi > 200).astype(np.uint8) * 255
    mask[580:690, 190:880] = cv2.dilate(m, np.ones((9, 9), np.uint8))
    clean = cv2.inpaint(im, mask, 7, cv2.INPAINT_TELEA)
    pim = Image.fromarray(cv2.cvtColor(clean, cv2.COLOR_BGR2RGB)); d = ImageDraw.Draw(pim)
    d.text((W/2, 635), "A psicologia diz...", font=ImageFont.truetype("/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf", 76), fill=WH, anchor="mm")
    pim.save(f"{D}/{out}", quality=93)

EN = [
 ("photo1.jpg", "People who let you talk while you make mistakes aren't being polite. They're *winning.*", (0.5, 0.5)),
 ("photo2.jpg", "Calm people aren't unaffected. They decided your words don't get to *control* them.", (0.5, 0.35)),
 ("photo3.jpg", "The person who betrays you is rarely a stranger. It's someone close enough to *know* you.", (0.5, 0.5)),
 ("photo4.jpg", "People who keep you afraid don't need to control you. Your *fear* does it for them.", (0.5, 0.45)),
 ("photo5.jpg", "When someone tells you who to blame, ask who *benefits.*", (0.5, 0.5)),
 ("photo6.jpg", "Predictable people are the easiest to *manipulate.*", (0.5, 0.5)),
]
PT = [
 "Quem te deixa falar enquanto erras não está a ser educado. Está a *ganhar.*",
 "Pessoas calmas não são indiferentes. Decidiram que as tuas palavras não as *controlam.*",
 "Quem te trai raramente é um estranho. É alguém perto o suficiente para te *conhecer.*",
 "Quem te mantém com medo não precisa de te controlar. O teu *medo* faz isso por eles.",
 "Quando alguém te diz a quem culpar, pergunta quem *ganha* com isso.",
 "Pessoas previsíveis são as mais fáceis de *manipular.*",
]
for i, (ph, t, fc) in enumerate(EN, 1):
    slide2(ph, "DID YOU KNOW?", t, f"en_{i}.jpg", fc)
    slide2(ph, "SABIAS QUE?", PT[i-1], f"pt_{i}.jpg", fc)
cover_pt("cover_pt.jpg")
Image.open(f"{D}/cover_psychology_says.jpg").convert("RGB").save(f"{D}/cover_en.jpg", quality=95)
print("ok")
