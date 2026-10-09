"""Chuyen file .docx sang .md de AI doc duoc (giu thu tu tieu de, doan van, bang).
Chay: python src/docx_sang_md.py <file.docx> <file.md>
"""
import sys
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph


def cell_text(cell):
    return " ".join(p.text.strip() for p in cell.paragraphs if p.text.strip()).replace("|", "\\|")


def table_md(tbl):
    rows = []
    for r in tbl.rows:
        cells, seen = [], set()
        for c in r.cells:  # o gop (merged) lap lai cung 1 doi tuong -> chi lay 1 lan
            if id(c._tc) in seen:
                continue
            seen.add(id(c._tc)); cells.append(cell_text(c))
        rows.append(cells)
    if not rows:
        return ""
    n = max(len(r) for r in rows)
    rows = [r + [""] * (n - len(r)) for r in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * n]
    out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(out)


def para_md(p):
    text = p.text.strip()
    if not text:
        return ""
    style = (p.style.name if p.style is not None else "").lower()
    if style.startswith("heading") or style.startswith("title"):
        level = 1 if style.startswith("title") else int("".join(ch for ch in style if ch.isdigit()) or 1)
        return "#" * min(level + 1, 6) + " " + text   # # danh cho tieu de file
    if "list" in style:
        return "- " + text
    return text


def convert(src, dst):
    doc = Document(src)
    parts = [f"# {doc.core_properties.title or src.split('/')[-1].split(chr(92))[-1].rsplit('.', 1)[0]}",
             f"\n> Chuyen tu `{src.split('/')[-1].split(chr(92))[-1]}` bang `src/docx_sang_md.py`. Ban goc la file .docx.\n"]
    for el in doc.element.body.iterchildren():
        tag = el.tag.split("}")[-1]
        if tag == "p":
            s = para_md(Paragraph(el, doc))
        elif tag == "tbl":
            s = table_md(Table(el, doc))
        else:
            continue
        if s:
            parts.append(s)
    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n\n".join(parts) + "\n")


if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
    print("Da ghi", sys.argv[2])
