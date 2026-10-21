import subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
BG = (10, 10, 10); WHITE = (238, 236, 232); GOLD = (184, 151, 90); DIM = (120, 104, 72)
F = lambda w, s: ImageFont.truetype(f"{D}/ebg-{w}.ttf", s)
f_psi = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 30)
f_hook, f_q, f_g, f_sm, f_num = F("600-normal", 92), F("500-normal", 74), F("500-normal", 66), F("500-normal", 30), F("600-normal", 60)

# scenes: (duration, [(text, font, color, gap_after, delay)])
items = [
    ("You're overreacting.", "Your reaction\nbecomes the problem."),
    ("After everything\nI've done for you.", "A debt you never agreed to."),
    ("Everyone agrees with me.", "An audience you can't check."),
    ("That's not what I said.", "Now you doubt\nyour own memory."),
    ("I was only joking.", "A test.\nYour silence was the answer."),
    ("Fine, do whatever you want.", "Guilt, delivered as freedom."),
]
scenes = [(1.8, [("6 things manipulators", f_hook, WHITE, 0, 0), ("say FIRST.", f_hook, GOLD, 60, 0),
                 ("#5 is the one you fell for.", f_g, GOLD, 0, 0.6)])]
for i, (q, g) in enumerate(items, 1):
    scenes.append((1.9, [(f"{i}", f_num, GOLD, 40, 0), (f"“{q}”".replace("\n”","”"), f_q, WHITE, 50, 0), (g, f_g, GOLD, 0, 0.55)]))
scenes += [(2.0, [("One sign proves nothing.", f_q, WHITE, 40, 0), ("The pattern does.", f_q, GOLD, 0, 0.5)]),
           (2.4, [("Read Anyone Instantly", f_q, WHITE, 40, 0), ("Link in bio.", f_q, GOLD, 0, 0.4)])]

def wrap(d, text, font, maxw=900):
    if "\n" in text: return text.split("\n")
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def frame(blocks, t):
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    d.text((W/2+14, 150), "LEGENDCHIL", font=f_sm, fill=DIM, anchor="mm"); d.text((W/2-d.textlength("LEGENDCHIL", font=f_sm)/2-10, 150), "Ψ", font=f_psi, fill=DIM, anchor="mm")
    laid = []
    for text, font, col, gap, delay in blocks:
        lh = int(font.size * 1.18)
        laid.append((wrap(d, text, font), font, col, gap, delay, lh))
    total = sum(len(l)*lh + gap for l, _, _, gap, _, lh in laid)
    y = (H - total) / 2 - 40
    for lines, font, col, gap, delay, lh in laid:
        a = max(0.0, min(1.0, (t - delay) / 0.18))
        if a > 0:
            c = tuple(int(BG[k] + (col[k]-BG[k])*a) for k in range(3))
            for ln in lines:
                d.text((W/2, y + lh/2 + (1-a)*14), ln, font=font, fill=c, anchor="mm"); y += lh
        else:
            y += lh*len(lines)
        y += gap
    yb = y + 30
    d.line([(W/2-28, yb), (W/2+28, yb)], fill=GOLD, width=2)
    return im

out = sys.argv[1]
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                      "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
for dur, blocks in scenes:
    for n in range(int(dur*FPS)):
        p.stdin.write(frame(blocks, n/FPS).tobytes())
p.stdin.close(); p.wait()
print("total", sum(s[0] for s in scenes))
