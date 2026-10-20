"""Amostra de venda + bónus (cábula A4 + red flags). Uso: python3 sales.py"""
import os, re
from weasyprint import HTML
import build as B

T = {
 "pt": dict(
  badge="AMOSTRA GRATUITA", code="MENTE20",
  url="https://legendchil.gumroad.com/l/leia-qualquer-pessoa/MENTE20",
  hook_label="ANTES DE COMEÇARES",
  hook=["Em 2018, uma mulher conheceu no Tinder um homem que dizia ser filho de um magnata dos diamantes. No primeiro encontro, levou-a de jato privado.",
        "Seguiram-se semanas de mensagens a toda a hora, declarações rápidas, planos para o futuro. Depois veio a crise: inimigos, cartões bloqueados, um pedido urgente de dinheiro. Ela emprestou. Não foi a única.",
        "Os sinais estavam lá desde o primeiro dia. Ela só não sabia o que estava a ver.",
        "Nesta amostra vais ver os primeiros."],
  inside="Nesta amostra", inside_list=["**Capítulo 1 completo** — as três máscaras e a lacuna que as denuncia.", "**Parte do Capítulo 10** — o love bombing, com o caso real que abriu esta página.", "**O que está no guia completo** — e um código só para quem leu até ao fim."],
  mid_title="Gostaste do Capítulo 1?",
  mid_text="O guia completo tem mais 25 capítulos assim. O próximo que vais ler é sobre a tática que esta mulher não viu chegar.",
  cut_lock="FIM DA AMOSTRA DESTE CAPÍTULO",
  cut_text="Os outros 3 sinais — incluindo o que quase toda a gente ignora — estão no guia completo. Tal como a forma de distinguir amor real de love bombing, e o que fazer se te estiver a acontecer.",
  full_title="Dentro do guia completo",
  full=[("Parte I · Ler", "Como perceber quando alguém mente sem cair nos mitos (braços cruzados não querem dizer nada). Os pés, a voz, as palavras, as mensagens de texto. Ler qualquer sala em 60 segundos."),
        ("Parte II · Os Predadores", "Porque é que te escolhem a ti. A tríade negra. Os 6 sinais do love bombing. Isolamento, gaslighting, triangulação — e o mecanismo que te impede de sair."),
        ("Parte III · Poder", "Os 6 gatilhos de Cialdini que te fazem dizer “sim”. Manipulação no trabalho e na família. Interesse real vs. falso. Os 5 sinais que anunciam a traição."),
        ("Parte IV · Defesa", "Frases prontas para cada tática. Limites que não se negoceiam. Como sair e não voltar. Como ajudar alguém que está preso. Protocolo de treino de 7 dias.")],
  stats="26 capítulos · 10 ilustrações · 10 casos reais e estudos · checklist de 50 sinais",
  bonus="Bónus: cábula imprimível dos 50 sinais + teste das 15 red flags.",
  check_title="Uma espreitadela na checklist final",
  check_more="+ 40 sinais no guia completo",
  final_title="Lê as pessoas antes que elas te leiam a ti.",
  final_text="Código exclusivo para quem leu a amostra:",
  btn="Quero o guia completo com 20% de desconto →",
  small="Pagamento seguro via Gumroad · PDF para ler no telemóvel, tablet ou computador",
  social="Instagram @legendchil · TikTok @legendchil",
  # bónus
  b_title="Cábula · 50 Sinais", b_sub="Imprime, guarda no telemóvel, relê antes de conversas importantes.",
  b_rule="Nenhum sinal isolado prova nada. Procura padrões, considera o contexto, faz perguntas.",
  r_title="15 Red Flags", r_sub="Responde sobre alguém novo na tua vida — um par, um amigo, um sócio, um chefe. Conta os “sim”.",
  r_q=[("Em poucas semanas, já se fala de futuro, de morar juntos ou de “alma gémea”?", 10),
       ("Há mágoa, insistência ou culpa quando dizes “não” ou pedes calma?", 10),
       ("Sabes muito sobre o que essa pessoa sente por ti, mas pouco sobre a vida dela?", 10),
       ("Os ex, antigos sócios ou amigos de antes são todos “loucos”, “invejosos” ou “traidores”?", 9),
       ("As regras que exige aos outros não se aplicam a ela?", 9),
       ("Fala mal das pessoas de quem gostas ou cria tensão quando vais estar com elas?", 11),
       ("Desde que a conheceste, vês menos os teus amigos?", 11),
       ("Já te disse “eu nunca disse isso” sobre algo que tens a certeza de que disse?", 12),
       ("Dás por ti a pedir desculpa sem saber bem porquê?", 12),
       ("Fala de outras pessoas de uma forma que te deixa a competir ou com ciúmes?", 13),
       ("Alterna entre carinho total e frieza sem razão clara?", 14),
       ("Usa o silêncio como castigo até cederes?", 14),
       ("Pressiona-te a decidir já — dinheiro, compromissos, favores?", 16),
       ("Faz-te favores que não pediste e depois cobra-os?", 16),
       ("Depois de estares com essa pessoa, sentes-te mais pequeno, cansado ou ansioso?", 18)],
  r_score=[("0–2", "Provavelmente normal. Continua a observar."), ("3–5", "Abranda. Nenhuma decisão grande e fala com alguém de confiança."), ("6+", "Protege-te. Relê os capítulos indicados e conta a alguém do teu círculo interior.")],
  r_note="Uma resposta sozinha não prova nada — o que conta é o padrão. Se há violência ou ameaças: APAV 116 006 (gratuito) · perigo imediato: 112.",
  chref="Cap.", yes="SIM",
 ),
 "en": dict(
  badge="FREE PREVIEW", code="MIND20",
  url="https://legendchil.gumroad.com/l/readanyone/MIND20",
  hook_label="BEFORE YOU START",
  hook=["In 2018, a woman met a man on Tinder who said he was the son of a diamond tycoon. On their first date, he flew her on a private jet.",
        "Then came weeks of constant messages, fast declarations, plans for the future. Then the crisis: enemies, blocked cards, an urgent request for money. She lent it. She wasn't the only one.",
        "The signs were there from day one. She just didn't know what she was looking at.",
        "In this preview, you'll see the first ones."],
  inside="In this preview", inside_list=["**All of Chapter 1** — the three masks and the gap that gives them away.", "**Part of Chapter 10** — love bombing, with the real case that opened this page.", "**What's in the full guide** — plus a code only for people who read to the end."],
  mid_title="Liked Chapter 1?",
  mid_text="The full guide has 25 more chapters like it. The next one you'll read is about the tactic that woman never saw coming.",
  cut_lock="END OF THIS CHAPTER'S PREVIEW",
  cut_text="The other 3 signs — including the one almost everyone ignores — are in the full guide. So is how to tell real love from love bombing, and what to do if it's happening to you.",
  full_title="Inside the full guide",
  full=[("Part I · Read", "How to tell when someone's lying without falling for the myths (crossed arms mean nothing). Feet, voice, words, text messages. Reading any room in 60 seconds."),
        ("Part II · The Predators", "Why they choose you. The Dark Triad. The 6 signs of love bombing. Isolation, gaslighting, triangulation — and the mechanism that stops you leaving."),
        ("Part III · Power", "Cialdini's 6 triggers that make you say “yes”. Manipulation at work and in families. Real vs. fake interest. The 5 signs that come before betrayal."),
        ("Part IV · Defense", "Ready-made lines for every tactic. Non-negotiable boundaries. How to leave and not go back. How to help someone who's trapped. A 7-day training protocol.")],
  stats="26 chapters · 10 illustrations · 10 real cases and studies · 50-sign checklist",
  bonus="Bonus: printable 50-sign cheat sheet + the 15 red flags test.",
  check_title="A peek at the final checklist",
  check_more="+ 40 more signs in the full guide",
  final_title="Read people before they read you.",
  final_text="Exclusive code for preview readers:",
  btn="Get the full guide with 20% off →",
  small="Secure checkout via Gumroad · PDF for phone, tablet or computer",
  social="Instagram @legendchil · TikTok @legendchil",
  b_title="Cheat Sheet · 50 Signs", b_sub="Print it, save it to your phone, reread it before important conversations.",
  b_rule="No single sign proves anything. Look for patterns, consider the context, ask questions.",
  r_title="15 Red Flags", r_sub="Answer about someone new in your life — a partner, a friend, a business partner, a boss. Count the “yes” answers.",
  r_q=[("Within a few weeks, is there already talk of the future, moving in, or being “soulmates”?", 10),
       ("Is there hurt, pushing or guilt when you say “no” or ask to slow down?", 10),
       ("Do you know a lot about how they feel about you, but little about their actual life?", 10),
       ("Are all their exes, former partners or old friends “crazy”, “jealous” or “traitors”?", 9),
       ("Do the rules they demand of others not apply to them?", 9),
       ("Do they badmouth the people you love, or create tension when you're going to see them?", 11),
       ("Since you met them, do you see your friends less?", 11),
       ("Have they said “I never said that” about something you're sure they said?", 12),
       ("Do you find yourself apologising without quite knowing why?", 12),
       ("Do they talk about other people in a way that leaves you competing or jealous?", 13),
       ("Do they swing between total affection and coldness for no clear reason?", 14),
       ("Do they use silence as punishment until you give in?", 14),
       ("Do they push you to decide right now — money, commitments, favours?", 16),
       ("Do they do you favours you didn't ask for, then collect on them?", 16),
       ("After time with them, do you feel smaller, drained or anxious?", 18)],
  r_score=[("0–2", "Probably normal. Keep observing."), ("3–5", "Slow down. No big decisions, and talk to someone you trust."), ("6+", "Protect yourself. Reread the chapters listed and tell someone in your inner circle.")],
  r_note="One answer alone proves nothing — the pattern is what counts. If there's violence or threats, contact a local victim-support service. In immediate danger, call 112 (Europe) or 911 (US).",
  chref="Ch.", yes="YES",
 ),
}

def md(t): return B.inline(t)

def cta(lang, big=True):
    s = T[lang]
    return (f'<div class="cta"><div class="label">{md(s["final_text"]).upper() if not big else md(s["final_text"])}</div>'
            f'<div class="code">{s["code"]}</div><a class="btn" href="{s["url"]}">{s["btn"]}</a>'
            f'<div class="small">{s["small"]}</div></div>')

def sample(lang):
    s, L = T[lang], B.S[lang]
    sections, adds = B.load(lang)
    sec = {h: b for h, b in sections}
    def find(old):
        for h, b in sections:
            m = re.match(r"(Capítulo|Chapter) (\d+) — (.+)", h)
            if m and int(m.group(2)) == old: return m.group(3), b
    parts = [B.cover(lang, badge=s["badge"])]
    # gancho
    parts.append(f'<section class="chapter hookpage"><div class="label">{s["hook_label"]}</div>' +
                 "".join(f'<p class="hook">{md(x)}</p>' for x in s["hook"][:2]) +
                 f'<blockquote>{md(s["hook"][2])}</blockquote><p class="hook">{md(s["hook"][3])}</p>'
                 f'<h3 class="gold" style="margin-top:9mm">{s["inside"].upper()}</h3><ul>' +
                 "".join(f"<li>{md(x)}</li>" for x in s["inside_list"]) + "</ul></section>")
    t1, b1 = find(1)
    parts.append(B.build_chapter(lang, 1, t1, b1, adds))
    parts.append(f'<section class="chapter midcta"><div class="ch-head"><div class="ch-label">{s["badge"]}</div>'
                 f'<h1 class="ch-title">{md(s["mid_title"])}</h1><div class="rule"></div></div><p class="hook">{md(s["mid_text"])}</p>'
                 + cta(lang) + "</section>")
    t9, b9 = find(9)
    cut = f'<div class="cut"><div class="lock">{s["cut_lock"]}</div><p>{md(s["cut_text"])}</p><a class="btn" style="display:block;background:#b8975a;color:#0b0b0e;font-weight:700;padding:3mm;text-decoration:none;border-radius:1mm;font-size:8.6pt" href="{s["url"]}">{s["btn"]}</a></div>'
    parts.append(B.build_chapter(lang, 9, t9, b9, adds, {"trunc": (2, 3), "cut_html": cut}))
    # dentro do guia
    full = "".join(f'<div class="fullrow"><div class="k">{md(k)}</div><div class="v">{md(v)}</div></div>' for k, v in s["full"])
    t24, b24 = find(24)
    items = re.findall(r"^\d+\. (.+)$", b24, flags=re.M)
    vis = "".join(f"<li>{md(x)}</li>" for x in items[:10])
    ghost = "".join(f"<li>{md(x)}</li>" for x in items[10:16])
    parts.append(f'<section class="chapter"><div class="ch-head"><div class="ch-label">{s["badge"]}</div><h1 class="ch-title">{md(s["full_title"])}</h1><div class="rule"></div></div>'
                 f'{full}<p class="stats">{md(s["stats"])}</p><p class="bonusline">{md(s["bonus"])}</p></section>'
                 f'<section class="chapter"><h3 style="margin-top:2mm">{md(s["check_title"]).upper()}</h3><ol class="peek">{vis}</ol><ol class="peek ghost" style="counter-reset: list-item 10">{ghost}</ol>'
                 f'<div class="more">{md(s["check_more"])}</div></section>')
    parts.append(f'<section class="chapter finalcta"><div class="psi-s">Ψ</div><h1 class="ch-title c">{md(s["final_title"])}</h1><div class="rule c"></div>'
                 + cta(lang) + f'<p class="social">{s["social"]}</p></section>')
    css_extra = """
    .hookpage { padding-top: 8mm; } .hookpage .hook { font-size: 12.4pt; }
    .fullrow { display: flex; gap: 4mm; padding: 3mm 0; border-bottom: .4pt solid #26262d; }
    .fullrow .k { flex: 0 0 30mm; font-size: 7pt; font-weight: 700; letter-spacing: .1em; color: #b8975a; padding-top: .6mm; }
    .fullrow .v { flex: 1; font-size: 8.8pt; }
    .stats { margin-top: 5mm; font-size: 7.6pt; font-weight: 600; letter-spacing: .06em; color: #f3f3f6; text-align: center; }
    .bonusline { text-align: center; font-size: 8pt; color: #9fb4c8; }
    .peek { font-size: 8.2pt; margin-bottom: 0; } .peek li { margin-bottom: .6mm; }
    .ghost { opacity: .35; } .more { text-align: center; font-size: 8pt; font-weight: 700; color: #b8975a; letter-spacing: .1em; margin-top: 2mm; }
    .finalcta { text-align: center; padding-top: 30mm; } .psi-s { font-family: "Corm"; font-size: 44pt; color: #b8975a; }
    .ch-title.c { font-size: 21pt; margin: 4mm 6mm 0; } .social { font-size: 7pt; color: #7c7c88; margin-top: 10mm; }
    .midcta .cta { margin-top: 12mm; }
    """
    html = B.page(lang, "".join(parts), L["title1"] + " " + L["title2"]).replace("</style>", css_extra + "</style>")
    out = os.path.join(B.OUT, L["file_sample"] + ".pdf")
    HTML(string=html, base_url=B.ROOT).write_pdf(out)
    return out

def bonus(lang):
    s, L = T[lang], B.S[lang]
    sections, adds = B.load(lang)
    for h, b in sections:
        if re.match(r"(Capítulo|Chapter) 24 ", h): b24 = b
    groups = re.split(r"^### ", b24, flags=re.M)[1:]
    cols = []
    for g in groups:
        head, _, body = g.partition("\n")
        items = re.findall(r"^(\d+)\. (.+)$", body, flags=re.M)
        cols.append(f'<div class="grp"><div class="gh">{head.strip()}</div>' + "".join(f'<div class="it"><span>{n}</span>{md(x)}</div>' for n, x in items) + "</div>")
    cols = f'<table class="grid"><tr><td>{cols[0]}{cols[2]}</td><td>{cols[1]}{cols[3]}</td></tr></table>'
    qs = "".join(f'<div class="q"><div class="box"></div><div class="n">{i+1:02d}</div><div class="tx">{md(q)}</div><div class="ref">{s["chref"]} {c}</div></div>' for i, (q, c) in enumerate(s["r_q"]))
    sc = "".join(f'<div class="sc"><div class="k">{k}</div><div>{md(v)}</div></div>' for k, v in s["r_score"])
    body = f"""
    <section class="sheet"><div class="top"><div class="brand">Ψ LEGENDCHIL · {L['title1']} {L['title2']}</div>
      <h1>{md(s['b_title'])}</h1><p class="sub">{md(s['b_sub'])}</p></div>
      <div class="rulebar">{md(s['b_rule'])}</div><div class="grid">{cols}</div></section>
    <section class="sheet"><div class="top"><div class="brand">Ψ LEGENDCHIL · {L['title1']} {L['title2']}</div>
      <h1>{md(s['r_title'])}</h1><p class="sub">{md(s['r_sub'])}</p></div>
      <div class="qs">{qs}</div><div class="score">{sc}</div><p class="note">{md(s['r_note'])}</p></section>"""
    css = """
    @font-face { font-family: "Corm"; font-weight: 600; src: url("file://%F/eb-garamond-latin-600-normal.woff"); }
    @page { size: A4; margin: 13mm 13mm 12mm; background: #0b0b0e; }
    body { font-family: Inter; color: #cfcfd6; font-size: 8pt; line-height: 1.35; }
    strong { color: #f3f3f6; font-weight: 600; }
    .sheet { break-after: page; } .sheet:last-child { break-after: auto; }
    .brand { font-size: 6.5pt; font-weight: 600; letter-spacing: .3em; color: #b8975a; }
    h1 { font-family: "Corm"; font-weight: 600; font-size: 28pt; color: #f3f3f6; margin: 2mm 0 1mm; }
    .sub { color: #9a9aa6; font-size: 8.6pt; margin: 0 0 4mm; }
    .rulebar { border-left: 1.4pt solid #b8975a; padding: 1.6mm 3mm; background: #121217; color: #e6e6ec; font-size: 8.2pt; margin-bottom: 5mm; }
    .grid { width: 100%; border-collapse: collapse; } .grid td { width: 50%; vertical-align: top; padding: 0 3mm 0 0; }
    .grid td + td { padding: 0 0 0 3mm; } .grp { margin-bottom: 8mm; }
    .gh { font-size: 7.6pt; font-weight: 700; letter-spacing: .18em; color: #9fb4c8; border-bottom: .8pt solid #b8975a; padding-bottom: 1mm; margin-bottom: 1.6mm; }
    .it { font-size: 9pt; margin-bottom: 2.35mm; display: flex; }
    .it span { flex: 0 0 6mm; color: #b8975a; font-weight: 700; }
    .q { display: flex; align-items: flex-start; gap: 3mm; padding: 2.3mm 0; border-bottom: .4pt solid #26262d; }
    .q .box { flex: 0 0 4mm; height: 4mm; border: .8pt solid #b8975a; border-radius: .6mm; }
    .q .n { flex: 0 0 6mm; color: #b8975a; font-weight: 700; font-size: 8.4pt; }
    .q .tx { flex: 1; font-size: 9pt; color: #e6e6ec; }
    .q .ref { flex: 0 0 13mm; text-align: right; font-size: 7pt; color: #7c7c88; }
    .score { display: flex; gap: 3mm; margin-top: 6mm; }
    .sc { flex: 1; background: #121217; padding: 3mm; font-size: 8pt; border-top: 1.2pt solid #9fb4c8; }
    .sc:last-child { border-top-color: #b8975a; }
    .sc .k { font-size: 13pt; font-weight: 700; color: #f3f3f6; margin-bottom: 1mm; }
    .note { margin-top: 5mm; font-size: 7.2pt; color: #8a8a96; }
    """.replace("%F", os.path.join(B.ROOT, "fonts"))
    html = f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>'
    out = os.path.join(B.OUT, L["file_bonus"] + ".pdf")
    HTML(string=html).write_pdf(out)
    return out

if __name__ == "__main__":
    for lg in ("pt", "en"):
        print(sample(lg)); print(bonus(lg))
