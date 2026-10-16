"""Perhitungan metrik penjualan (setara PivotTable + Narrative VBA)."""
import numpy as np
import pandas as pd
from .data_loader import MONTH_ORDER, MONTH_ID


def kpi(df: pd.DataFrame) -> dict:
    """KPI utama. Total Transactions = jumlah order_id unik."""
    sales = df["total"].sum()
    tx = df["order_id"].nunique()
    return {"total_sales": int(sales), "total_transactions": int(tx),
            "avg_order_value": float(sales / tx) if tx else 0.0,
            "items_sold": int(df["quantity"].sum())}


def check_total_sales(df: pd.DataFrame) -> dict:
    """Bukti debugging Task 2: subtotal (salah) vs total (benar)."""
    wrong, right = int(df["subtotal"].sum()), int(df["total"].sum())
    return {"salah_subtotal": wrong, "benar_total": right,
            "selisih": wrong - right, "total_discount_amount": int(df["discount_amount"].sum())}


def by_dimension(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Sales, transaksi, AOV, item, dan kontribusi per category / order_type."""
    g = df.groupby(col).agg(total_sales=("total", "sum"),
                            transactions=("order_id", "nunique"),
                            items_sold=("quantity", "sum"))
    g["avg_order_value"] = g["total_sales"] / g["transactions"]
    g["contribution_pct"] = g["total_sales"] / g["total_sales"].sum() * 100
    return g.sort_values("total_sales", ascending=False).round(2)


def top_menus(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    g = df.groupby(["menu_name", "category"]).agg(
        total_sales=("total", "sum"), items_sold=("quantity", "sum"),
        transactions=("order_id", "nunique"), price=("price", "first")).reset_index()
    g["contribution_pct"] = g["total_sales"] / df["total"].sum() * 100
    return g.sort_values("total_sales", ascending=False).head(n).round(2)


def monthly_sales(df: pd.DataFrame) -> pd.Series:
    return (df.groupby("Month", observed=False)["total"].sum()
              .reindex(MONTH_ORDER, fill_value=0))


def status_summary(df: pd.DataFrame) -> pd.Series:
    """Status dihitung per order_id unik (bukan per baris)."""
    return df.drop_duplicates("order_id")["status"].value_counts()


def group_insight(df: pd.DataFrame, col: str, value: str) -> dict:
    """Narrative Analysis untuk satu category / order type."""
    sub = df[df[col] == value]
    m = monthly_sales(sub)
    menu = sub.groupby("menu_name")["total"].sum().sort_values(ascending=False)
    out = kpi(sub)
    out.update({"group": value,
                "top_menu": menu.index[0], "top_menu_sales": int(menu.iloc[0]),
                "best_month": MONTH_ID[MONTH_ORDER.index(m.idxmax())], "best_month_sales": int(m.max()),
                "worst_month": MONTH_ID[MONTH_ORDER.index(m.idxmin())], "worst_month_sales": int(m.min()),
                "status": status_summary(sub).to_dict()})
    return out


def trend_label(series: pd.Series) -> str:
    """Pola tren sederhana: kemiringan regresi linear dibanding rata-rata."""
    y = series.values.astype(float)
    slope = np.polyfit(range(len(y)), y, 1)[0]
    rel = slope * (len(y) - 1) / y.mean() * 100
    if rel > 5:
        return f"cenderung naik ({rel:+.1f}%)"
    if rel < -5:
        return f"cenderung turun ({rel:+.1f}%)"
    return f"fluktuatif cenderung datar ({rel:+.1f}%)"
