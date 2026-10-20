"""Ilustrações do ebook (PT/EN). Paleta: preto, cinzento, azul-gelo, acento dourado.
Uso: python3 illus.py  -> out/{pt,en}/fig01..fig10.png (+ .svg)
"""
import math, os
from xml.sax.saxutils import escape
import cairosvg

W, H = 1200, 800
BG, LINE, DIM, ICE, GOLD, TXT, SUB = "#0b0b0d", "#a9a9ad", "#3c3c42", "#9fb4c8", "#b8975a", "#e9e9ec", "#8d8d93"
FONT = "Inter"

L = {
 "pt": {
  "fig": "FIG.",
  1: ("As 3 máscaras", "A máscara cai em microssegundos. É aí que lês.",
      [("Máscara Pública", "o que mostra a estranhos"), ("Máscara Social", "o que mostra aos amigos"), ("Face Privada", "o que aparece sob pressão")]),
  2: ("A linha de base", "Não leias o sinal. Lê a mudança.",
      {"band": "linha de base", "spike": "desvio", "spike2": "logo após a pergunta crítica", "x": "tempo de conversa"}),
  3: ("Os pés não mentem", "O tronco é educado. Os pés dizem a verdade.",
      {"you": "tu", "torso": "tronco: virado para ti", "feet": "pés: virados para a saída", "door": "saída"}),
  4: ("As 7 expressões de Ekman", "Duram menos de meio segundo. Só a do desprezo é assimétrica.",
      ["Alegria", "Tristeza", "Raiva", "Medo", "Surpresa", "Repulsa", "Desprezo"]),
  5: ("Ler a sala", "Quando o grupo ri, os olhos vão para quem manda.",
      {"leader": "o Alfa real", "leader2": "para onde vão os olhares quando alguém ri", "pair": "aliança", "iso": "o Observador: na periferia", "door": "porta"}),
  6: ("O ciclo do love bombing", "O ciclo não acaba. Só acelera.",
      [("Idealização", "és perfeito, tudo é intenso"), ("Dependência", "o teu dia gira à volta dela"),
       ("Desvalorização", "críticas, frieza, comparações"), ("Descarte ou ciclo", "larga-te ou alterna frio e quente")], "repete"),
  7: ("Isolamento", "Ninguém isola de repente. Corta-se um laço de cada vez.",
      [("Mês 1", "“prefiro quando estamos só os dois”"), ("Mês 3", "“a tua amiga tem inveja de nós”"), ("Mês 6", "“eles não te conhecem como eu”")],
      {"you": "tu", "him": "manipulador"}),
  8: ("Reforço intermitente", "Carinho imprevisível prende mais do que carinho constante.",
      {"a": "Previsível", "a2": "habituas-te", "b": "Intermitente", "b2": "ficas à espera do próximo", "x": "tempo"}),
  9: ("Os 6 gatilhos de Cialdini", "Se sentes pressa para decidir, alguém puxou um gatilho.",
      [("Reciprocidade", "“dei-te algo”"), ("Escassez", "“só hoje”"), ("Autoridade", "“confia no especialista”"),
       ("Compromisso", "“já disseste que sim”"), ("Prova social", "“toda a gente faz”"), ("Simpatia", "“somos iguais”")],
      "a tua\ndecisão"),
  10: ("Círculos de confiança", "O acesso ganha-se com tempo e prova, não com intensidade.",
      ["Círculo interior · 2 a 5", "Círculo do meio", "Círculo exterior", "Estranhos"], "salta de fora para dentro em semanas"),
 },
 "en": {
  "fig": "FIG.",
  1: ("The 3 masks", "The mask slips for microseconds. That's when you read.",
      [("Public Mask", "what strangers see"), ("Social Mask", "what friends see"), ("Private Face", "what shows under pressure")]),
  2: ("The baseline", "Don't read the signal. Read the change.",
      {"band": "baseline", "spike": "deviation", "spike2": "right after the critical question", "x": "conversation time"}),
  3: ("The feet don't lie", "The torso is polite. The feet tell the truth.",
      {"you": "you", "torso": "torso: facing you", "feet": "feet: facing the exit", "door": "exit"}),
  4: ("Ekman's 7 expressions", "They last under half a second. Only contempt is one-sided.",
      ["Joy", "Sadness", "Anger", "Fear", "Surprise", "Disgust", "Contempt"]),
  5: ("Reading the room", "When the group laughs, eyes go to whoever's in charge.",
      {"leader": "the real Alpha", "leader2": "where eyes go when someone laughs", "pair": "alliance", "iso": "the Observer: on the edge", "door": "door"}),
  6: ("The love bombing cycle", "The cycle doesn't end. It speeds up.",
      [("Idealisation", "you're perfect, it's all intense"), ("Dependence", "your day revolves around it"),
       ("Devaluation", "criticism, coldness, comparisons"), ("Discard or cycle", "they leave, or go hot and cold")], "repeat"),
  7: ("Isolation", "Nobody isolates you overnight. One tie is cut at a time.",
      [("Month 1", "“I prefer it when it's just us”"), ("Month 3", "“your friend is jealous of us”"), ("Month 6", "“they don't know you like I do”")],
      {"you": "you", "him": "manipulator"}),
  8: ("Intermittent reinforcement", "Unpredictable affection hooks harder than constant affection.",
      {"a": "Predictable", "a2": "you get used to it", "b": "Intermittent", "b2": "you wait for the next one", "x": "time"}),
  9: ("Cialdini's 6 triggers", "If you feel rushed to decide, someone pulled a trigger.",
      [("Reciprocity", "“I gave you something”"), ("Scarcity", "“today only”"), ("Authority", "“trust the expert”"),
       ("Commitment", "“you already said yes”"), ("Social proof", "“everyone does it”"), ("Liking", "“we're the same”")],
      "your\ndecision"),
  10: ("Circles of trust", "Access is earned with time and proof, not intensity.",
      ["Inner circle · 2 to 5", "Middle circle", "Outer circle", "Strangers"], "jumps from outside to inside in weeks"),
 },
}

# ---------- primitives ----------
def t(x, y, s, size=22, fill=TXT, anchor="middle", weight=400, italic=False, ls=0, op=1, halo=False):
    st = "italic" if italic else "normal"
    lines = str(s).split("\n")
    out = []
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x}" y="{y + i*size*1.2:.1f}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
                   f'text-anchor="{anchor}" font-weight="{weight}" font-style="{st}" letter-spacing="{ls}" opacity="{op}"' + f'>{escape(ln)}</text>')
        if halo:
            out[-1] = out[-1].replace('<text ', f'<text stroke="{BG}" stroke-width="8" stroke-linejoin="round" ', 1) + out[-1]
    return "".join(out)

def line(x1, y1, x2, y2, c=LINE, w=2, dash=None, op=1, marker=None, cap="round"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="{w}" stroke-linecap="{cap}" opacity="{op}"{d}{m}/>'

def circ(x, y, r, stroke=LINE, fill="none", w=2, op=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" stroke="{stroke}" fill="{fill}" stroke-width="{w}" opacity="{op}"{d}/>'

def path(d, c=LINE, w=2, fill="none", op=1, dash=None, marker=None):
    ds = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return f'<path d="{d}" stroke="{c}" stroke-width="{w}" fill="{fill}" opacity="{op}" stroke-linecap="round" stroke-linejoin="round"{ds}{m}/>'

DEFS = f'''<defs>
<marker id="aI" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{ICE}"/></marker>
<marker id="aG" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{GOLD}"/></marker>
<marker id="aL" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/></marker>
<radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity="0.55"/></radialGradient>
<radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="{GOLD}" stop-opacity="0.28"/><stop offset="100%" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>
</defs>'''

SRC = {
 "pt": {4: "Joe Navarro, What Every Body Is Saying", 3: "Paul Ekman & W. Friesen (1971; desprezo: 1986)",
        7: "Evan Stark, controlo coercivo (2007)", 8: "B. F. Skinner, esquemas de reforço (1957)",
        9: "Robert Cialdini, Influence (1984)"},
 "en": {4: "Joe Navarro, What Every Body Is Saying", 3: "Paul Ekman & W. Friesen (1971; contempt: 1986)",
        7: "Evan Stark, coercive control (2007)", 8: "B. F. Skinner, schedules of reinforcement (1957)",
        9: "Robert Cialdini, Influence (1984)"},
}

def frame(n, title, take, body, lang):
    src = SRC[lang].get(n)
    head = (t(W - 70, 78, ("FONTE: " if lang == "pt" else "SOURCE: ") + src, 15, SUB, "end", 500, ls=1.5) if src else "") + (t(70, 78, f'{L[lang]["fig"]} {n:02d}', 17, SUB, "start", 600, ls=4) +
            t(70, 118, title, 34, TXT, "start", 600) +
            line(70, 140, 150, 140, GOLD, 2))
    foot = t(W/2, 752, take, 23, SUB, italic=True)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{DEFS}'
            f'<rect width="{W}" height="{H}" fill="{BG}"/><rect width="{W}" height="{H}" fill="url(#vig)"/>'
            f'{head}{body}{foot}</svg>')

def glow(x, y, r):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="url(#glow)"/>'

def arc(cx, cy, r, a1, a2):
    x1, y1 = cx + r*math.cos(math.radians(a1)), cy + r*math.sin(math.radians(a1))
    x2, y2 = cx + r*math.cos(math.radians(a2)), cy + r*math.sin(math.radians(a2))
    large = 1 if (a2 - a1) % 360 > 180 else 0
    return f"M{x1:.1f},{y1:.1f} A{r},{r} 0 {large} 1 {x2:.1f},{y2:.1f}"

# ---------- figures ----------
def f1(lang):
    title, take, items = L[lang][1]
    b = ""
    xs = [260, 600, 940]
    mouths = ["M-34,62 Q0,88 34,62", "M-30,70 L30,70", "M-30,76 Q0,60 30,76"]
    for i, (x, (nm, sub)) in enumerate(zip(xs, items)):
        c = GOLD if i == 2 else ICE
        y = 380
        if i == 2: b += glow(x, y, 200)
        dash = None if i != 1 else None
        b += f'<g transform="translate({x},{y})">'
        b += path("M0,-150 C95,-150 118,-60 112,10 C104,95 60,150 0,150 C-60,150 -104,95 -112,10 C-118,-60 -95,-150 0,-150 Z",
                  c, 2.5, fill="#0f0f12", op=1 if i == 2 else .85)
        for ex in (-44, 44):
            b += f'<ellipse cx="{ex}" cy="-18" rx="27" ry="14" fill="{BG}" stroke="{c}" stroke-width="2"/>'
        b += path("M0,-2 L-8,38 L8,38", c, 1.6, op=.6)
        b += path(mouths[i], c, 2.5)
        if i == 2:  # rachadura
            b += path("M70,-120 L52,-80 L66,-56 L44,-22", GOLD, 1.8, op=.9)
        b += '</g>'
        b += t(x, 590, nm, 28, GOLD if i == 2 else TXT, weight=600)
        b += t(x, 624, sub, 20, SUB)
    b += line(395, 380, 455, 380, DIM, 2, marker="aL") + line(735, 380, 795, 380, DIM, 2, marker="aL")
    return frame(1, title, take, b, lang)

def f2(lang):
    title, take, d = L[lang][2]
    b = ""
    x0, x1, yb = 120, 1090, 610
    b += line(x0, yb, x1, yb, DIM, 2, marker="aL")
    b += t(x1, yb + 34, d["x"], 18, SUB, "end")
    b += f'<rect x="{x0}" y="395" width="{x1-x0-20}" height="70" fill="{ICE}" opacity="0.07"/>'
    b += line(x0, 395, x1 - 20, 395, ICE, 1, "4 6", .5) + line(x0, 465, x1 - 20, 465, ICE, 1, "4 6", .5)
    b += t(x0 + 10, 385, d["band"], 19, ICE, "start", 500)
    import random
    random.seed(7)
    pts = []
    for i in range(0, 61):
        x = x0 + 10 + i * 15.5
        y = 430 + 12 * math.sin(i * .7) + random.uniform(-7, 7)
        pts.append([x, y])
    sp = 42
    for k, dy in [(39, -40), (40, -120), (41, -205), (42, -150), (43, -60), (44, -10)]:
        pts[k][1] = 430 + dy
    base_a = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts[:40])
    spike = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts[38:46])
    base_b = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts[44:])
    b += f'<polyline points="{base_a}" fill="none" stroke="{ICE}" stroke-width="2.5" stroke-linejoin="round"/>'
    b += f'<polyline points="{base_b}" fill="none" stroke="{ICE}" stroke-width="2.5" stroke-linejoin="round"/>'
    px, py = pts[41]
    b += glow(px, py, 90)
    b += f'<polyline points="{spike}" fill="none" stroke="{GOLD}" stroke-width="3.5" stroke-linejoin="round"/>'
    b += circ(px, py, 7, GOLD, GOLD)
    b += line(px + 14, py - 4, px + 80, py - 30, GOLD, 1.5)
    b += t(px + 90, py - 34, d["spike"], 26, GOLD, "start", 600)
    b += t(px + 90, py - 6, d["spike2"], 19, SUB, "start")
    qx = pts[38][0]
    b += line(qx, yb, qx, 480, LINE, 1.5, "3 5", .6)
    b += t(qx, yb + 34, "?", 24, LINE, weight=600)
    return frame(2, title, take, b, lang)

def foot(x, y, ang, c):
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="11" ry="25" fill="none" stroke="{c}" stroke-width="2.5" transform="rotate({ang} {x:.1f} {y:.1f})"/>'

def f3(lang):
    title, take, d = L[lang][3]
    b = ""
    # paredes e porta
    b += path("M120,190 L1080,190 L1080,560 M1080,660 L1080,690 L120,690 Z".replace(" Z", ""), DIM, 3)
    b += path("M120,690 L120,190", DIM, 3)
    b += line(1080, 560, 1080, 660, GOLD, 3, "6 6", .7)
    b += t(1060, 545, d["door"], 18, GOLD, "end", 500)
    # pessoa A (tu), virada para a direita
    ax, ay = 360, 420
    b += f'<ellipse cx="{ax}" cy="{ay}" rx="34" ry="78" fill="#121216" stroke="{LINE}" stroke-width="2.5"/>'
    b += circ(ax + 4, ay, 30, LINE, "#16161a", 2.5)
    b += path(f"M{ax+34},{ay-7} L{ax+46},{ay} L{ax+34},{ay+7}", LINE, 2)
    b += foot(ax + 62, ay - 22, 90, LINE) + foot(ax + 62, ay + 22, 90, LINE)
    b += t(ax, ay + 128, d["you"], 22, TXT, weight=600)
    # pessoa B: tronco para A, pés para a saída
    bx, by = 740, 420
    b += f'<ellipse cx="{bx}" cy="{by}" rx="34" ry="78" fill="#121216" stroke="{ICE}" stroke-width="2.5"/>'
    b += circ(bx - 4, by, 30, ICE, "#16161a", 2.5)
    b += path(f"M{bx-34},{by-7} L{bx-46},{by} L{bx-34},{by+7}", ICE, 2)
    b += glow(bx + 50, by + 55, 90)
    b += foot(bx + 52, by + 62, -55, GOLD) + foot(bx + 76, by + 92, -55, GOLD)
    b += path(f"M{bx+90},{by+90} Q{bx+230},{by+200} 1066,612", GOLD, 2, dash="6 8", marker="aG")
    b += line(bx - 60, by - 95, bx - 20, by - 60, ICE, 1.5)
    b += t(bx - 66, by - 104, d["torso"], 21, ICE, "middle", 500)
    b += t(bx + 150, by + 25, d["feet"], 21, GOLD, "start", 600)
    return frame(4, title, take, b, lang)

def face(cx, cy, kind, c):
    r = 62
    s = circ(cx, cy, r, c, "#121216", 2.5)
    def brow(lx1, ly1, lx2, ly2):
        return (line(cx + lx1, cy + ly1, cx + lx2, cy + ly2, c, 3) +
                line(cx - lx1, cy + ly1, cx - lx2, cy + ly2, c, 3))
    def eyes(rr=5, squint=False):
        if squint:
            return path(f"M{cx-30},{cy-8} Q{cx-21},{cy-15} {cx-12},{cy-8}", c, 2.5) + path(f"M{cx+12},{cy-8} Q{cx+21},{cy-15} {cx+30},{cy-8}", c, 2.5)
        return circ(cx - 21, cy - 8, rr, c, c if rr <= 5 else "none", 2) + circ(cx + 21, cy - 8, rr, c, c if rr <= 5 else "none", 2)
    if kind == 0:   # alegria
        s += brow(-34, -28, -12, -30) + eyes(squint=True) + path(f"M{cx-26},{cy+18} Q{cx},{cy+44} {cx+26},{cy+18}", c, 3)
    elif kind == 1: # tristeza
        s += brow(-34, -24, -12, -32) + eyes() + path(f"M{cx-22},{cy+32} Q{cx},{cy+18} {cx+22},{cy+32}", c, 3)
    elif kind == 2: # raiva
        s += brow(-34, -32, -10, -20) + eyes() + line(cx - 20, cy + 28, cx + 20, cy + 28, c, 3)
    elif kind == 3: # medo
        s += brow(-34, -30, -12, -38) + eyes(8) + f'<ellipse cx="{cx}" cy="{cy+28}" rx="18" ry="7" fill="none" stroke="{c}" stroke-width="3"/>'
    elif kind == 4: # surpresa
        s += path(f"M{cx-34},{cy-30} Q{cx-23},{cy-44} {cx-12},{cy-32}", c, 3) + path(f"M{cx+12},{cy-32} Q{cx+23},{cy-44} {cx+34},{cy-30}", c, 3)
        s += eyes(8) + f'<ellipse cx="{cx}" cy="{cy+30}" rx="11" ry="15" fill="none" stroke="{c}" stroke-width="3"/>'
    elif kind == 5: # nojo
        s += brow(-34, -24, -12, -20) + eyes(squint=False) + path(f"M{cx-7},{cy+4} l4,-6 M{cx+7},{cy+4} l-4,-6", c, 2)
        s += path(f"M{cx-22},{cy+30} Q{cx-10},{cy+18} {cx},{cy+26} Q{cx+10},{cy+18} {cx+22},{cy+30}", c, 3)
    elif kind == 6: # desprezo: só um canto sobe
        s += brow(-34, -26, -12, -26) + eyes() + path(f"M{cx-22},{cy+28} L{cx+10},{cy+28} Q{cx+20},{cy+26} {cx+26},{cy+14}", c, 3)
        s += circ(cx + 26, cy + 14, 3, c, c)
    return s

def f4(lang):
    title, take, names = L[lang][4]
    b = ""
    xs = [130 + i * 157 for i in range(7)]
    for i, (x, nm) in enumerate(zip(xs, names)):
        c = GOLD if i == 6 else ICE
        if i == 6: b += glow(x, 400, 130)
        b += face(x, 400, i, c)
        b += t(x, 510, nm, 22, GOLD if i == 6 else TXT, weight=600)
    b += path(f"M{xs[6]+30},{318} Q{xs[6]+44},{350} {xs[6]+30},{396}", GOLD, 1.5, dash="3 5", marker="aG")
    b += t(xs[6], 300, "↑ 1 lado" if lang == "pt" else "↑ 1 side", 18, GOLD, weight=500)
    b += line(110, 580, 1090, 580, DIM, 1)
    b += t(600, 620, "< 0,5 s" if lang == "pt" else "< 0.5 s", 26, LINE, weight=300, ls=2)
    return frame(3, title, take, b, lang)

def f5(lang):
    title, take, d = L[lang][5]
    b = path("M1060,520 L1060,180 L140,180 L140,690 L1060,690 L1060,620", DIM, 3)
    b += t(1045, 650, d["door"], 18, SUB, "end")
    cx, cy, R = 470, 440, 135
    angs = [-90, -20, 40, 110, 165, 220]
    P = [(cx + R*math.cos(math.radians(a)), cy + R*math.sin(math.radians(a))) for a in angs]
    lx, ly = P[0]
    b += glow(lx, ly, 110)
    for i, (x, y) in enumerate(P):
        c = GOLD if i == 0 else ICE
        b += circ(x, y, 26, c, "#121216", 2.5)
        if i:
            dx, dy = lx - x, ly - y; n = math.hypot(dx, dy)
            b += line(x + dx/n*30, y + dy/n*30, x + dx/n*72, y + dy/n*72, GOLD, 2, op=.85, marker="aG")
    
    b += t(lx, ly - 22 - 48 + 70 - 70 - 0 + 0, "", 1)
    b += t(lx + 0, ly - 48 + 26, d["leader2"], 18, GOLD, op=.85) if False else ""
    b += t(lx, 222 - 18, d["leader2"], 18, GOLD, op=.85) if False else ""
    # aliança
    for (x, y) in [(800, 470), (870, 500)]:
        b += circ(x, y, 24, LINE, "#121216", 2.2, .8)
    b += line(822, 478, 846, 488, LINE, 2, op=.7) + line(848, 492, 824, 482, LINE, 2, op=.7)
    b += t(835, 555, d["pair"], 18, SUB)
    # isolado
    b += circ(970, 585, 24, ICE, "#121216", 2.2, .7, "4 4")
    b += line(990, 585, 1030, 585, ICE, 1.6, op=.6, marker="aI")
    b += t(940, 592, d["iso"], 18, ICE, "end", op=.85)
    return frame(5, title, take, b, lang).replace(
        f'>{escape(d["leader"])}<', f'>{escape(d["leader"])}<', 1)

def f5_fix(lang):
    svg = f5(lang)
    d = L[lang][5][2]
    cx, cy, R = 470, 440, 135
    lx, ly = cx, cy - R
    extra = t(lx, ly - 48 + 0, "", 1)
    sub = t(lx + 0, ly - 22 + 0 - 26 + 0 + 0 + 26 - 26, "", 1)
    add = t(lx, ly - 76, d["leader"], 21, GOLD, weight=600) + t(lx, ly - 50, d["leader2"], 18, GOLD, op=.85)
    return svg.replace("</svg>", add + "</svg>")

def f6(lang):
    title, take, items, mid = L[lang][6]
    b = ""
    cx, cy, R = 600, 415, 185
    angs = [-90, 0, 90, 180]
    for k in range(4):
        a1, a2 = angs[k] + 13, angs[(k + 1) % 4] - 13 + (360 if k == 3 else 0)
        c, w, m = (GOLD, 3.5, "aG") if k == 1 else (ICE, 2.2, "aI")
        b += path(arc(cx, cy, R, a1, a2), c, w, marker=m)
    for k, a in enumerate(angs):
        x, y = cx + R*math.cos(math.radians(a)), cy + R*math.sin(math.radians(a))
        c = GOLD if k == 2 else ICE
        if k == 2: b += glow(x, y, 90)
        b += circ(x, y, 13, c, c if k == 2 else BG, 2.5)
        nm, sub = items[k]
        if k == 0: b += t(x, y - 50, nm, 26, TXT, weight=600) + t(x, y - 24, sub, 18, SUB)
        if k == 1: b += t(x + 32, y - 6, nm, 26, TXT, "start", 600) + t(x + 32, y + 22, sub, 18, SUB, "start")
        if k == 2: b += t(x, y + 46, nm, 26, GOLD, weight=600) + t(x, y + 72, sub, 18, SUB)
        if k == 3: b += t(x - 32, y - 6, nm, 26, TXT, "end", 600) + t(x - 32, y + 22, sub, 18, SUB, "end")
    b += path(arc(cx, cy, 46, -60, 230), DIM, 2, marker="aL")
    b += t(cx, cy + 7, mid, 18, SUB, weight=500)
    return frame(6, title, take, b, lang)

def f7(lang):
    title, take, panels, d = L[lang][7]
    b = ""
    for p, (xc, (nm, sub)) in enumerate(zip([235, 600, 965], panels)):
        yc = 420
        fr = [(xc + 118*math.cos(math.radians(a)), yc + 118*math.sin(math.radians(a))) for a in (-150, -90, -30, 30, 90, 150)]
        mx, my = xc + 118*math.cos(math.radians(0)) * 0, yc
        # manipulador fica sempre à direita do "tu", ligado
        mx, my = xc + 62, yc + 4
        cut = {0: [], 1: [0, 2, 4], 2: [0, 1, 2, 3, 4, 5]}[p]
        for i, (x, y) in enumerate(fr):
            if i in cut:
                b += line(xc, yc, x, y, DIM, 1.5, "3 7", .7) if p == 1 else ""
                b += circ(x, y, 13, DIM, BG, 2, .8)
            else:
                b += line(xc, yc, x, y, ICE, 2, op=.8)
                b += circ(x, y, 13, ICE, BG, 2.2)
        b += circ(xc, yc, 20, TXT, "#16161a", 2.5)
        if p == 2: b += glow(mx, my, 70)
        b += line(xc + 20, yc + 2, mx - 14, my, GOLD, 3)
        b += circ(mx, my, 14, GOLD, GOLD, 2)
        b += t(xc, 238, nm, 26, TXT, weight=600)
        b += t(xc, 610, sub, 19, GOLD if p == 2 else SUB, italic=True, weight=500 if p == 2 else 400)
        if p < 2: b += line(xc + 150, yc, xc + 215, yc, DIM, 2, marker="aL")
    b += circ(150, 680, 8, TXT, "#16161a", 2) + t(166, 686, d["you"], 17, SUB, "start")
    b += circ(240, 680, 8, GOLD, GOLD) + t(256, 686, d["him"], 17, SUB, "start")
    return frame(7, title, take, b, lang)

def f8(lang):
    title, take, d = L[lang][8]
    b = ""
    x0, x1 = 330, 1080
    for row, (yb, lab, sub) in enumerate([(370, d["a"], d["a2"]), (600, d["b"], d["b2"])]):
        c = ICE if row == 0 else GOLD
        b += t(80, yb - 34, lab, 26, TXT if row == 0 else GOLD, "start", 600)
        b += t(80, yb - 6, sub, 18, SUB, "start")
        b += line(x0, yb, x1, yb, DIM, 2, marker="aL")
    for i in range(10):
        x = x0 + 30 + i * 72
        b += f'<rect x="{x}" y="{370-60}" width="16" height="60" rx="3" fill="{ICE}" opacity="0.8"/>'
    seq = [(0, 40), (95, 130), (130, 25), (300, 170), (390, 15), (560, 110), (600, 200), (700, 35)]
    top = 600
    for x, h in seq:
        b += f'<rect x="{x0+30+x}" y="{top-h}" width="16" height="{h}" rx="3" fill="{GOLD}" opacity="{0.55 + 0.45*h/200:.2f}"/>'
    # espera
    b += path(f"M{x0+30+430},{top-30} q30,-40 60,0 q30,40 60,0", GOLD, 1.5, dash="3 5", op=.7)
    b += t(x0 + 30 + 490, top - 62, "…?", 24, GOLD, weight=600)
    b += t(x1, top + 34, d["x"], 18, SUB, "end")
    return frame(8, title, take, b, lang)

def f9(lang):
    title, take, items, mid = L[lang][9]
    b = ""
    cx, cy, R = 600, 420, 200
    angs = [-90, -30, 30, 90, 150, 210]
    pts = [(cx + R*math.cos(math.radians(a)), cy + R*math.sin(math.radians(a))) for a in angs]
    b += path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z", DIM, 1.5, dash="2 6")
    b += glow(cx, cy, 140)
    for (x, y) in pts:
        dx, dy = cx - x, cy - y; n = math.hypot(dx, dy)
        b += line(x + dx/n*16, y + dy/n*16, cx - dx/n*80, cy - dy/n*80, ICE, 1.8, op=.75, marker="aI")
        b += circ(x, y, 11, ICE, BG, 2.5)
    for k, ((x, y), (nm, sub)) in enumerate(zip(pts, items)):
        if k == 0: b += t(x, y - 46, nm, 24, TXT, weight=600) + t(x, y - 22, sub, 17, SUB)
        elif k == 3: b += t(x, y + 42, nm, 24, TXT, weight=600) + t(x, y + 66, sub, 17, SUB)
        elif k in (1, 2): b += t(x + 26, y - 4, nm, 24, TXT, "start", 600) + t(x + 26, y + 22, sub, 17, SUB, "start")
        else: b += t(x - 26, y - 4, nm, 24, TXT, "end", 600) + t(x - 26, y + 22, sub, 17, SUB, "end")
    b += circ(cx, cy, 72, GOLD, "#121216", 3)
    b += t(cx, cy - 6, mid, 21, GOLD, weight=600)
    return frame(9, title, take, b, lang)

def f10(lang):
    title, take, rings, jump = L[lang][10]
    b = ""
    cx, cy = 470, 450
    rs = [58, 120, 182, 244]
    for i, r in enumerate(reversed(rs)):
        b += circ(cx, cy, r, ICE, "none", 2, op=.35 + .2*i, dash="3 7" if i == 0 else None)
    b += f'<circle cx="{cx}" cy="{cy}" r="58" fill="{ICE}" opacity="0.08"/>'
    for i, (r, nm) in enumerate(zip(rs, rings)):
        y = cy - r * math.sin(math.radians(35))
        x = cx + r * math.cos(math.radians(35))
        b += circ(x, y, 4, ICE, ICE)
        b += line(x + 8, y, 830, y, ICE, 1, "2 5", .4)
        b += t(845, y + 8, nm, 22, TXT, "start", 600 if i == 0 else 400, op=1 - .15*i)
    # salto
    gx, gy = cx - 330, cy + 120
    b += glow(cx - 30, cy + 12, 90)
    b += path(f"M{gx},{gy} Q{cx-150},{cy+150} {cx-40},{cy+18}", GOLD, 3, dash="7 7", marker="aG")
    b += circ(gx, gy, 10, GOLD, GOLD)
    b += t(gx - 30, gy + 48, jump, 21, GOLD, "start", 600, halo=True)
    return frame(10, title, take, b, lang)

FIGS = {1: f1, 2: f2, 3: f4, 4: f3, 5: f5_fix, 6: f6, 7: f7, 8: f8, 9: f9, 10: f10}

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for lang in ("pt", "en"):
        od = os.path.join(here, "out", lang); os.makedirs(od, exist_ok=True)
        for n, fn in FIGS.items():
            svg = fn(lang)
            open(os.path.join(od, f"fig{n:02d}.svg"), "w").write(svg)
            cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(od, f"fig{n:02d}.png"), output_width=2400)
    print("ok")
