"""Pembuatan grafik (Line Chart bulanan, bar category, order type, top menu)."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from .data_loader import MONTH_ORDER
from .metrics import monthly_sales

RED, GREY = "#B3261E", "#5B6770"
juta = FuncFormatter(lambda v, _: f"{v/1e6:,.0f}")


def _slug(s: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in s).strip("_")


def _clean(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


def line_monthly(df, title, path):
    s = monthly_sales(df)
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(MONTH_ORDER, s.values, marker="o", color=RED, lw=2.4)
    for x, y in zip(MONTH_ORDER, s.values):
        ax.annotate(f"{y/1e6:.1f}", (x, y), textcoords="offset points", xytext=(0, 7),
                    ha="center", fontsize=8, color=GREY)
    ax.set_title(f"{title}\nHistorical Sales by Month (Rp juta)", fontsize=11)
    ax.yaxis.set_major_formatter(juta); ax.grid(axis="y", alpha=.3); _clean(ax)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def bar_sales(table, title, path):
    t = table.sort_values("total_sales")
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(t.index, t["total_sales"], color=RED)
    for b, p in zip(bars, t["contribution_pct"]):
        ax.text(b.get_width(), b.get_y() + b.get_height() / 2, f"  {p:.1f}%", va="center", fontsize=9)
    ax.xaxis.set_major_formatter(juta); ax.set_xlabel("Total Sales (Rp juta)")
    ax.set_title(title, fontsize=11); _clean(ax)
    ax.set_xlim(0, t["total_sales"].max() * 1.15)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def bar_menus(table, title, path):
    t = table.iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.barh(t["menu_name"], t["total_sales"], color=RED)
    ax.xaxis.set_major_formatter(juta); ax.set_xlabel("Total Sales (Rp juta)")
    ax.set_title(title, fontsize=11); _clean(ax)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def generate_all(df, cat_table, ot_table, menus, fig_dir: Path):
    fig_dir.mkdir(parents=True, exist_ok=True)
    line_monthly(df, "Executive Overview", fig_dir / "01_line_monthly_overall.png")
    bar_sales(cat_table, "Kontribusi Sales per Category", fig_dir / "02_bar_category.png")
    bar_sales(ot_table, "Kontribusi Sales per Order Type", fig_dir / "03_bar_order_type.png")
    bar_menus(menus, "Top 10 Menu berdasarkan Sales", fig_dir / "04_top_menu.png")
    for col in ("category", "order_type"):
        (fig_dir / col).mkdir(exist_ok=True)
        for v in df[col].unique():
            line_monthly(df[df[col] == v], f"{col}: {v}", fig_dir / col / f"{_slug(v)}.png")
