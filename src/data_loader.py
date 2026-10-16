"""Memuat, menggabungkan, dan membersihkan data transaksi Annyeongbap.

Setara dengan Task 1 (Excel): kolom Month, order_type, category,
payment_method, dan status yang di Excel diisi dengan VLOOKUP/TEXT,
di sini dibuat dengan pandas merge.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"]


def load_raw() -> dict:
    """Baca 3 tabel mentah dari data/raw."""
    return {
        "transaksi": pd.read_csv(RAW / "transaksi.csv"),
        "mapping_transaksi": pd.read_csv(RAW / "mapping_transaksi.csv"),
        "mapping_menu": pd.read_csv(RAW / "mapping_menu.csv"),
    }


def validate(tables: dict) -> list:
    """Cek kualitas data. Mengembalikan daftar catatan (kosong = aman)."""
    notes = []
    t, mt, mm = tables["transaksi"], tables["mapping_transaksi"], tables["mapping_menu"]
    if t.duplicated().any():
        notes.append(f"{t.duplicated().sum()} baris identik penuh (TIDAK dihapus: mungkin menu yang sama dipesan 2x dalam 1 order, dan agar konsisten dengan hasil Excel/PivotTable)")
    if mt["order_id"].duplicated().any():
        notes.append("order_id pada mapping_transaksi tidak unik")
    missing_orders = set(t["order_id"]) - set(mt["order_id"])
    if missing_orders:
        notes.append(f"{len(missing_orders)} order_id tidak ada di mapping_transaksi")
    missing_menu = set(t["menu_name"]) - set(mm["menu_name"])
    if missing_menu:
        notes.append(f"{len(missing_menu)} menu tidak ada di mapping_menu")
    if ((t["price"] * t["quantity"]) != t["subtotal"]).any():
        notes.append("ada baris dengan price x quantity != subtotal")
    if ((t["subtotal"] - t["discount_amount"]) != t["total"]).any():
        notes.append("ada baris dengan subtotal - discount_amount != total")
    return notes


def build_dataset(tables: dict) -> pd.DataFrame:
    """Gabungkan semua tabel menjadi satu dataset siap analisis."""
    df = (tables["transaksi"]
          .merge(tables["mapping_transaksi"], on="order_id", how="left")
          .merge(tables["mapping_menu"], on="menu_name", how="left"))
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month_num"] = df["order_date"].dt.month
    df["Month"] = pd.Categorical(df["order_date"].dt.strftime("%b"),
                                 categories=MONTH_ORDER, ordered=True)
    for col in ["order_type", "category", "payment_method", "status"]:
        df[col] = df[col].astype(str).str.strip()
    return df


def load_dataset(save: bool = True) -> pd.DataFrame:
    tables = load_raw()
    for note in validate(tables):
        print("[PERINGATAN DATA]", note)
    df = build_dataset(tables)
    if save:
        PROCESSED.mkdir(parents=True, exist_ok=True)
        df.to_csv(PROCESSED / "transaksi_clean.csv", index=False)
    return df
