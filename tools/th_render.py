import subprocess, numpy as np, json, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SRC = '/root/th4/raw.mp4'
FONT = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
GOLD = (226, 186, 112)
WHITE = (255, 255, 255)

# kept source segments: (start, end, zoom_start, zoom_end)
SEGS = [
    (1.15, 2.40, 1.14, 1.14),
    (3.55, 6.40, 1.00, 1.00),
    (6.70, 10.45, 1.06, 1.06),
    (10.90, 12.10, 1.00, 1.00),
    (12.35, 15.55, 1.00, 1.20),
    (15.95, 21.10, 1.06, 1.06),
    (21.25, 27.20, 1.00, 1.00),
    (27.45, 29.13, 1.08, 1.08),
    (29.13, 31.12, 1.00, 1.00),
]
# b-roll in source time
BROLL = [
    (6.75, 8.80, '/root/th4/img/b1.jpg'),
    (17.70, 20.95, '/root/th4/img/b2.jpg'),
    (24.45, 27.10, '/root/th4/img/b3.jpg'),
]
# caption chunks: (start, end, [(word, kw)], big)
C = [
    (1.26, 2.22, [('CALA-TE.', 1)], 0),
    (3.66, 4.74, [('QUEM', 0), ('MENTE', 1)], 0),
    (4.74, 6.26, [('ODEIA', 0), ('O', 0), ('SILÊNCIO.', 1)], 0),
    (6.82, 7.66, [('FAZ', 0), ('UMA', 0), ('PERGUNTA', 1)], 0),
    (7.66, 8.74, [('E', 0), ('ELE', 0), ('RESPONDE.', 0)], 0),
    (8.88, 9.18, [('E', 0), ('TU,', 0)], 0),
    (9.60, 10.32, [('NÃO', 0), ('DIZES', 0), ('NADA.', 1)], 0),
    (11.00, 11.48, [('OLHA', 0), ('PARA', 0), ('ELE.', 0)], 0),
    (11.48, 11.98, [('CALMA.', 1)], 0),
    (12.50, 13.30, [('UM', 1)], 1),
    (13.44, 14.80, [('DOIS', 1)], 1),
    (14.98, 15.55, [('TRÊS', 1)], 1),
    (16.12, 16.84, [('QUEM', 0), ('DIZ', 0), ('A', 0), ('VERDADE', 1)], 0),
    (16.84, 17.38, [('ESPERA.', 0)], 0),
    (17.76, 19.08, [('QUEM', 0), ('ESCONDE', 1), ('ALGUMA', 0), ('COISA', 0)], 0),
    (19.08, 20.10, [('COMEÇA', 0), ('A', 0), ('ENCHER', 0)], 0),
    (20.10, 20.90, [('O', 0), ('SILÊNCIO.', 1)], 0),
    (21.36, 22.44, [('JUSTIFICA-SE.', 1)], 0),
    (22.88, 23.36, [('DÁ', 0), ('DETALHES', 1)], 0),
    (23.36, 24.04, [('QUE', 0), ('NINGUÉM', 0), ('PEDIU.', 0)], 0),
    (24.52, 25.22, [('MUDA', 0), ('A', 0), ('HISTÓRIA.', 1)], 0),
    (25.22, 26.18, [('UM', 0), ('SINAL', 1)], 0),
    (26.18, 27.04, [('NÃO', 0), ('PROVA', 0), ('NADA,', 0)], 0),
    (27.56, 28.28, [('MAS', 0), ('MOSTRA-TE', 0)], 0),
    (28.28, 29.04, [('ONDE', 0), ('CARREGAR.', 1)], 0),
    (29.22, 30.08, [('TENHO', 0), ('UM', 0), ('CAPÍTULO', 1)], 0),
    (30.08, 31.06, [('INTEIRO', 0), ('SOBRE', 0), ('ISTO.', 0)], 0),
]

def src_to_out(t):
    acc = 0.0
    for a, b, *_ in SEGS:
        if t < a: return acc
        if t <= b: return acc + (t - a)
        acc += b - a
    return acc
TOTAL = sum(b - a for a, b, *_ in SEGS)

fnt = ImageFont.truetype(FONT, 80)
fbig = ImageFont.truetype(FONT, 230)
ftitle = ImageFont.truetype(FONT, 66)
_cache = {}
def caption_layer(ci, nshow):
    key = (ci, nshow)
    if key in _cache: return _cache[key]
    s, e, words, big = C[ci]
    f = fbig if big else fnt
    sp = f.getlength(' ')
    widths = [f.getlength(w) for w, _ in words]
    tw = sum(widths) + sp * (len(words) - 1)
    if tw > 960:
        f = ImageFont.truetype(FONT, int(80 * 960 / tw))
        sp = f.getlength(' ')
        widths = [f.getlength(w) for w, _ in words]
        tw = sum(widths) + sp * (len(words) - 1)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    y = 900 if big else 1300
    x = (W - tw) / 2
    stroke = 12 if big else 7
    for i, (w, kw) in enumerate(words):
        if i < nshow:
            col = GOLD if kw else WHITE
            # shadow
            d.text((x + 4, y + 6), w, font=f, fill=(0, 0, 0, 150), stroke_width=stroke, stroke_fill=(0, 0, 0, 150))
            d.text((x, y), w, font=f, fill=col, stroke_width=stroke, stroke_fill=(0, 0, 0))
        x += widths[i] + sp
    _cache[key] = lay
    return lay

def title_layer():
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    parts = [('CALA-TE', GOLD), (' 3 SEGUNDOS', WHITE)]
    tw = sum(ftitle.getlength(p) for p, _ in parts)
    x = (W - tw) / 2; y = 300
    d.rounded_rectangle((x - 30, y - 18, x + tw + 30, y + 96), 18, fill=(0, 0, 0, 200))
    for p, c in parts:
        d.text((x, y), p, font=ftitle, fill=c); x += ftitle.getlength(p)
    return lay
TITLE = title_layer()
def dm_layer():
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    parts = [('MANDA-ME DM: ', WHITE), ('MENTE', GOLD)]
    tw = sum(ftitle.getlength(p) for p, _ in parts)
    x = (W - tw) / 2; y = 300
    d.rounded_rectangle((x - 30, y - 18, x + tw + 30, y + 96), 18, fill=(0, 0, 0, 200))
    for p, c in parts:
        d.text((x, y), p, font=ftitle, fill=c); x += ftitle.getlength(p)
    return lay
DM = dm_layer()

def broll_frame(path, k):
    im = Image.open(path).convert('L')
    im = im.point(lambda v: max(0, min(255, int((v - 128) * 1.25 + 118))))
    s = 1.0 + 0.08 * k
    sw, sh = im.size
    scale = max(W / sw, H / sh) * s
    im = im.resize((int(sw * scale), int(sh * scale)), Image.LANCZOS)
    x = (im.width - W) // 2; y = (im.height - H) // 2
    im = im.crop((x, y, x + W, y + H)).convert('RGB')
    a = np.asarray(im).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - 0.55 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2
    a *= np.clip(v, 0, 1)[..., None]
    a[..., 2] *= 1.04
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
_bcache = {}

def zoom(img, z):
    if abs(z - 1) < 1e-3: return img
    cx, cy = 540, 820
    w, h = W / z, H / z
    x0 = min(max(cx - w / 2, 0), W - w); y0 = min(max(cy - h / 2, 0), H - h)
    return img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))

out = sys.argv[1]
dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', SRC, '-vf', f'fps={FPS},scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
i = 0; n = 0
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    t = i / FPS; i += 1
    seg = next((s for s in SEGS if s[0] <= t < s[1]), None)
    if seg is None: continue
    a, bb, z0, z1 = seg
    img = Image.frombuffer('RGB', (W, H), b)
    br = next((x for x in BROLL if x[0] <= t < x[1]), None)
    if br:
        k = (t - br[0]) / (br[1] - br[0])
        kk = round(k * 40) / 40
        key = (br[2], kk)
        if key not in _bcache: _bcache[key] = broll_frame(br[2], kk)
        img = _bcache[key].copy()
    else:
        img = zoom(img, z0 + (z1 - z0) * (t - a) / (bb - a))
    img = img.convert('RGBA')
    tout = src_to_out(t)
    if tout < 3.6: img.alpha_composite(TITLE)
    if t >= 29.15: img.alpha_composite(DM)
    # caption
    ci = None
    for j, (s, e, words, big) in enumerate(C):
        nxt = C[j + 1][0] if j + 1 < len(C) else 99
        if s - 0.05 <= t < min(nxt, e + 0.6):
            ci = j
    if ci is not None:
        s, e, words, big = C[ci]
        nw = len(words)
        nshow = min(nw, 1 + int((t - s) / max(0.01, (e - s)) * nw)) if t < e else nw
        img.alpha_composite(caption_layer(ci, max(1, nshow)))
    enc.stdin.write(img.convert('RGB').tobytes()); n += 1
enc.stdin.close(); enc.wait()
print('frames', n, 'expected', round(TOTAL * FPS))
json.dump([[a, b] for a, b, *_ in SEGS], open('/root/th4/segs.json', 'w'))
