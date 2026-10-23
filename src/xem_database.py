"""Chay lan luot cac truy van mau trong database/truy_van_mau.sql va in ket qua (de trinh bay).
Chay: python src/xem_database.py
"""
import os
import re
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from csdl import doc  # noqa: E402

pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)

with open("database/truy_van_mau.sql", encoding="utf-8") as f:
    text = f.read()
for block in re.split(r"\n(?=-- \d+\. )", text):
    m = re.match(r"-- (\d+\. .*)\n", block)
    if not m:
        continue
    sql = "\n".join(l for l in block.splitlines() if not l.strip().startswith("--")).strip().rstrip(";")
    print(f"\n=== {m.group(1)} ===")
    if not sql:
        print("(xem file .sql: cac cau lenh nay can bao loi)")
        continue
    print(doc(sql).to_string(index=False))
