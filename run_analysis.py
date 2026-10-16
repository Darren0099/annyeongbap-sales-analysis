"""Jalankan seluruh analisis:  python run_analysis.py"""
from pathlib import Path
import pandas as pd
from src import data_loader as dl, metrics as mx, visualizer as vz

ROOT = Path(__file__).resolve().parent
REPORTS, FIGS = ROOT / "outputs" / "reports", ROOT / "outputs" / "figures"
rp = lambda n: "Rp " + f"{n:,.0f}".replace(",", ".")
pct = lambda v: f"{v:.2f}".replace(".", ",") + "%"
bln = lambda m: dl.MONTH_ID[dl.MONTH_ORDER.index(m)]


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    df = dl.load_dataset()
    print(f"Dataset: {len(df):,} baris, {df.order_id.nunique():,} transaksi")

    # --- metrik ---
    k = mx.kpi(df)
    dbg = mx.check_total_sales(df)
    cat = mx.by_dimension(df, "category")
    ot = mx.by_dimension(df, "order_type")
    menus = mx.top_menus(df, 10)
    monthly = mx.monthly_sales(df)
    status = mx.status_summary(df)

    # --- simpan CSV ---
    pd.Series(k).to_csv(REPORTS / "kpi_overview.csv", header=["value"])
    pd.Series(dbg).to_csv(REPORTS / "debug_total_sales_check.csv", header=["value"])
    cat.to_csv(REPORTS / "sales_by_category.csv")
    ot.to_csv(REPORTS / "sales_by_order_type.csv")
    menus.to_csv(REPORTS / "top_menu.csv", index=False)
    monthly.rename("total_sales").to_csv(REPORTS / "monthly_sales.csv")
    status.rename("transactions").to_csv(REPORTS / "status_summary.csv")
    insights = [mx.group_insight(df, "category", v) for v in cat.index] + \
               [mx.group_insight(df, "order_type", v) for v in ot.index]
    pd.DataFrame(insights).to_csv(REPORTS / "narrative_per_group.csv", index=False)

    # --- grafik ---
    vz.generate_all(df, cat, ot, menus, FIGS)

    # --- jawaban Final Challenge ---
    top_cat, top_ot = cat.index[0], ot.index[0]
    tm = menus.iloc[0]
    by_qty = df.groupby("menu_name")["quantity"].sum().sort_values(ascending=False)
    best_m, worst_m = monthly.idxmax(), monthly.idxmin()
    ins = mx.group_insight(df, "category", top_cat)
    lines = [
        "# Jawaban Final Challenge - Annyeongbap 2025", "",
        "## Task 2 - Debugging",
        f"- Error: macro menjumlahkan kolom 12 (subtotal), seharusnya kolom 15 (total).",
        f"- Hasil salah {rp(dbg['salah_subtotal'])} -> benar {rp(dbg['benar_total'])} (selisih {rp(dbg['selisih'])} = total diskon).", "",
        "## Jawaban",
        f"1. Total Sales {rp(k['total_sales'])}; Total Transactions {k['total_transactions']:,}".replace(",", "."),
        f"2. Category terbesar: {top_cat} - {rp(cat.loc[top_cat,'total_sales'])} ({pct(cat.loc[top_cat,'contribution_pct'])} dari Total Sales)",
        f"3. Menu sales tertinggi: {tm.menu_name} - {rp(tm.total_sales)} ({pct(tm.contribution_pct)}), harga {rp(tm.price)}, "
        f"{int(tm.items_sold)} porsi. Menu terlaris per porsi: {by_qty.index[0]} ({by_qty.iloc[0]} porsi). "
        "Jadi menu sales tertinggi = produk premium/penyumbang nilai, belum tentu unggulan volume.",
        "4. Order Type: " + "; ".join(f"{i} {rp(r.total_sales)} ({pct(r.contribution_pct)}, AOV {rp(r.avg_order_value)})" for i, r in ot.iterrows())
        + f". Tertinggi: {top_ot}.",
        f"5. Bulan terbaik: {bln(best_m)} ({rp(monthly.max())}); terendah {bln(worst_m)} ({rp(monthly.min())}). Tren: {mx.trend_label(monthly)}.",
        f"6. Insight {top_cat}: kontribusi {pct(cat.loc[top_cat,'contribution_pct'])}, AOV {rp(ins['avg_order_value'])}; "
        f"top menu {ins['top_menu']} ({rp(ins['top_menu_sales'])}); bulan terbaik {ins['best_month']} "
        f"({rp(ins['best_month_sales'])}), terlemah {ins['worst_month']}; status {ins['status']}.",
    ]
    (REPORTS / "jawaban_final_challenge.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nSelesai. Lihat folder {REPORTS.relative_to(ROOT)} dan {FIGS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
