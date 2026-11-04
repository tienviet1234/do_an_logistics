"""Dat nhan cho bieu do diem it diem: thu moi cach tren / duoi, chon cach it de nhat. Ham thuan, khong phu thuoc giao dien."""
from itertools import product

import numpy as np


def _de(a, b):
    """Dien tich chong nhau cua 2 hop (trai, tren, phai, duoi)."""
    return max(0.0, min(a[2], b[2]) - max(a[0], b[0])) * max(0.0, min(a[3], b[3]) - max(a[1], b[1]))


def vi_tri_nhan(x, y, ten, rong=320.0, cao=120.0, cach=10.0, tren=-12.0, duoi=15.0, chu=6.0, dong=12.0, co_diem=8.0):
    """Tra ve (phai, le): phai[i] = nhan nam ben trai diem vi diem o nua phai; le[i] = 1 neu nhan dat duoi diem.
    rong, cao: co ve uoc luong (px, do tren anh chup that); chu: be rong 1 ky tu; dong: chieu cao nhan; co_diem: nua canh dau cham."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if not len(x) == len(y) == len(ten):
        raise ValueError("x, y, ten khong cung do dai")
    if not len(x):
        return [], []
    nx = (x - x.min()) / (np.ptp(x) or 1.0) * rong
    ny = (1 - (y - y.min()) / (np.ptp(y) or 1.0)) * cao
    phai = [bool(v > rong / 2) for v in nx]
    diem = [(a - co_diem, b - co_diem, a + co_diem, b + co_diem) for a, b in zip(nx, ny)]

    def hop(i, le):
        w = chu * len(ten[i])
        trai = nx[i] - cach - w if phai[i] else nx[i] + cach
        tam = ny[i] + (duoi if le else tren)
        return (trai, tam - dong / 2, trai + w, tam + dong / 2)

    tot, cach_tot = float("inf"), None
    for chon in product((0, 1), repeat=len(x)):                    # moi bieu do chi vai diem nen thu het duoc
        hops = [hop(i, le) for i, le in enumerate(chon)]
        tong = sum(_de(a, b) for k, a in enumerate(hops) for b in hops[k + 1:]) + sum(_de(a, d) for k, a in enumerate(hops) for j, d in enumerate(diem) if j != k)
        if tong < tot:
            tot, cach_tot = tong, chon
    return phai, list(cach_tot)


def do_de_nhan(x, y, ten, le, phai, rong=320.0, cao=120.0, cach=10.0, tren=-12.0, duoi=15.0, chu=6.0, dong=12.0):
    """Tong dien tich chong nhau giua cac nhan voi 1 cach dat (de kiem tra)."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    nx = (x - x.min()) / (np.ptp(x) or 1.0) * rong
    ny = (1 - (y - y.min()) / (np.ptp(y) or 1.0)) * cao
    hops = []
    for i in range(len(x)):
        w = chu * len(ten[i])
        trai = nx[i] - cach - w if phai[i] else nx[i] + cach
        tam = ny[i] + (duoi if le[i] else tren)
        hops.append((trai, tam - dong / 2, trai + w, tam + dong / 2))
    return sum(_de(a, b) for k, a in enumerate(hops) for b in hops[k + 1:])
