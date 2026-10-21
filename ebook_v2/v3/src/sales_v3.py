"""Amostra v3. Uso: python3 sales_v3.py"""
import os, re
from weasyprint import HTML
import build as B, pilot as P, sales as S

X = {
 "pt": dict(
  hook=["Uma rapariga de 27 anos muda-se para Lisboa. Emprego novo, casa nova, ninguém na cidade.",
        "Na primeira semana conhece três pessoas: uma colega que a ajuda em tudo, um rapaz nervoso que chega atrasado ao primeiro encontro e um vizinho calado que diz só uma palavra.",
        "Uma delas vai manipulá-la durante um ano.",
        "Nesta amostra conheces as três. Antes disso, aprendes o método para descobrires quem é."],
  inside_list=["**Capítulo 1 completo** — as três máscaras e a lacuna que as denuncia, com o caso real Theranos.",
               "**Episódio 1 da história da Inês** — o primeiro de 25. A resposta só aparece no último capítulo.",
               "**O que está no guia completo** — e um código só para quem leu até ao fim."],
  mid_title="Em quem confiarias?",
  mid_text="Guarda a tua resposta. No guia completo, a história continua durante 25 episódios — um no fim de cada capítulo, cada um a testar o que acabaste de aprender. No Capítulo 26 está a resposta e todas as pistas, episódio a episódio. Vê se acertas.",
  stats="26 capítulos · 25 casos reais · mais de 40 fontes · 10 ilustrações · 1 enigma · checklist de 50 sinais",
 ),
 "en": dict(
  hook=["A 27-year-old woman moves to Lisbon. New job, new flat, no one in the city.",
        "In her first week she meets three people: a colleague who helps her with everything, a nervous guy who turns up late to their first date, and a quiet neighbour who says only three words.",
        "One of them will manipulate her for a year.",
        "In this preview you'll meet all three. First, you'll learn the method to work out who it is."],
  inside_list=["**All of Chapter 1** — the three masks and the gap that gives them away, with the real Theranos case.",
               "**Episode 1 of Inês's story** — the first of 25. The answer only comes in the last chapter.",
               "**What's in the full guide** — plus a code only for people who read to the end."],
  mid_title="Who would you trust?",
  mid_text="Keep your answer. In the full guide, the story runs for 25 episodes — one at the end of every chapter, each testing what you've just learned. Chapter 26 has the answer and every clue, episode by episode. See if you get it right.",
  stats="26 chapters · 25 real cases · 40+ sources · 10 illustrations · 1 mystery · 50-sign checklist",
 )}

def sample(lang):
    s = dict(S.T[lang]); s.update(X[lang]); L = B.S[lang]; md = S.md
    d = os.path.join(B.ROOT, lang, "v3")
    parts = [B.cover(lang, badge=s["badge"])]
    parts.append(f'<section class="chapter hookpage"><div class="label">{s["hook_label"]}</div>' +
                 "".join(f'<p class="hook">{md(x)}</p>' for x in s["hook"][:2]) +
                 f'<blockquote>{md(s["hook"][2])}</blockquote><p class="hook">{md(s["hook"][3])}</p>'
                 f'<h3 class="gold" style="margin-top:9mm">{s["inside"].upper()}</h3><ul>' +
                 "".join(f"<li>{md(x)}</li>" for x in s["inside_list"]) + "</ul></section>")
    parts.append(P.render_v3(lang, open(f"{d}/ch01.md").read(), 1))
    parts.append(f'<section class="chapter midcta"><div class="ch-head"><div class="ch-label">{s["badge"]}</div>'
                 f'<h1 class="ch-title">{md(s["mid_title"])}</h1><div class="rule"></div></div><p class="hook">{md(s["mid_text"])}</p>'
                 + S.cta(lang) + "</section>")
    full = "".join(f'<div class="fullrow"><div class="k">{md(k)}</div><div class="v">{md(v)}</div></div>' for k, v in s["full"])
    items = re.findall(r"^\d+\. (.+)$", open(f"{d}/ch26.md").read(), flags=re.M)
    vis = "".join(f"<li>{md(x)}</li>" for x in items[:10])
    ghost = "".join(f"<li>{md(x)}</li>" for x in items[10:16])
    parts.append(f'<section class="chapter"><div class="ch-head"><div class="ch-label">{s["badge"]}</div><h1 class="ch-title">{md(s["full_title"])}</h1><div class="rule"></div></div>'
                 f'{full}<p class="stats">{md(s["stats"])}</p><p class="bonusline">{md(s["bonus"])}</p></section>'
                 f'<section class="chapter"><h3 style="margin-top:2mm">{md(s["check_title"]).upper()}</h3><ol class="peek">{vis}</ol><ol class="peek ghost" style="counter-reset: list-item 10">{ghost}</ol>'
                 f'<div class="more">{md(s["check_more"])}</div></section>')
    parts.append(f'<section class="chapter finalcta"><div class="psi-s">Ψ</div><h1 class="ch-title c">{md(s["final_title"])}</h1><div class="rule c"></div>'
                 + S.cta(lang) + f'<p class="social">{s["social"]}</p></section>')
    css = re.search(r'css_extra = """(.*?)"""', open(S.__file__).read(), re.S).group(1)
    html = B.page(lang, "".join(parts), L["title1"] + " " + L["title2"]).replace("</style>", P.CSS_EXTRA + css + "</style>")
    out = os.path.join(B.OUT, "v3_" + L["file_sample"] + ".pdf")
    HTML(string=html, base_url=B.ROOT).write_pdf(out)
    return out

if __name__ == "__main__":
    for lg in ("pt", "en"): print(sample(lg))
