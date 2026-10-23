-- =====================================================================
-- TRUY VAN MAU DE TRINH BAY TRUOC HOI DONG (chay tung cau trong DB Browser for SQLite,
-- hoac: python src/xem_database.py). Du lieu mo phong.
-- =====================================================================

-- 1. Co so du lieu co gi: so dong moi bang
SELECT 'dm_sku' AS bang, COUNT(*) AS so_dong FROM dm_sku
UNION ALL SELECT 'giao_dich_tho', COUNT(*) FROM giao_dich_tho
UNION ALL SELECT 'giao_dich_sach', COUNT(*) FROM giao_dich_sach
UNION ALL SELECT 'nhat_ky_sua_loi', COUNT(*) FROM nhat_ky_sua_loi
UNION ALL SELECT 'lich_su_kien', COUNT(*) FROM lich_su_kien
UNION ALL SELECT 'lich_khuyen_mai', COUNT(*) FROM lich_khuyen_mai
UNION ALL SELECT 'du_bao', COUNT(*) FROM du_bao;

-- 2. Luong lam sach: tu bang tho (co loi) sang bang sach
SELECT
  (SELECT COUNT(*) FROM giao_dich_tho)                                   AS dong_tho,
  (SELECT COUNT(*) FROM giao_dich_tho WHERE qty_out IS NULL)             AS thieu_qty_out,
  (SELECT COUNT(*) - COUNT(DISTINCT ngay || ma_sku) FROM giao_dich_tho)  AS dong_trung,
  (SELECT COUNT(*) FROM giao_dich_sach)                                  AS dong_sach,
  (SELECT COUNT(*) FROM nhat_ky_sua_loi)                                 AS dong_da_sua;

-- 3. Doi soat ton kho bang SQL: ton cuoi = ton dau + nhap - xuat (ket qua mong doi: 0 dong lech)
SELECT COUNT(*) AS so_dong_lech FROM (
  SELECT ton_cuoi_ngay - (LAG(ton_cuoi_ngay) OVER (PARTITION BY ma_sku ORDER BY ngay) + qty_in - qty_out) AS lech
  FROM giao_dich_sach) WHERE ABS(lech) > 0.5;

-- 4. Nhom hang nao het hang nhieu nhat
SELECT s.nhom_hang, COUNT(*) AS so_ngay_het_hang,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM giao_dich_sach g2 JOIN dm_sku s2 USING (ma_sku)
                                 WHERE s2.nhom_hang = s.nhom_hang), 1) AS ty_le_phan_tram
FROM giao_dich_sach g JOIN dm_sku s USING (ma_sku)
WHERE g.het_hang = 1 GROUP BY s.nhom_hang ORDER BY so_ngay_het_hang DESC LIMIT 5;

-- 5. Xep hang mo hinh du bao (tap test)
SELECT * FROM v_xep_hang_mo_hinh;

-- 6. Du bao cua mo hinh duoc chon cho Mut Tet, moc 20/01/2026 (truoc Tet 2026)
SELECT ngay, ngay_thu, du_bao, thuc_te, sai_so
FROM v_du_bao_chon WHERE ma_sku = 'SKU058' AND moc = '2026-01-20' ORDER BY ngay;

-- 7. Nhat ky lan nap du lieu gan nhat
SELECT buoc, bang, bat_dau, so_dong, trang_thai FROM nhat_ky_chay ORDER BY id;

-- 8. Rang buoc chan du lieu sai (moi cau phai BAO LOI - day la dieu mong muon)
-- INSERT INTO giao_dich_sach VALUES ('2026-10-01','SKU999',0,5,10,0,0,0);   -- SKU khong ton tai -> FOREIGN KEY
-- INSERT INTO giao_dich_sach VALUES ('2026-10-01','SKU001',0,-5,10,0,0,0);  -- xuat am -> CHECK
-- INSERT INTO giao_dich_sach VALUES ('2023-10-01','SKU001',0,5,10,0,0,0);   -- trung (ngay, SKU) -> UNIQUE
