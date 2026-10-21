"""Livro v3 completo. Uso: python3 book_v3.py pt"""
import os, re, sys, html
from weasyprint import HTML
import build as B
import pilot as P

PARTS = {
 "pt": [("I", "Ler", "O método. Antes de reconheceres predadores, tens de aprender a ver.", range(1, 8)),
        ("II", "Os Predadores", "Quem te quer usar raramente parece perigoso. Parece perfeito.", range(8, 16)),
        ("III", "Poder", "A manipulação não acontece só no amor. Acontece no trabalho, na família, nas amizades — e em cada compra que fazes.", range(16, 21)),
        ("IV", "Defesa", "Ver é metade. A outra metade é saber o que fazer quando vês.", range(21, 27))],
 "en": [("I", "Read", "The method. Before you can spot predators, you have to learn to see.", range(1, 8)),
        ("II", "The Predators", "People who want to use you rarely look dangerous. They look perfect.", range(8, 16)),
        ("III", "Power", "Manipulation doesn't only happen in love. It happens at work, in families, in friendships — and in every purchase you make.", range(16, 21)),
        ("IV", "Defence", "Seeing is half of it. The other half is knowing what to do when you see.", range(21, 27))],
}
WORDS = {"pt": dict(intro="Introdução", final="Palavras Finais", src="Fontes e Leituras",
                    src_intro="Os casos e conceitos deste guia vêm de investigação publicada, livros e reportagem documentada. A história da Inês é ficção. Para quem quiser ir mais fundo:",
                    disc="Este guia é educativo. Não substitui aconselhamento psicológico, médico ou jurídico. Sinais comportamentais não provam intenções nem servem para diagnosticar ninguém.", part="PARTE", enigma="O ENIGMA DA INÊS", ans="A Resposta"),
         "en": dict(intro="Introduction", final="Final Words", src="Sources and Further Reading",
                    src_intro="The cases and concepts in this guide come from published research, books and documented reporting. Inês's story is fiction. For anyone who wants to go deeper:",
                    disc="This guide is educational. It does not replace psychological, medical or legal advice. Behavioural signs don't prove intentions and must not be used to diagnose anyone.", part="PART", enigma="INÊS'S MYSTERY", ans="The Answer")}

def simple_section(lang, md, sid, label):
    head, _, body = md.strip().partition("\n")
    title = head[2:].split("—", 1)[-1].strip() if "—" in head else head[2:].strip()
    blocks = B.md_blocks(body)
    sec = B.chapter_open(lang, 0, title, sid)
    sec = sec.replace(f'<div class="ch-label">{B.S[lang]["chap"]}</div><div class="ch-no">00</div>', f'<div class="ch-label">{label}</div>')
    return sec + B.render(blocks) + "</section>"

def build(lang):
    L, W = B.S[lang], WORDS[lang]
    d = os.path.join(B.ROOT, lang, "v3")
    parts, entries = [], []
    parts.append(simple_section(lang, open(f"{d}/intro.md").read(), "intro", W["intro"].upper()))
    entries.append(("intro", W["intro"], "intro"))
    for no_r, name, sub, chs in PARTS[lang]:
        pid = "part" + no_r
        parts.append(B.part_page(lang, f"{W['part']} {no_r} — {name.upper()}", sub, pid).replace(f">{name.upper().capitalize()}<", f">{name}<"))
        entries.append(("part", f"{W['part']} {no_r} — {name.upper()}", pid))
        for n in chs:
            md = open(f"{d}/ch{n:02d}.md").read()
            title = md.split("\n", 1)[0].split("—", 1)[1].strip()
            parts.append(P.render_v3(lang, md, n))
            entries.append(("ch", f"{n} · {title}", f"ch{n}"))
    src = B.render(B.md_blocks(open(f"{d}/fontes.md").read()))
    parts.append(f'<section class="sources" id="sources"><h1 class="s-title" data-toc="{W["src"]}">{W["src"]}</h1>'
                 f'<p class="lead">{W["src_intro"]}</p>{src}<p class="disc">{W["disc"]}</p></section>')
    entries.append(("end", W["src"], "sources"))
    parts.append(simple_section(lang, open(f"{d}/resposta.md").read(), "answer", W["enigma"]))
    entries.append(("end", W["ans"], "answer"))
    fin = open(f"{d}/final.md").read()
    parts.append(simple_section(lang, fin, "final", "").replace('<div class="ch-label"></div>', ""))
    entries.append(("end", W["final"], "final"))
    body = B.cover(lang) + B.toc(lang, entries) + "".join(parts)
    page = B.page(lang, body, L["title1"] + " " + L["title2"]).replace("</style>", P.CSS_EXTRA + "\n.checklist ol{font-size:7.9pt}\n</style>")
    out = os.path.join(B.OUT, "v3_" + L["file_book"] + ".pdf")
    HTML(string=page, base_url=B.ROOT).write_pdf(out)
    return out

if __name__ == "__main__":
    print(build(sys.argv[1] if len(sys.argv) > 1 else "pt"))
