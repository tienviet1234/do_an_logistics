"""Chuyen file .md sang .docx de mo bang Word (giu tieu de, bang, danh sach).
Chay: python src/md_sang_docx.py [file.md ...]   (mac dinh: docs/10_bao_cao_giai_doan_2.md)
Ket qua: reports/word/<ten>.docx  (ghi de moi lan chay -> neu sua trong Word, hay "Save As" ten khac)
"""
import os
import sys
import pypandoc

files = sys.argv[1:] or ["docs/10_bao_cao_giai_doan_2.md"]
os.makedirs("reports/word", exist_ok=True)
for f in files:
    out = "reports/word/" + os.path.splitext(os.path.basename(f))[0] + ".docx"
    pypandoc.convert_file(f, "docx", outputfile=out, extra_args=["--from=gfm", "--resource-path=."])
    print("Da ghi", out)
