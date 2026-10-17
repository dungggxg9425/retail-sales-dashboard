"""
Bước 2 – Tính các chỉ số giống measure DAX để đối chiếu với dashboard, rút ra nhận định và vẽ biểu đồ.
Đầu vào : data/model/*.csv
Đầu ra  : outputs/tables/*.csv, outputs/figures/*.png
Chạy    : python src/02_analysis.py
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

ROOT = Path(__file__).resolve().parents[1]
M, T, F = ROOT / "data" / "model", ROOT / "outputs" / "tables", ROOT / "outputs" / "figures"
F.mkdir(parents=True, exist_ok=True)

BLUE, ORANGE, GREY, INK, INK2 = "#2a78d6", "#eb6834", "#c9c8c3", "#0b0b0b", "#52514e"
plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 160, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#b5b4ae",
    "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "axes.grid": True, "grid.color": "#ebeae6", "axes.axisbelow": True,
    "axes.titleweight": "bold", "axes.titlesize": 12, "axes.titlelocation": "left",
})
usd = mtick.FuncFormatter(lambda x, _: f"{'-' if x < 0 else ''}${abs(x)/1e3:,.0f}K")

# Ghép bảng sự kiện với các bảng chiều (giống quan hệ trong mô hình Power BI)
f = (pd.read_csv(M / "fact_sales.csv", parse_dates=["order_date"])
       .merge(pd.read_csv(M / "dim_product.csv"), on="product_key")
       .merge(pd.read_csv(M / "dim_geography.csv"), on="geo_key")
       .merge(pd.read_csv(M / "dim_customer.csv"), on="customer_id"))
f["year"] = f["order_date"].dt.year


def summary(g):
    return pd.Series({"doanh_thu": g["sales"].sum(), "loi_nhuan": g["profit"].sum(),
                      "so_don": g["order_id"].nunique()})


# ---------------------------------------------------------------- 1. Theo năm: doanh thu, lợi nhuận, YoY
y = f.groupby("year").apply(summary, include_groups=False)
y["bien_loi_nhuan_pct"] = 100 * y["loi_nhuan"] / y["doanh_thu"]
y["tang_truong_yoy_pct"] = 100 * y["doanh_thu"].pct_change()
y.round(2).to_csv(T / "01_by_year.csv")

# ---------------------------------------------------------------- 2. Theo danh mục, nhóm hàng, khu vực
cat = f.groupby("category").apply(summary, include_groups=False)
cat["bien_loi_nhuan_pct"] = 100 * cat["loi_nhuan"] / cat["doanh_thu"]
cat.round(2).to_csv(T / "02_by_category.csv")

sub = f.groupby(["category", "sub_category"]).apply(summary, include_groups=False).reset_index()
sub["bien_loi_nhuan_pct"] = 100 * sub["loi_nhuan"] / sub["doanh_thu"]
sub.sort_values("loi_nhuan").round(2).to_csv(T / "03_by_sub_category.csv", index=False)

reg = f.groupby("region").apply(summary, include_groups=False)
reg["bien_loi_nhuan_pct"] = 100 * reg["loi_nhuan"] / reg["doanh_thu"]
reg.round(2).to_csv(T / "04_by_region.csv")

# ---------------------------------------------------------------- 3. Mức chiết khấu và lợi nhuận
bins = [-0.01, 0, 0.2, 0.4, 1]
labels = ["0%", "1–20%", "21–40%", "> 40%"]
f["muc_chiet_khau"] = pd.cut(f["discount"], bins=bins, labels=labels)
disc = f.groupby("muc_chiet_khau", observed=True).agg(
    so_dong=("sales", "size"), doanh_thu=("sales", "sum"), loi_nhuan=("profit", "sum"))
disc["bien_loi_nhuan_pct"] = 100 * disc["loi_nhuan"] / disc["doanh_thu"]
disc["ty_le_dong_lo_pct"] = 100 * f.groupby("muc_chiet_khau", observed=True)["profit"].apply(lambda s: (s < 0).mean())
disc.round(2).to_csv(T / "05_by_discount.csv")

# ---------------------------------------------------------------- 4. Top 10 sản phẩm theo doanh thu
top = (f.groupby("product_name").agg(doanh_thu=("sales", "sum"), loi_nhuan=("profit", "sum"))
         .nlargest(10, "doanh_thu"))
top.round(2).to_csv(T / "06_top10_products.csv")

# ---------------------------------------------------------------- Biểu đồ
# (a) Doanh thu theo tháng, mỗi năm một đường – năm gần nhất màu xanh, năm trước màu xám
mo = f.groupby([f["order_date"].dt.year.rename("y"), f["order_date"].dt.month.rename("m")])["sales"].sum().unstack(0)
fig, ax = plt.subplots(figsize=(9, 3.8))
for yr in mo.columns:
    last = yr == mo.columns.max()
    ax.plot(mo.index, mo[yr], color=BLUE if last else GREY, lw=2.2 if last else 1.4,
            marker="o" if last else None, ms=4, label=str(yr), zorder=3 if last else 2)
    ax.text(12.15, mo[yr].iloc[-1], str(yr), va="center", fontsize=9, color=INK if last else INK2)
ax.set_xticks(range(1, 13), [f"T{i}" for i in range(1, 13)]); ax.set_xlim(0.7, 12.8)
ax.yaxis.set_major_formatter(usd)
ax.set_title("Doanh thu theo tháng, 2014–2017 (đường xanh: 2017)")
fig.tight_layout(); fig.savefig(F / "01_monthly_sales_by_year.png"); plt.close(fig)

# (b) Lợi nhuận theo nhóm hàng – nhóm lỗ tô cam
s = sub.sort_values("loi_nhuan")
fig, ax = plt.subplots(figsize=(8, 5.2))
ax.barh(s["sub_category"], s["loi_nhuan"], color=[ORANGE if v < 0 else BLUE for v in s["loi_nhuan"]], height=0.65)
ax.axvline(0, color="#8a8984", lw=0.8)
ax.xaxis.set_major_formatter(usd); ax.grid(axis="y", visible=False)
ax.set_title("Lợi nhuận theo nhóm hàng 2014–2017 (cam: nhóm lỗ)")
fig.tight_layout(); fig.savefig(F / "02_profit_by_sub_category.png"); plt.close(fig)

# (c) Biên lợi nhuận theo mức chiết khấu
fig, ax = plt.subplots(figsize=(7, 3.6))
cols = [ORANGE if v < 0 else BLUE for v in disc["bien_loi_nhuan_pct"]]
ax.bar(disc.index.astype(str), disc["bien_loi_nhuan_pct"], color=cols, width=0.55)
for i, v in enumerate(disc["bien_loi_nhuan_pct"]):
    ax.text(i, v + (1.5 if v >= 0 else -1.5), f"{v:.1f}%", ha="center", va="bottom" if v >= 0 else "top",
            fontsize=9, color=INK)
ax.axhline(0, color="#8a8984", lw=0.8)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0)); ax.grid(axis="x", visible=False)
ax.set_xlabel("Mức chiết khấu"); ax.set_title("Biên lợi nhuận theo mức chiết khấu")
ax.set_ylim(disc["bien_loi_nhuan_pct"].min() * 1.25, disc["bien_loi_nhuan_pct"].max() * 1.3)
fig.tight_layout(); fig.savefig(F / "03_margin_by_discount.png"); plt.close(fig)

# ---------------------------------------------------------------- In kết quả
pd.set_option("display.float_format", "{:,.2f}".format)
print("Tổng doanh thu:", round(f["sales"].sum(), 2), "| Tổng lợi nhuận:", round(f["profit"].sum(), 2),
      "| Biên LN %:", round(100 * f["profit"].sum() / f["sales"].sum(), 2), "| Số đơn:", f["order_id"].nunique())
for name, t in [("Theo năm", y), ("Theo danh mục", cat), ("Theo khu vực", reg), ("Theo chiết khấu", disc)]:
    print(f"\n== {name}\n{t}")
print("\n== Nhóm hàng lỗ\n", sub[sub["loi_nhuan"] < 0].sort_values("loi_nhuan").to_string(index=False))
print("\n== Top 10 sản phẩm\n", top)
