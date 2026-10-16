# Annyeongbap Korean Restaurant – Sales Analysis 2025 (Python)

Versi Python dari Final Challenge (Excel + VBA): menyiapkan data transaksi,
mengecek kesalahan hitung Total Sales, lalu menghasilkan KPI, tabel ringkasan,
grafik, dan jawaban 6 pertanyaan challenge secara otomatis.

## Struktur Project
```
annyeongbap-sales-analysis/
├── data/
│   ├── raw/                      # 3 tabel mentah + Data_Dictionary.csv
│   └── processed/                # dibangun ulang oleh run_analysis.py
├── src/
│   ├── data_loader.py            # memuat, validasi, dan menggabungkan tabel
│   ├── metrics.py                # KPI, kontribusi, top menu, tren bulanan, narasi
│   └── visualizer.py             # grafik (.png)
├── outputs/
│   ├── figures/                  # grafik (.png)
│   └── reports/                  # ringkasan metrik (.csv) + jawaban .md
├── run_analysis.py
├── requirements.txt
└── README.md
```

## Cara Menjalankan
```bash
pip install -r requirements.txt
python run_analysis.py
```
Hasil muncul di `data/processed/`, `outputs/figures/`, dan `outputs/reports/`.

## Data (data/raw)
| File | Isi | Setara di Excel |
|---|---|---|
| `transaksi.csv` | 20.000 baris item pesanan (kolom A–O) | sheet *Transaksi* |
| `mapping_transaksi.csv` | order_type, payment_method, status per `order_id` (7.184 transaksi) | sheet *Mapping Transaksi* |
| `mapping_menu.csv` | category per `menu_name` (102 menu) | sheet *Mapping Menu* |
| `Data_Dictionary.csv` | penjelasan kolom | – |

Satu `order_id` bisa punya banyak baris (satu baris per menu), jadi
**Total Transactions dihitung dari `order_id` unik**, bukan jumlah baris.

## Penjelasan Tiap Modul
**`src/data_loader.py`** – setara *Task 1*. Membaca CSV, memvalidasi data
(duplikat, order_id/menu tanpa mapping, konsistensi `price×quantity=subtotal` dan
`subtotal−discount=total`), lalu `merge` untuk membuat kolom `order_type`, `category`,
`payment_method`, `status` (pengganti VLOOKUP) dan `Month` (pengganti `TEXT(DATEVALUE())`).
Hasil bersih disimpan ke `data/processed/transaksi_clean.csv`.

**`src/metrics.py`** – setara PivotTable + Narrative Analysis VBA:
`kpi()` (Total Sales, Transactions, AOV, Items), `check_total_sales()` (bukti *Task 2*),
`by_dimension()` (per category / order type + % kontribusi), `top_menus()`,
`monthly_sales()`, `status_summary()`, `group_insight()` (narasi per grup), dan `trend_label()`.

**`src/visualizer.py`** – setara PivotChart/Dashboard: line chart penjualan bulanan
(keseluruhan, per category, per order type), bar kontribusi, dan top 10 menu.

**`run_analysis.py`** – menjalankan semuanya berurutan dan menulis output.

## Catatan Penting (temuan Task 2 – Debugging)
Macro `Sales_Check` salah menjumlahkan kolom ke-12 (**subtotal**, sebelum diskon),
padahal seharusnya kolom ke-15 (**total**). Hasil salah Rp 1.662.407.000, benar
**Rp 1.661.714.800**; selisih Rp 692.200 = total `discount_amount`.
Lihat `outputs/reports/debug_total_sales_check.csv`.

## Ringkasan Hasil
| Pertanyaan | Jawaban |
|---|---|
| Total Sales / Transactions | Rp 1.661.714.800 / 7.184 |
| Category terbesar | BBQ / Grill – Rp 434.645.600 (26,16%) |
| Menu sales tertinggi | Paket Keluarga (5-6 Orang) – Rp 121.824.000 (premium, bukan terlaris per porsi) |
| Order Type tertinggi | Dine In – Rp 1.061.102.800 (63,86%) |
| Bulan terbaik / tren | Desember (Rp 144,67 jt); fluktuatif cenderung datar |

Jawaban lengkap: `outputs/reports/jawaban_final_challenge.md`.

## Catatan Teknis
- Ada 118 baris identik penuh. **Tidak dihapus** agar angka sama dengan Excel/PivotTable
  (bisa jadi menu yang sama dipesan lebih dari sekali dalam satu order).
- Total Sales menjumlahkan semua status (Selesai, Dibatalkan, Void), sama seperti
  PivotTable/VBA. Untuk *net sales* bersih, filter `status == "Selesai"` di `metrics.py`.
