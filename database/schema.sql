-- =====================================================================
-- CO SO DU LIEU KHO HANG: du bao nhu cau va toi uu ton kho
-- He quan tri: SQLite (1 file data/kho_hang.db). Viet bang SQL chuan de
-- chuyen sang MySQL / PostgreSQL / SQL Server khi can (doi kieu du lieu).
-- Nap du lieu: python src/nap_database.py   (xoa va tao lai toan bo)
-- Du lieu MO PHONG, khong phai so lieu kho that.
-- =====================================================================
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- NHOM 1. DANH MUC (du lieu goc, it thay doi)
-- ---------------------------------------------------------------------
CREATE TABLE dm_nha_cung_cap (
    ma_ncc              TEXT PRIMARY KEY
);

CREATE TABLE dm_sku (
    ma_sku              TEXT PRIMARY KEY,
    ten_sku             TEXT NOT NULL,
    nhom_hang           TEXT NOT NULL,
    don_vi              TEXT NOT NULL,
    ma_ncc              TEXT NOT NULL REFERENCES dm_nha_cung_cap(ma_ncc),
    gia_von             INTEGER NOT NULL CHECK (gia_von > 0),          -- VND / don vi
    gia_ban             REAL    NOT NULL CHECK (gia_ban > 0),
    lead_time_tb        REAL    NOT NULL CHECK (lead_time_tb > 0),     -- ngay
    lead_time_std       REAL    NOT NULL CHECK (lead_time_std >= 0),
    chi_phi_dat_hang    INTEGER NOT NULL CHECK (chi_phi_dat_hang > 0), -- S: VND / lan dat
    ty_le_chi_phi_luu_kho REAL  NOT NULL CHECK (ty_le_chi_phi_luu_kho > 0), -- h: %/nam tren gia von
    moq                 INTEGER NOT NULL CHECK (moq > 0),
    ton_kho_ban_dau     INTEGER NOT NULL CHECK (ton_kho_ban_dau >= 0),
    loai_mua_vu         TEXT NOT NULL,
    phan_loai_abc       TEXT CHECK (phan_loai_abc IN ('A','B','C')),   -- tinh tren 36 thang (chi de tham khao)
    phan_loai_xyz       TEXT CHECK (phan_loai_xyz IN ('X','Y','Z')),
    cv_theo_thang       REAL,
    gia_tri_xuat_36t    INTEGER,
    -- tham so cua bo sinh du lieu mo phong (khong co trong WMS that)
    nhu_cau_tb_ngay_mp  REAL,
    xu_huong_nam_mp     REAL,
    cv_nhu_cau_mp       REAL
);

-- Phan loai tinh tren TAP HUAN LUYEN (den 30/09/2025) - mo hinh dung bang nay
CREATE TABLE phan_loai_sku (
    ma_sku              TEXT PRIMARY KEY REFERENCES dm_sku(ma_sku),
    abc_train           TEXT CHECK (abc_train IN ('A','B','C')),
    xyz_train           TEXT CHECK (xyz_train IN ('X','Y','Z')),
    cv_thang_train      REAL,
    adi                 REAL,
    cv2                 REAL,
    loai_nhu_cau        TEXT
);

-- ---------------------------------------------------------------------
-- NHOM 2. LICH VA SU KIEN (yeu to tac dong nhu cau)
-- ---------------------------------------------------------------------
CREATE TABLE lich_su_kien (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    ten_su_kien         TEXT NOT NULL,
    ngay                TEXT NOT NULL,          -- YYYY-MM-DD
    cua_so_truoc        INTEGER NOT NULL CHECK (cua_so_truoc <= 0),   -- so ngay truoc su kien nhu cau bat dau tang
    cua_so_sau          INTEGER NOT NULL CHECK (cua_so_sau >= 0),
    biet_truoc_28_ngay  INTEGER NOT NULL CHECK (biet_truoc_28_ngay IN (0,1)), -- 0: bao, thoi tiet, dich benh
    ghi_chu             TEXT
);

CREATE TABLE lich_ngay_nghi (
    ngay                TEXT PRIMARY KEY,
    ly_do               TEXT NOT NULL
);

CREATE TABLE lich_khuyen_mai (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    ma_sku              TEXT NOT NULL REFERENCES dm_sku(ma_sku),
    tu_ngay             TEXT NOT NULL,
    den_ngay            TEXT NOT NULL,
    so_ngay             INTEGER NOT NULL CHECK (so_ngay > 0),
    CHECK (den_ngay >= tu_ngay)
);

CREATE TABLE su_kien_dot_bien (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    nhom_ly_do          TEXT NOT NULL,
    su_kien             TEXT NOT NULL,
    tu_ngay             TEXT NOT NULL,
    den_ngay            TEXT NOT NULL,
    muc_do              REAL CHECK (muc_do IS NULL OR (muc_do >= 0 AND muc_do <= 1)),
    nguon_du_lieu       TEXT,                   -- "Thuc te" hay "Mo phong"
    tac_dong_chinh      TEXT,
    ghi_chu_hoac_sku    TEXT
);

-- ---------------------------------------------------------------------
-- NHOM 3. GIAO DICH NHAP - XUAT - TON
-- ---------------------------------------------------------------------
-- Vung tam (staging): nhan nguyen van file xuat tu WMS/ERP, CHUA kiem tra (co the trung, thieu, sai)
CREATE TABLE giao_dich_tho (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    ngay                TEXT NOT NULL,
    ma_sku              TEXT NOT NULL,
    qty_in              REAL,
    qty_out             REAL,                   -- co the NULL (loi thieu)
    ton_cuoi_ngay       REAL,
    nguon_file          TEXT NOT NULL
);

-- Sau lam sach: moi (ngay, SKU) dung 1 dong, da doi soat ton kho
CREATE TABLE giao_dich_sach (
    ngay                TEXT NOT NULL,
    ma_sku              TEXT NOT NULL REFERENCES dm_sku(ma_sku),
    qty_in              REAL NOT NULL CHECK (qty_in >= 0),
    qty_out             REAL NOT NULL CHECK (qty_out >= 0),
    ton_cuoi_ngay       REAL NOT NULL CHECK (ton_cuoi_ngay >= 0),
    la_ngay_nghi        INTEGER NOT NULL CHECK (la_ngay_nghi IN (0,1)),
    het_hang            INTEGER NOT NULL CHECK (het_hang IN (0,1)),
    co_sua              INTEGER NOT NULL CHECK (co_sua IN (0,1)),
    PRIMARY KEY (ngay, ma_sku)
);
CREATE INDEX ix_gds_sku ON giao_dich_sach(ma_sku, ngay);

-- Nhat ky cac dong da sua khi lam sach (truy vet duoc tung thay doi)
CREATE TABLE nhat_ky_sua_loi (
    ngay                TEXT NOT NULL,
    ma_sku              TEXT NOT NULL REFERENCES dm_sku(ma_sku),
    qty_out_tho         REAL,
    qty_out_da_sua      REAL NOT NULL,
    loai_loi            TEXT NOT NULL,
    PRIMARY KEY (ngay, ma_sku)
);

-- ---------------------------------------------------------------------
-- NHOM 4. MO HINH, DU BAO, KET QUA
-- ---------------------------------------------------------------------
CREATE TABLE mo_hinh (
    ma_mo_hinh          TEXT PRIMARY KEY,
    mo_ta               TEXT,
    pham_vi             TEXT NOT NULL DEFAULT 'Toan bo 121 SKU',   -- ARIMA chi chay nhom A: khong so truc tiep
    duoc_chon           INTEGER NOT NULL DEFAULT 0 CHECK (duoc_chon IN (0,1))  -- mo hinh dung cho ton kho
);

CREATE TABLE ket_qua_mo_hinh (
    ma_mo_hinh          TEXT NOT NULL REFERENCES mo_hinh(ma_mo_hinh),
    tap                 TEXT NOT NULL CHECK (tap IN ('validation','validation2','test')),
    so_diem             INTEGER,
    mae                 REAL, rmse REAL, wmape REAL, wmape_tuan REAL, mase REAL,
    bias                REAL, bias_pct REAL,
    wmape_a REAL, wmape_b REAL, wmape_c REAL, wmape_x REAL, wmape_y REAL, wmape_z REAL,
    PRIMARY KEY (ma_mo_hinh, tap)
);

CREATE TABLE du_bao (
    ma_mo_hinh          TEXT NOT NULL REFERENCES mo_hinh(ma_mo_hinh),
    tap                 TEXT NOT NULL,
    moc                 TEXT NOT NULL,          -- ngay dung ra du bao
    ngay                TEXT NOT NULL,          -- ngay duoc du bao
    ma_sku              TEXT NOT NULL REFERENCES dm_sku(ma_sku),
    ngay_thu            INTEGER NOT NULL CHECK (ngay_thu BETWEEN 1 AND 28),
    du_bao              REAL NOT NULL CHECK (du_bao >= 0),
    thuc_te             REAL,                   -- nhu cau tin duoc (NULL = ngay khong cham)
    thap_80 REAL, cao_80 REAL, thap_95 REAL, cao_95 REAL,   -- khoang du bao 80% / 95% (chi mo hinh co, docs/10 muc 9.6)
    PRIMARY KEY (ma_mo_hinh, tap, moc, ngay, ma_sku),
    CHECK (ngay > moc)                          -- khong du bao qua khu
);
CREATE INDEX ix_dubao_sku ON du_bao(ma_sku, ngay);

-- ---------------------------------------------------------------------
-- HE THONG: nhat ky moi lan chay luong
-- ---------------------------------------------------------------------
CREATE TABLE nhat_ky_chay (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    buoc                TEXT NOT NULL,
    bang                TEXT,
    bat_dau             TEXT NOT NULL,
    ket_thuc            TEXT,
    so_dong             INTEGER,
    trang_thai          TEXT NOT NULL CHECK (trang_thai IN ('dang_chay','thanh_cong','loi')),
    ghi_chu             TEXT
);

-- ---------------------------------------------------------------------
-- KHUNG NHIN (VIEW) de trinh bay va cho dashboard
-- ---------------------------------------------------------------------
-- Giao dich kem thong tin SKU va co khuyen mai
CREATE VIEW v_giao_dich AS
SELECT g.ngay, g.ma_sku, s.ten_sku, s.nhom_hang, g.qty_in, g.qty_out, g.ton_cuoi_ngay,
       g.het_hang, g.la_ngay_nghi,
       EXISTS (SELECT 1 FROM lich_khuyen_mai k
               WHERE k.ma_sku = g.ma_sku AND g.ngay BETWEEN k.tu_ngay AND k.den_ngay) AS khuyen_mai
FROM giao_dich_sach g JOIN dm_sku s USING (ma_sku);

-- Du bao cua mo hinh duoc chon, so voi thuc te. Moi ngay chi lay BAN MOI NHAT (mo hinh cap nhat moi tuan co nhieu moc
-- du bao cung 1 ngay; cong tat ca se dem trung).
CREATE VIEW v_du_bao_chon AS
SELECT moc, ngay, ma_sku, ten_sku, nhom_hang, xyz_train, ngay_thu, du_bao, thuc_te, sai_so, thap_80, cao_80, thap_95, cao_95
FROM (SELECT d.moc, d.ngay, d.ma_sku, s.ten_sku, s.nhom_hang, p.xyz_train, d.ngay_thu,
             ROUND(d.du_bao, 1) AS du_bao, d.thuc_te, ROUND(d.thuc_te - d.du_bao, 1) AS sai_so,
             ROUND(d.thap_80, 1) AS thap_80, ROUND(d.cao_80, 1) AS cao_80, ROUND(d.thap_95, 1) AS thap_95, ROUND(d.cao_95, 1) AS cao_95,
             ROW_NUMBER() OVER (PARTITION BY d.ngay, d.ma_sku ORDER BY d.ngay_thu) AS thu_tu
      FROM du_bao d
      JOIN mo_hinh m ON m.ma_mo_hinh = d.ma_mo_hinh AND m.duoc_chon = 1
      JOIN dm_sku s ON s.ma_sku = d.ma_sku
      JOIN phan_loai_sku p ON p.ma_sku = d.ma_sku
      WHERE d.tap = 'test')
WHERE thu_tu = 1;

-- Bang xep hang mo hinh tren tap test
CREATE VIEW v_xep_hang_mo_hinh AS
SELECT k.ma_mo_hinh, m.pham_vi, ROUND(k.wmape, 3) AS wmape, ROUND(k.wmape_tuan, 3) AS wmape_tuan,
       ROUND(k.bias_pct * 100, 1) AS bias_phan_tram, ROUND(k.wmape_z, 3) AS wmape_mua_vu,
       CASE m.duoc_chon WHEN 1 THEN 'DUOC CHON' ELSE '' END AS ghi_chu
FROM ket_qua_mo_hinh k JOIN mo_hinh m USING (ma_mo_hinh)
WHERE k.tap = 'test' AND k.wmape IS NOT NULL
ORDER BY (m.pham_vi <> 'Toan bo 121 SKU'), k.wmape;

-- ---------------------------------------------------------------------
-- NHOM 5. TON KHO (GD F) - bang do src/ton_kho.py ghi (chay sau nap_database.py)
-- ---------------------------------------------------------------------
-- DAP AN cua du lieu mo phong: nhu cau that, ke ca ngay het hang.
-- CHI dung de cham chinh sach ton kho (ty le dap ung), KHONG dua vao mo hinh du bao.
CREATE TABLE nhu_cau_that (
    ngay                TEXT NOT NULL,
    ma_sku              TEXT NOT NULL REFERENCES dm_sku(ma_sku),
    nhu_cau             REAL NOT NULL CHECK (nhu_cau >= 0),
    PRIMARY KEY (ngay, ma_sku)
);

CREATE TABLE chinh_sach (
    ma_chinh_sach       TEXT PRIMARY KEY,
    mo_ta               TEXT NOT NULL,
    mo_hinh_du_bao      TEXT,                   -- NULL: hien trang (do tu du lieu)
    quy_tac_luong_dat   TEXT,                   -- eoq / dat_den_muc / lai (chon tren validation2)
    hieu_chinh_lech     INTEGER NOT NULL DEFAULT 0 CHECK (hieu_chinh_lech IN (0,1))
);

CREATE TABLE tham_so_ton_kho (
    ma_chinh_sach       TEXT NOT NULL REFERENCES chinh_sach(ma_chinh_sach),
    muc_phuc_vu         REAL NOT NULL CHECK (muc_phuc_vu > 0 AND muc_phuc_vu < 1),
    ma_sku              TEXT NOT NULL REFERENCES dm_sku(ma_sku),
    he_so_hieu_chinh    REAL,                   -- nhan voi du bao (uoc luong tren validation2)
    sigma_ltd           REAL,                   -- do lech chuan sai so du bao trong lead time (validation2)
    ss_tb               REAL, rop_tb REAL, eoq_tb REAL,
    PRIMARY KEY (ma_chinh_sach, muc_phuc_vu, ma_sku)
);

CREATE TABLE ket_qua_ton_kho (
    ma_chinh_sach       TEXT NOT NULL REFERENCES chinh_sach(ma_chinh_sach),
    muc_phuc_vu         REAL NOT NULL,
    ma_sku              TEXT NOT NULL REFERENCES dm_sku(ma_sku),
    nhu_cau             REAL, da_dap_ung REAL, so_ngay_thieu INTEGER,
    ton_tb              REAL, gia_tri_ton_tb REAL, so_lan_nhap INTEGER,
    chi_phi_dat         REAL, chi_phi_luu REAL, doanh_thu_mat REAL, loi_nhuan_mat REAL, ton_cuoi_ky REAL,
    PRIMARY KEY (ma_chinh_sach, muc_phuc_vu, ma_sku)
);

CREATE TABLE mo_phong_ngay (
    ma_chinh_sach       TEXT NOT NULL REFERENCES chinh_sach(ma_chinh_sach),
    ngay                TEXT NOT NULL,
    ma_sku              TEXT NOT NULL REFERENCES dm_sku(ma_sku),
    nhap REAL, nhu_cau REAL, xuat REAL, ton_cuoi REAL, dat_hang REAL, rop REAL,
    PRIMARY KEY (ma_chinh_sach, ngay, ma_sku)
);

-- So sanh chinh sach toan kho (dung cho bang truoc - sau)
CREATE VIEW v_so_sanh_chinh_sach AS
SELECT k.ma_chinh_sach, c.mo_ta, k.muc_phuc_vu,
       ROUND(100.0 * SUM(k.da_dap_ung) / SUM(k.nhu_cau), 2)          AS fill_rate_pt,
       SUM(k.so_ngay_thieu)                                          AS so_ngay_sku_thieu,
       ROUND(SUM(k.gia_tri_ton_tb) / 1e6, 1)                         AS ton_tb_trieu_vnd,
       SUM(k.so_lan_nhap)                                            AS so_lan_nhap,
       ROUND(SUM(k.chi_phi_dat) / 1e6, 1)                            AS chi_phi_dat_trieu,
       ROUND(SUM(k.chi_phi_luu) / 1e6, 1)                            AS chi_phi_luu_trieu,
       ROUND((SUM(k.chi_phi_dat) + SUM(k.chi_phi_luu)) / 1e6, 1)     AS tong_chi_phi_trieu,
       ROUND(SUM(k.doanh_thu_mat) / 1e6, 1)                          AS doanh_thu_mat_trieu,
       ROUND(SUM(k.loi_nhuan_mat) / 1e6, 1)                          AS loi_nhuan_mat_trieu,
       ROUND((SUM(k.chi_phi_dat) + SUM(k.chi_phi_luu) + SUM(k.loi_nhuan_mat)) / 1e6, 1) AS chi_phi_lien_quan_trieu
FROM ket_qua_ton_kho k JOIN chinh_sach c USING (ma_chinh_sach)
GROUP BY k.ma_chinh_sach, k.muc_phuc_vu;

-- ---------------------------------------------------------------------
-- NHOM 6. THU DO NHAY (GD F bo sung) - bang do src/do_nhay.py ghi (chay sau ton_kho.py)
-- IF NOT EXISTS: do_nhay.py tu chay lai phan nay tren CSDL cu, khong can nap lai toan bo.
-- Kich ban theo docs/07: tac cang, lead time dai them, chi phi dat hang / luu kho tang. Muc phuc vu 95%.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS kich_ban_do_nhay (
    ma_kich_ban         TEXT PRIMARY KEY,
    nhom                TEXT NOT NULL CHECK (nhom IN ('goc','tac_cang','lead_time','chi_phi')),
    mo_ta               TEXT NOT NULL,
    tham_so             REAL,                   -- so ngay tre them, hoac he so nhan chi phi
    tu_ngay             TEXT,                   -- dot tac cang: hang du kien ve trong [tu_ngay, den_ngay] bi tre
    den_ngay            TEXT,
    biet_truoc          INTEGER NOT NULL CHECK (biet_truoc IN (0,1))   -- 1: nguoi lap ke hoach cap nhat tham so
);

CREATE TABLE IF NOT EXISTS ket_qua_do_nhay (
    ma_kich_ban         TEXT NOT NULL REFERENCES kich_ban_do_nhay(ma_kich_ban),
    ma_chinh_sach       TEXT NOT NULL REFERENCES chinh_sach(ma_chinh_sach),
    muc_phuc_vu         REAL NOT NULL,
    ma_sku              TEXT NOT NULL REFERENCES dm_sku(ma_sku),
    nhu_cau             REAL, da_dap_ung REAL, so_ngay_thieu INTEGER,
    ton_tb              REAL, gia_tri_ton_tb REAL, so_lan_nhap INTEGER,
    chi_phi_dat         REAL, chi_phi_luu REAL, doanh_thu_mat REAL, loi_nhuan_mat REAL, ton_cuoi_ky REAL,
    PRIMARY KEY (ma_kich_ban, ma_chinh_sach, ma_sku)
);

CREATE VIEW IF NOT EXISTS v_do_nhay AS
SELECT k.ma_kich_ban, b.nhom, b.tham_so, b.tu_ngay, b.biet_truoc, k.ma_chinh_sach,
       ROUND(100.0 * SUM(k.da_dap_ung) / SUM(k.nhu_cau), 2)                          AS fill_rate_pt,
       SUM(k.so_ngay_thieu)                                                          AS so_ngay_sku_thieu,
       ROUND(SUM(k.gia_tri_ton_tb) / 1e6, 1)                                         AS ton_tb_trieu_vnd,
       SUM(k.so_lan_nhap)                                                            AS so_lan_nhap,
       ROUND((SUM(k.chi_phi_dat) + SUM(k.chi_phi_luu)) / 1e6, 1)                     AS chi_phi_dat_luu_trieu,
       ROUND(SUM(k.loi_nhuan_mat) / 1e6, 1)                                          AS loi_nhuan_mat_trieu,
       ROUND((SUM(k.chi_phi_dat) + SUM(k.chi_phi_luu) + SUM(k.loi_nhuan_mat)) / 1e6, 1) AS chi_phi_lien_quan_trieu
FROM ket_qua_do_nhay k JOIN kich_ban_do_nhay b USING (ma_kich_ban)
GROUP BY k.ma_kich_ban, k.ma_chinh_sach;
