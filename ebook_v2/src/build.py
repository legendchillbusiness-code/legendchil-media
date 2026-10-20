"""Gera livro, amostra e bónus (PT/EN) em PDF.
Uso: python3 build.py [pt|en|all]
Fontes: {pt,en}/base.md (texto) + {pt,en}/add.md (casos, pontes, capítulos novos, fontes)
"""
import re, sys, os, html
from weasyprint import HTML

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "out"); os.makedirs(OUT, exist_ok=True)

GOLD, ICE = "#b8975a", "#9fb4c8"

S = {
 "pt": dict(
   title1="LEIA QUALQUER PESSOA", title2="INSTANTANEAMENTE",
   sub="A Psicologia das Intenções Ocultas, dos Microssinais e das Máscaras Humanas",
   by="por", run="LEGENDCHIL · LEIA QUALQUER PESSOA INSTANTANEAMENTE",
   chap="CAPÍTULO", part="PARTE", toc="Índice", case="O CASO", why="PORQUE É QUE ISTO IMPORTA",
   use="USA ISTO", prot="PROTEGE-TE", help="AJUDA ALGUÉM", train="TREINO DE HOJE",
   fig="FIG.", sources="Fontes e Leituras", intro="Introdução", final="Palavras Finais",
   sources_intro="Os casos e conceitos deste guia vêm de investigação publicada, livros e reportagem documentada. Para quem quiser ir mais fundo:",
   file_book="Leia_Qualquer_Pessoa_Instantaneamente_PT", file_sample="Amostra_Gratis_Leia_Qualquer_Pessoa_PT",
   file_bonus="Bonus_Cabula_e_Red_Flags_PT", chword="Capítulo",
 ),
 "en": dict(
   title1="READ ANYONE", title2="INSTANTLY",
   sub="The Psychology of Hidden Intentions, Micro-Signals and Human Masks",
   by="by", run="LEGENDCHIL · READ ANYONE INSTANTLY",
   chap="CHAPTER", part="PART", toc="Contents", case="THE CASE", why="WHY THIS MATTERS",
   use="USE THIS", prot="PROTECT YOURSELF", help="HELP SOMEONE", train="TODAY'S PRACTICE",
   fig="FIG.", sources="Sources & Further Reading", intro="Introduction", final="Final Words",
   sources_intro="The cases and concepts in this guide come from published research, books and documented reporting. If you want to go deeper:",
   file_book="Read_Anyone_Instantly_EN", file_sample="Free_Preview_Read_Anyone_Instantly_EN",
   file_bonus="Bonus_Cheat_Sheet_and_Red_Flags_EN", chword="Chapter",
 ),
}

# capítulo antigo -> novo
def newno(o):
    o = int(o)
    if o <= 7: return o
    if o <= 22: return o + 1
    return o + 2

# figuras: capítulo antigo -> (fig, índice do ### antes do qual entra | 'end')
FIG_AT = {1: (1, 1), 2: (2, 2), 3: (3, 1), 4: (4, 1), 7: (5, 2), 9: (6, 2), 10: (7, 1), 13: (8, 2), 15: (9, 0), 21: (10, "end")}
WHY_AT = {1: 1, 2: 1, 3: 1, 4: 1, 9: 1, 11: 1, 12: 1}

# ---------------- markdown mínimo ----------------
def curly(t):
    t = re.sub(r'"(?=\w|\.\.\.|…|¿|¡)', "“", t)
    return t.replace('"', "”")

def inline(t):
    t = html.escape(curly(t), quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return t

def md_blocks(text):
    """devolve lista de (tipo, conteúdo)"""
    lines = text.split("\n"); i = 0; out = []
    while i < len(lines):
        l = lines[i].rstrip()
        if not l.strip(): i += 1; continue
        if l.startswith("### "): out.append(("h3", l[4:].strip())); i += 1; continue
        if l.startswith("# "): out.append(("h1", l[2:].strip())); i += 1; continue
        if l.startswith("> "): out.append(("quote", l[2:].strip())); i += 1; continue
        if l.startswith(":::"): out.append(("marker", l[3:].strip())); i += 1; continue
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.match(r"^\|(-+\|)+$", lines[i].strip()):
                    rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append(("table", rows)); continue
        if l.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:].strip()); i += 1
            out.append(("ul", items)); continue
        m = re.match(r"^(\d+)\. (.+)", l)
        if m and not l.startswith("**"):
            items = []; start = int(m.group(1))
            while i < len(lines):
                m = re.match(r"^(\d+)\. (.+)", lines[i])
                if m: items.append(m.group(2).strip()); i += 1; continue
                if not lines[i].strip() and i + 1 < len(lines) and re.match(r"^\d+\. ", lines[i + 1]): i += 1; continue
                break
            out.append(("ol", (start, items))); continue
        out.append(("p", l.strip())); i += 1
    return out

def render(blocks):
    h = []
    for k, v in blocks:
        if k == "h3": h.append(f"<h3>{inline(v)}</h3>")
        elif k == "p":
            if v.startswith("*") and v.endswith("*") and not v.startswith("**"): h.append(f'<p class="lead">{inline(v[1:-1])}</p>')
            else: h.append(f"<p>{inline(v)}</p>")
        elif k == "quote": h.append(f'<blockquote>{inline(v)}</blockquote>')
        elif k == "ul": h.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in v) + "</ul>")
        elif k == "ol": h.append(f'<ol style="counter-reset: list-item {v[0]-1}">' + "".join(f"<li>{inline(x)}</li>" for x in v[1]) + "</ol>")
        elif k == "table":
            rows = v
            h.append('<table><thead><tr>' + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr></thead><tbody>" +
                     "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:]) + "</tbody></table>")
        elif k == "raw": h.append(v)
    return "\n".join(h)

# ---------------- leitura das fontes ----------------
def load(lang):
    base = open(os.path.join(ROOT, lang, "base.md")).read()
    add = open(os.path.join(ROOT, lang, "add.md")).read()
    secs = re.split(r"\n(?=# )", "\n" + base)
    sections = []
    for s in secs:
        s = s.strip()
        if not s: continue
        head, _, body = s.partition("\n")
        sections.append((head[2:].strip(), body.strip()))
    adds = {}
    for blk in re.split(r"^== ", add, flags=re.M):
        if not blk.strip(): continue
        key, _, body = blk.partition("\n")
        key = key.strip()
        if key.startswith("new:") or key == "fontes":
            adds[key] = body.strip(); continue
        parts = {}
        for m in re.finditer(r"^\[(\w+)\]\n(.*?)(?=^\[\w+\]\n|\Z)", body, flags=re.M | re.S):
            parts[m.group(1)] = m.group(2).strip()
        adds[key] = parts
    return sections, adds

def remap_refs(text, lang):
    w = S[lang]["chword"]
    return re.sub(rf"({w}) (\d+)", lambda m: f"{m.group(1)} {newno(m.group(2))}", text)

# ---------------- peças ----------------
def fig_html(lang, n):
    p = os.path.join(ROOT, "illus", "out", lang, f"fig{n:02d}.png")
    return f'<figure><img src="file://{p}"/></figure>'

def case_html(lang, t):
    return f'<div class="case"><div class="label">{S[lang]["case"]}</div>' + "".join(f"<p>{inline(x)}</p>" for x in t.split("\n\n")) + "</div>"

def why_html(lang, t):
    return f'<div class="why"><h3 class="gold">{S[lang]["why"]}</h3><p>{inline(t)}</p></div>'

def use_html(lang, prot, hlp):
    L = S[lang]
    return (f'<div class="use"><div class="label">{L["use"]}</div>'
            f'<div class="row"><div class="k ice">{L["prot"]}</div><div class="v">{inline(prot)}</div></div>'
            f'<div class="row"><div class="k gold">{L["help"]}</div><div class="v">{inline(hlp)}</div></div></div>')

def train_html(lang, paras):
    return f'<div class="train"><div class="label">{S[lang]["train"]}</div>' + "".join(f"<p>{inline(p)}</p>" for p in paras) + "</div>"

def chapter_open(lang, no, title, cid):
    L = S[lang]
    return (f'<section class="chapter" id="{cid}"><div class="ch-head"><div class="ch-label">{L["chap"]}</div>'
            f'<div class="ch-no">{no:02d}</div><h1 class="ch-title" data-toc="{html.escape(title)}">{inline(title)}</h1><div class="rule"></div></div>')

def build_chapter(lang, old, title, body, adds, opts=None):
    """capítulo existente com as peças novas inseridas"""
    opts = opts or {}
    a = adds.get(str(old), {})
    no = newno(old)
    body = remap_refs(body, lang)
    blocks = md_blocks(body)
    # separa treino
    train = []
    if ("marker", "treino") in blocks:
        k = blocks.index(("marker", "treino"))
        train = [v for t, v in blocks[k + 1:] if t == "p"]
        blocks = blocks[:k]
    h3idx = [i for i, (t, _) in enumerate(blocks) if t == "h3"]
    inserts = {}
    def put(idx, htmlpiece, first=False):
        pos = len(blocks) if idx == "end" or idx >= len(h3idx) else h3idx[idx]
        inserts.setdefault(pos, [])
        (inserts[pos].insert(0, htmlpiece) if first else inserts[pos].append(htmlpiece))
    if "caso" in a: put(0, case_html(lang, a["caso"]), first=True)
    if old in FIG_AT:
        f, idx = FIG_AT[old]; put(idx, fig_html(lang, f))
    if "porque" in a: put(WHY_AT.get(old, 0), why_html(lang, a["porque"]))
    trunc = opts.get("trunc")
    if trunc:
        hi, n = trunc
        j = next(x for x in range(h3idx[hi], len(blocks)) if blocks[x][0] == "ul")
        blocks = blocks[:j] + [("ul", blocks[j][1][:n])]
    out = []
    for i, b in enumerate(blocks):
        if i in inserts: out += [("raw", x) for x in inserts[i]]
        out.append(b)
    if trunc:
        out.append(("raw", opts["cut_html"]))
    else:
        if len(blocks) in inserts: out += [("raw", x) for x in inserts[len(blocks)]]
        if "protege" in a and not opts.get("no_use"): out.append(("raw", use_html(lang, a["protege"], a["ajuda"])))
        if train and not opts.get("no_train"): out.append(("raw", train_html(lang, train)))
    cls = ' checklist' if old == 24 else ''
    return chapter_open(lang, no, title, f"ch{no}").replace('class="chapter"', f'class="chapter{cls}"') + render(out) + "</section>"

def build_new(lang, key, no, adds):
    t = adds[key]
    head, _, body = t.partition("\n")
    title = head.split("—", 1)[1].strip()
    m = re.search(r":::usa\n\[protege\]\n(.*?)\n\[ajuda\]\n(.*?)\n:::", body, re.S)
    use = use_html(lang, m.group(1).strip(), m.group(2).strip()) if m else ""
    body = body[:m.start()] + "%%USE%%" + body[m.end():] if m else body
    m2 = re.search(r":::treino\n(.*?)\n:::", body, re.S)
    train = train_html(lang, [m2.group(1).strip()]) if m2 else ""
    body = body[:m2.start()] + body[m2.end():] if m2 else body
    blocks = md_blocks(body)
    # o 1.º "### PORQUE…" ganha estilo dourado
    out = []
    for k, v in blocks:
        if k == "p" and v == "%%USE%%": out.append(("raw", use)); continue
        if k == "h3" and v.upper() in (S["pt"]["why"], S["en"]["why"]): out.append(("raw", f'<h3 class="gold">{v}</h3>')); continue
        out.append((k, v))
    out.append(("raw", train))
    return chapter_open(lang, no, title, f"ch{no}") + render(out) + "</section>"

def part_page(lang, head, sub, pid):
    m = re.match(r"(PARTE|PART) ([IV]+) — (.+)", head)
    return (f'<section class="partpage" id="{pid}"><div class="p-no">{S[lang]["part"]} {m.group(2)}</div>'
            f'<h1 class="p-title" data-toc="{html.escape(head)}">{m.group(3).title() if lang=="en" else m.group(3).capitalize()}</h1>'
            f'<div class="rule c"></div><p class="p-sub">{inline(sub.strip("*"))}</p></section>')

def cover(lang, sample=False, badge=None):
    L = S[lang]
    b = f'<div class="badge">{badge}</div>' if badge else ""
    return (f'<section class="cover"><div class="frame"></div>{b}<div class="psi">Ψ</div><div class="t1">{L["title1"]}</div><div class="t2">{L["title2"]}</div>'
            f'<div class="rule c"></div><div class="csub">{L["sub"]}</div><div class="by">{L["by"]} LEGENDCHIL</div></section>')

def toc(lang, entries):
    L = S[lang]
    rows = []
    for kind, label, ref in entries:
        if kind == "part": rows.append(f'<li class="tp"><a href="#{ref}">{inline(label)}</a></li>')
        else: rows.append(f'<li class="tc {kind}"><a href="#{ref}">{inline(label)}</a></li>')
    return f'<section class="toc"><h2>{L["toc"]}</h2><ul>{"".join(rows)}</ul></section>'

CSS = open(os.path.join(ROOT, "book.css")).read()

def page(lang, body, title):
    css = CSS.replace("%RUN%", S[lang]["run"]).replace("%FONTS%", os.path.join(ROOT, "fonts"))
    return f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{title}</title><style>{css}</style></head><body>{body}</body></html>'

# ---------------- livro ----------------
def intro_html(lang, body, adds):
    if lang == "pt":
        body = body.replace("reforço intermitente, regresso.", "reforço intermitente, regresso — e porque é que te escolhem a ti.")
        body = body.replace("como sair, como treinar.", "como sair, como ajudar alguém que está preso, como treinar.")
        how = ("### COMO ESTÁ CONSTRUÍDO CADA CAPÍTULO\n\n- **O caso** — uma história real e documentada, para veres o padrão em ação.\n"
               "- **Porque é que isto importa** — o que perdes se não souberes ver.\n- **Os sinais** — o que procurar, em concreto.\n"
               "- **Usa isto** — uma forma de te protegeres e uma forma de ajudares alguém.\n- **Treino de hoje** — dez minutos no mundo real.\n\n")
        body = body.replace("### O QUE ESTE GUIA NÃO É", how + "### O QUE ESTE GUIA NÃO É")
        body = body.replace("Cada capítulo termina com um **Treino de hoje** — um exercício curto para aplicares no mundo real. ", "")
    else:
        body = body.replace("intermittent reinforcement, hoovering.", "intermittent reinforcement, hoovering — and why they choose you.")
        body = body.replace("how to leave, how to train.", "how to leave, how to help someone who's trapped, how to train.")
        how = ("### HOW EACH CHAPTER WORKS\n\n- **The case** — a real, documented story, so you see the pattern in action.\n"
               "- **Why this matters** — what you lose if you can't see it.\n- **The signs** — exactly what to look for.\n"
               "- **Use this** — one way to protect yourself and one way to help someone else.\n- **Today's practice** — ten minutes in the real world.\n\n")
        body = body.replace("### WHAT THIS GUIDE IS NOT", how + "### WHAT THIS GUIDE IS NOT")
        body = body.replace("Every chapter ends with **Today's practice** — a short exercise for the real world. ", "")
    g = adds["intro"]["gancho"]
    hook = "".join(f'<p class="hook">{inline(x)}</p>' for x in g.split("\n\n"))
    return hook + render(md_blocks(body))

def build_book(lang):
    L = S[lang]
    sections, adds = load(lang)
    parts, entries = [], []
    for head, body in sections:
        if head.startswith(("INTRODU",)):
            t = head.split("—", 1)[1].strip().capitalize()
            parts.append(chapter_open(lang, 0, t, "intro").replace(f'<div class="ch-label">{L["chap"]}</div><div class="ch-no">00</div>', f'<div class="ch-label">{L["intro"].upper()}</div>')
                         + intro_html(lang, body, adds) + "</section>")
            entries.append(("intro", L["intro"], "intro"))
        elif head.startswith(("PARTE", "PART ")):
            pid = "part" + head.split()[1]
            parts.append(part_page(lang, head, body, pid))
            entries.append(("part", head, pid))
            if head.split()[1] == "II":
                parts.append(build_new(lang, "new:alvo", 8, adds))
                entries.append(("ch", f"8 · {adds['new:alvo'].split('—',1)[1].split(chr(10))[0].strip()}", "ch8"))
        elif re.match(r"(Capítulo|Chapter) \d+", head):
            old = int(re.match(r"\w+ (\d+)", head).group(1))
            title = head.split("—", 1)[1].strip()
            if old == 23:
                parts.append(build_new(lang, "new:ajudar", 24, adds))
                entries.append(("ch", f"24 · {adds['new:ajudar'].split('—',1)[1].split(chr(10))[0].strip()}", "ch24"))
            parts.append(build_chapter(lang, old, title, body, adds))
            entries.append(("ch", f"{newno(old)} · {title}", f"ch{newno(old)}"))
        else:  # palavras finais
            fin_blocks = md_blocks(body)
            disc = [b for b in fin_blocks if b[0] == "p" and b[1].startswith(("Este guia é educativo", "This guide is educational"))]
            fin_blocks = [b for b in fin_blocks if b not in disc]
            parts.append(chapter_open(lang, 0, L["final"], "final").replace(f'<div class="ch-label">{L["chap"]}</div><div class="ch-no">00</div>', "")
                         + render(fin_blocks) + "</section>")
            entries.append(("end", L["final"], "final"))
            src = render(md_blocks(adds["fontes"]))
            parts.append(f'<section class="sources" id="sources"><h1 class="s-title" data-toc="{L["sources"]}">{L["sources"]}</h1>'
                         f'<p class="lead">{L["sources_intro"]}</p>{src}<p class="disc">{inline(disc[0][1]) if disc else ""}</p></section>')
            entries.append(("end", L["sources"], "sources"))
    body = cover(lang) + toc(lang, entries) + "".join(parts)
    out = os.path.join(OUT, L["file_book"] + ".pdf")
    HTML(string=page(lang, body, L["title1"] + " " + L["title2"]), base_url=ROOT).write_pdf(out)
    return out

if __name__ == "__main__":
    langs = ["pt", "en"] if len(sys.argv) < 2 or sys.argv[1] == "all" else [sys.argv[1]]
    for lg in langs:
        print(build_book(lg))
