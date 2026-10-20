"""PDF antigo -> markdown estruturado. Uso: python3 extract.py book_pt.pdf out.md"""
import sys, re, pymupdf

def style(s):
    return hex(s["color"]), round(s["size"], 1)

def run_text(spans):
    out = ""
    for s in spans:
        t = s["text"]
        if not t: continue
        c, z = style(s)
        if c == "0xf4f4f7" and t.strip():
            lead = len(t) - len(t.lstrip()); trail = len(t) - len(t.rstrip())
            out += t[:lead] + "**" + t.strip() + "**" + (t[len(t)-trail:] if trail else "")
        else:
            out += t
    return out.replace("****", "")

def main(src, dst):
    d = pymupdf.open(src)
    items = []  # (kind, text, extra)
    for pno, pg in enumerate(d):
        if pno == 0: continue
        bullets = [r["rect"] for r in pg.get_drawings()
                   if r.get("fill") and abs(r["fill"][0] - .7529) < .01 and r["rect"].width < 8]
        lines = []
        for b in pg.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                sp = [s for s in l["spans"] if s["text"]]
                if not sp: continue
                lines.append((l["bbox"], sp))
        lines.sort(key=lambda x: (round(x[0][1]), x[0][0]))
        for bbox, sp in lines:
            c, z = style(sp[0])
            raw = "".join(s["text"] for s in sp)
            if z in (4.9, 9.3, 8.5) or (c, z) == ("0xd6d6dc", 8.0): continue
            x, y = bbox[0], bbox[1]
            isbul = any(abs(r.y0 - y) < 9 and r.x0 < x for r in bullets)
            if z == 22.0 or (c, z) == ("0xf2f2f5", 15.0): kind = "H"
            elif (c, z) == ("0x9fb4c8", 10.5): kind = "h3"
            elif (c, z) == ("0x9fb4c8", 10.2): kind = "partsub"
            elif (c, z) == ("0xececf0", 10.6): kind = "quote"
            elif (c, z) == ("0xc0283a", 10.5): kind = "treino"
            elif z == 9.0: kind = "cell"
            elif c == "0xc0283a" and z == 10.2: kind = "ol"
            else: kind = "li" if isbul else ("cont_li" if x > 50 else "p")
            items.append([kind, run_text(sp) if kind not in ("H",) else raw, (pno, x, y, z)])

    md = []; prev = None; inlist = False; cells = []; lasty = 0; lastp = 0
    def flush_cells():
        nonlocal cells
        if not cells: return
        rows = {}
        for t, (pno, x, y, z) in cells:
            rows.setdefault((pno, round(y)), []).append((x, t))
        xs = sorted({round(x) for r in rows.values() for x, _ in r})
        md.append("")
        rws = [ [t for _, t in sorted(r)] for _, r in sorted(rows.items())]
        # merge rows that only fill some columns (wrapped cells)
        ncol = max(len(r) for r in rws)
        out = []
        for r in rws:
            out.append(r + [""] * (ncol - len(r)))
        md.append("| " + " | ".join(out[0]) + " |")
        md.append("|" + "---|" * ncol)
        for r in out[1:]: md.append("| " + " | ".join(r) + " |")
        md.append("")
        cells = []
    for kind, t, meta in items:
        if kind == "cell":
            cells.append((t.strip(), meta)); prev = kind; continue
        flush_cells()
        t = t.rstrip()
        joinable = prev == kind and kind in ("H", "p", "quote", "partsub")
        if kind == "cont_li" and prev in ("li", "cont_li", "ol", "ol_cont"):
            md[-1] = joinmerge(md[-1], t); prev = "cont_li"; continue
        if kind == "p" and prev in ("ol", "ol_cont") and meta[1] > 45:
            md[-1] = joinmerge(md[-1], t); continue
        if joinable and meta[2] - lasty < 19 and meta[0] == lastp:
            md[-1] = joinmerge(md[-1], t)
        elif joinable and kind == "p" and meta[0] != lastp and not md[-1].endswith((".", ":", "?", "!", "”", '"')):
            md[-1] = joinmerge(md[-1], t)  # parágrafo partido entre páginas
        else:
            if kind == "H": md += ["", "# " + t]
            elif kind == "h3": md += ["", "### " + t.strip()]
            elif kind == "partsub": md += ["", "*" + t + "*"]
            elif kind == "quote": md += ["", "> " + t]
            elif kind == "treino": md += ["", ":::treino"]
            elif kind == "li": md += ["- " + t.strip()] if prev in ("li", "cont_li") else ["", "- " + t.strip()]
            elif kind == "ol": md += ["", t.strip()]; kind = "ol"
            else: md += ["", t]
        prev = kind; lasty = meta[2]; lastp = meta[0]
    flush_cells()
    txt = "\n".join(md)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    open(dst, "w").write(txt.strip() + "\n")

def joinmerge(a, b):
    if a.endswith("-") and not a.endswith(" -"): return a[:-1] + b.lstrip() if False else a + b.lstrip()
    return a + " " + b.lstrip()

lasty = 0; lastp = 0
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
