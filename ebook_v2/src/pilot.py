"""Capítulo-piloto v3 (caso como fio condutor + caixas de investigação). Uso: python3 pilot.py pt/ch01_v3.md pt"""
import re, sys, os, html
from weasyprint import HTML
import build as B

def render_v3(lang, md, no):
    return render_v3_core(lang, md, no)

def render_v3_core(lang, md, no):
    L = B.S[lang]
    head, _, body = md.strip().partition("\n")
    title = head.split("—", 1)[1].strip()
    raws = []
    def keep(h):
        raws.append(h); return f"\n\n%%RAW{len(raws)-1}%%\n\n"
    def estudo(m):
        lines = [x for x in m.group(1).strip().split("\n") if x.strip()]
        lab, txt, src = lines[0], " ".join(lines[1:-1]), lines[-1]
        return keep(f'<div class="study"><div class="slabel">{"O QUE DIZ A INVESTIGAÇÃO" if lang=="pt" else "WHAT THE RESEARCH SAYS"}</div>'
                    f'<div class="stitle">{B.inline(lab)}</div><p>{B.inline(txt)}</p><div class="ssrc">{B.inline(src)}</div></div>')
    body = re.sub(r":::estudo\n(.*?)\n:::", estudo, body, flags=re.S)
    def episodio(m):
        lines = m.group(1).strip().split("\n", 1)
        paras = "".join(f"<p>{B.inline(x.strip())}</p>" for x in lines[1].split("\n\n") if x.strip())
        return keep(f'<div class="episode"><div class="elabel">{B.inline(lines[0])}</div>{paras}</div>')
    body = re.sub(r":::episodio\n(.*?)\n:::", episodio, body, flags=re.S)
    body = re.sub(r":::resposta\n(.*?)\n:::", lambda m: keep(f'<div class="answer"><div class="alabel">{"RESPOSTA DO EPISÓDIO ANTERIOR" if lang=="pt" else "ANSWER TO THE LAST EPISODE"}</div><p>{B.inline(m.group(1).strip())}</p></div>'), body, flags=re.S)
    body = re.sub(r":::fig (\d+):::", lambda m: keep(B.fig_html(lang, int(m.group(1)))), body)
    def usa(m): return keep(B.use_html(lang, m.group(1).strip(), m.group(2).strip()))
    body = re.sub(r":::usa\n\[protege\]\n(.*?)\n\[ajuda\]\n(.*?)\n:::", usa, body, flags=re.S)
    body = re.sub(r":::treino\n(.*?)\n:::", lambda m: keep(B.train_html(lang, [m.group(1).strip()])), body, flags=re.S)
    out = []
    first = True
    for k, v in B.md_blocks(body):
        if k == "p" and re.fullmatch(r"%%RAW(\d+)%%", v):
            out.append(("raw", raws[int(v[5:-2])])); continue
        if k == "h3" and v.startswith(("PORQUE É QUE ISTO IMPORTA", "WHY THIS MATTERS")):
            out.append(("raw", f'<h3 class="gold">{v}</h3>')); continue
        if k == "p" and first:
            out.append(("raw", f'<p class="scene">{B.inline(v)}</p>')); first = False; continue
        out.append((k, v))
    return B.chapter_open(lang, no, title, f"ch{no}") + B.render(out) + "</section>"

CSS_EXTRA = """
.answer { margin: 0 0 6mm; padding: 3mm 4mm 1mm; border-left: 1.2pt solid #b8975a; background: #12110e; }
.answer .alabel { font-size: 6pt; font-weight: 700; letter-spacing: .3em; color: #b8975a; margin-bottom: 1.5mm; }
.answer p { font-size: 8.4pt; color: #d9d3c6; }
.episode { break-before: page; margin: 2mm 0 5mm; padding: 5mm 5.5mm 2mm; background: #141210; border: .5pt solid #3a3226; border-top: 1.6pt solid #b8975a; break-inside: auto; }
.episode .elabel { font-size: 6.6pt; font-weight: 700; letter-spacing: .32em; color: #b8975a; margin-bottom: 3mm; }
.episode p { font-family: "Corm"; font-weight: 500; font-size: 11.2pt; line-height: 1.45; color: #ebe6dc; }
.episode p:last-child { font-family: Inter; font-size: 8.8pt; color: #d9c9a6; border-top: .4pt solid #3a3226; padding-top: 3mm; }
.scene { font-size: 10pt; color: #e8e8ee; }
.scene { font-family: "Corm"; font-style: italic; font-weight: 500; font-size: 12.2pt; line-height: 1.42; }
.study { border: .5pt solid #2f3640; border-left: 1.4pt solid #9fb4c8; background: #10131a; padding: 4mm 5mm 3mm; margin: 5mm 0; break-inside: avoid; }
.study .slabel { font-size: 6.2pt; font-weight: 700; letter-spacing: .3em; color: #9fb4c8; }
.study .stitle { font-family: "Corm"; font-weight: 600; font-size: 12.5pt; color: #f3f3f6; margin: 1.5mm 0 2mm; }
.study p { font-size: 8.8pt; margin-bottom: 2mm; }
.study .ssrc { font-size: 7pt; color: #7c7c88; }
"""

def build_many(lang, files, outname):
    body = ""
    for f in files:
        md = open(os.path.join(B.ROOT, f)).read()
        no = int(re.search(r"(\d+)", os.path.basename(f).split("_")[0]).group(1))
        body += render_v3(lang, md, no)
    page = B.page(lang, body, outname).replace("</style>", CSS_EXTRA + "</style>")
    out = os.path.join(B.OUT, outname + ".pdf")
    HTML(string=page, base_url=B.ROOT).write_pdf(out)
    return out

if __name__ == "__main__" and sys.argv[1] == "many":
    print(build_many(sys.argv[2], sys.argv[4:], sys.argv[3])); sys.exit()

if __name__ == "__main__":
    src, lang = sys.argv[1], sys.argv[2]
    md = open(os.path.join(B.ROOT, src)).read()
    no = int(re.search(r"(\d+)", os.path.basename(src).split("_")[0]).group(1))
    body = render_v3(lang, md, no)
    page = B.page(lang, body, "Piloto").replace("</style>", CSS_EXTRA + "</style>")
    out = os.path.join(B.OUT, f"Capitulo{no:02d}_piloto_{lang.upper()}.pdf")
    HTML(string=page, base_url=B.ROOT).write_pdf(out)
    print(out, len(re.findall(r"\w+", md)), "palavras")
