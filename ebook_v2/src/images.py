"""Capas Gumroad, miniaturas, cartões finais, último slide TikTok e foto de perfil Ψ (dourado)."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

R = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(R, "out", "img"); os.makedirs(O, exist_ok=True)
GOLD, ICE, BG, HI, MUTE = (184, 151, 90), (159, 180, 200), (11, 11, 14), (243, 243, 246), (150, 150, 160)
SERIF = os.path.join(R, "fonts", "eb-garamond-latin-600-normal.woff")
SERIF_I = os.path.join(R, "fonts", "eb-garamond-latin-500-italic.woff")
SANS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
SANS_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SANS_R = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
def F(p, s): return ImageFont.truetype(p, s)

def bg(w, h, cx=.5, cy=.42):
    im = Image.new("RGB", (w, h), BG)
    g = Image.new("L", (w, h), 0); d = ImageDraw.Draw(g)
    r = int(max(w, h) * .55)
    d.ellipse([w*cx - r, h*cy - r, w*cx + r, h*cy + r], fill=60)
    g = g.filter(ImageFilter.GaussianBlur(r * .45))
    warm = Image.new("RGB", (w, h), (34, 30, 22))
    im = Image.composite(warm, im, g)
    # vinheta
    v = Image.new("L", (w, h), 0); dv = ImageDraw.Draw(v)
    dv.rectangle([0, 0, w, h], fill=120); dv.ellipse([-w*.2, -h*.2, w*1.2, h*1.2], fill=0)
    v = v.filter(ImageFilter.GaussianBlur(min(w, h) * .12))
    return Image.composite(Image.new("RGB", (w, h), (0, 0, 0)), im, v)

def mockup(cover_png, h):
    c = Image.open(cover_png).convert("RGB")
    w = int(c.width * h / c.height); c = c.resize((w, h), Image.LANCZOS)
    # lombada
    d = ImageDraw.Draw(c)
    for i in range(int(w * .035)):
        a = int(90 * (1 - i / (w * .035)))
        d.line([(i, 0), (i, h)], fill=(max(0, 11 - a // 10), max(0, 11 - a // 10), max(0, 14 - a // 10)))
    d.line([(int(w*.035), 0), (int(w*.035), h)], fill=(60, 55, 45), width=2)
    pad = int(h * .12)
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("L", canvas.size, 0); ImageDraw.Draw(sh).rectangle([pad + 12, pad + 24, pad + w + 12, pad + h + 24], fill=210)
    sh = sh.filter(ImageFilter.GaussianBlur(pad * .35))
    glow = Image.new("L", canvas.size, 0); ImageDraw.Draw(glow).rectangle([pad, pad, pad + w, pad + h], fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(pad * .6))
    canvas = Image.composite(Image.new("RGBA", canvas.size, GOLD + (255,)), canvas, glow)
    canvas.paste(Image.new("RGBA", canvas.size, (0, 0, 0, 255)), (0, 0), sh)
    canvas.paste(c, (pad, pad))
    ImageDraw.Draw(canvas).rectangle([pad, pad, pad + w - 1, pad + h - 1], outline=(70, 62, 45), width=1)
    return canvas, pad

def text_rich(d, xy, parts, font, anchor="la"):
    """parts = [(texto, cor)] numa linha"""
    x, y = xy
    total = sum(d.textlength(t, font=font) for t, _ in parts)
    if anchor[0] == "m": x -= total / 2
    for t, col in parts:
        d.text((x, y), t, font=font, fill=col, anchor="l" + anchor[1]); x += d.textlength(t, font=font)

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

C = {
 "pt": dict(cover="cover_pt.png", scover="cover_pt_s.png", kicker="PSICOLOGIA ESCURA · LINGUAGEM CORPORAL",
   head="Lê as pessoas antes que elas te leiam a ti.", pts=["26 capítulos · 10 ilustrações", "10 casos reais e estudos", "Bónus: cábula + 15 red flags"],
   skicker="AMOSTRA GRÁTIS", shead="Os sinais estavam lá. Aprende a vê-los.", spts=["Capítulo 1 completo", "O love bombing por dentro", "Código de 20% no fim"],
   endtop="O GUIA COMPLETO", endcta=[("Comenta ", HI), ("MENTE", GOLD)], endsub="e envio-te o link"),
 "en": dict(cover="cover_en.png", scover="cover_en_s.png", kicker="DARK PSYCHOLOGY · BODY LANGUAGE",
   head="Read people before they read you.", pts=["26 chapters · 10 illustrations", "10 real cases and studies", "Bonus: cheat sheet + 15 red flags"],
   skicker="FREE PREVIEW", shead="The signs were there. Learn to see them.", spts=["All of Chapter 1", "Love bombing, from the inside", "20% code at the end"],
   endtop="THE FULL GUIDE", endcta=[("Link in ", HI), ("bio", GOLD)], endsub="Read Anyone Instantly"),
}

def gumroad_cover(lang, sample=False):
    c = C[lang]; W, H = 1280, 720
    im = bg(W, H, .3, .5); d = ImageDraw.Draw(im)
    m, pad = mockup(os.path.join(R, "out", c["scover" if sample else "cover"]), 560)
    im.paste(m, (300 - m.width // 2, H // 2 - m.height // 2 + 5), m)
    x = 600
    d.text((x, 175), c["skicker" if sample else "kicker"], font=F(SANS, 17), fill=GOLD)
    y = 215
    for ln in wrap(d, c["shead" if sample else "head"], F(SERIF, 62), 600):
        d.text((x, y), ln, font=F(SERIF, 62), fill=HI); y += 70
    d.line([(x, y + 22), (x + 60, y + 22)], fill=GOLD, width=2); y += 52
    for p in c["spts" if sample else "pts"]:
        d.ellipse([x, y + 9, x + 7, y + 16], fill=GOLD); d.text((x + 22, y), p, font=F(SANS_R, 23), fill=(215, 215, 222)); y += 40
    im.save(os.path.join(O, f"gumroad_cover_{'sample_' if sample else ''}{lang}.png"))

def thumb(lang, sample=False):
    c = C[lang]; W = 600
    im = bg(W, W, .5, .48); d = ImageDraw.Draw(im)
    m, pad = mockup(os.path.join(R, "out", c["scover" if sample else "cover"]), 470)
    im.paste(m, (W // 2 - m.width // 2, W // 2 - m.height // 2 - (22 if sample else 0)), m)
    if sample:
        d = ImageDraw.Draw(im)
        d.rectangle([0, 528, W, 600], fill=GOLD)
        d.text((W / 2, 564), "AMOSTRA GRÁTIS" if lang == "pt" else "FREE PREVIEW", font=F(SANS_B, 34), fill=BG, anchor="mm")
    im.save(os.path.join(O, f"gumroad_thumb_{'sample_' if sample else ''}{lang}.png"))

def endcard(lang):
    c = C[lang]; W, H = 1080, 1920
    im = bg(W, H, .5, .44); d = ImageDraw.Draw(im)
    d.text((W / 2, 300), c["endtop"], font=F(SANS, 34), fill=GOLD, anchor="mm")
    m, pad = mockup(os.path.join(R, "out", c["cover"]), 980)
    im.paste(m, (W // 2 - m.width // 2, 870 - m.height // 2), m)
    text_rich(d, (W / 2, 1500), c["endcta"], F(SERIF, 120), anchor="mm")
    d.text((W / 2, 1610), c["endsub"], font=F(SANS_R, 40), fill=(200, 200, 208), anchor="mm")
    im.save(os.path.join(O, f"endcard_{lang}.png"))

def lastslide(variant):
    W, H = 1080, 1920
    hooks = {"A": [[("Want to ", HI), ("see it", GOLD)], [("before it happens?", HI)]],
             "B": [[("Most people ", HI), ("never", GOLD)], [("see it coming.", HI)]]}
    im = bg(W, H, .5, .5); d = ImageDraw.Draw(im)
    y = 290
    for ln in hooks[variant]:
        text_rich(d, (W / 2, y), ln, F(SERIF, 96), anchor="mm"); y += 112
    m, pad = mockup(os.path.join(R, "out", "cover_en.png"), 900)
    im.paste(m, (W // 2 - m.width // 2, 1010 - m.height // 2), m)
    text_rich(d, (W / 2, 1610), [("Link in ", HI), ("bio", GOLD)], F(SANS_B, 72), anchor="mm")
    d.text((W / 2, 1712), "Follow for part 2", font=F(SANS_R, 44), fill=(200, 200, 208), anchor="mm")
    im.save(os.path.join(O, f"tiktok_lastslide_{variant}.png"))

def pfp():
    W = 1080; im = Image.new("RGB", (W, W), BG); d = ImageDraw.Draw(im)
    g = Image.new("L", (W, W), 0); ImageDraw.Draw(g).ellipse([240, 240, 840, 840], fill=70)
    g = g.filter(ImageFilter.GaussianBlur(120)); im = Image.composite(Image.new("RGB", (W, W), (40, 34, 22)), im, g); d = ImageDraw.Draw(im)
    d.ellipse([40, 40, W - 40, W - 40], outline=GOLD, width=26)
    d.text((W / 2, W / 2 - 10), "Ψ", font=F("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 520), fill=GOLD, anchor="mm")
    im.save(os.path.join(O, "pfp_B_psi_gold.png"))

if __name__ == "__main__":
    for lg in ("pt", "en"):
        gumroad_cover(lg); gumroad_cover(lg, True); thumb(lg); thumb(lg, True); endcard(lg)
    lastslide("A"); lastslide("B"); pfp()
    print(sorted(os.listdir(O)))
