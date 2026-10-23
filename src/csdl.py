"""Ket noi co so du lieu kho hang (SQLite) - dung chung cho moi buoc cua luong.
    from csdl import ket_noi, doc
    df = doc("SELECT * FROM v_xep_hang_mo_hinh")
"""
import sqlite3
from contextlib import closing

import pandas as pd

DB_PATH = "data/kho_hang.db"
SCHEMA = "database/schema.sql"


def ket_noi(path=DB_PATH):
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys = ON")        # SQLite mac dinh TAT kiem tra khoa ngoai
    return con


def doc(sql, params=None, path=DB_PATH):
    with closing(ket_noi(path)) as con:
        return pd.read_sql_query(sql, con, params=params)
