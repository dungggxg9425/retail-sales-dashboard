"""
Bước 1 – Làm sạch dữ liệu Superstore và tách thành mô hình dạng sao (star schema).
Logic giống hệt các truy vấn Power Query trong thư mục powerquery/ – file này dùng để
kiểm tra kết quả và tạo sẵn CSV cho ai muốn nạp thẳng vào Power BI.

Đầu vào : data/raw/Superstore.csv
Đầu ra  : data/model/fact_sales.csv, dim_date.csv, dim_product.csv, dim_customer.csv, dim_geography.csv
          outputs/tables/data_quality_log.csv
Chạy    : python src/01_build_star_schema.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODEL, TABLES = ROOT / "data" / "model", ROOT / "outputs" / "tables"
MODEL.mkdir(parents=True, exist_ok=True)
TABLES.mkdir(parents=True, exist_ok=True)
log = []

# 1. Đọc đúng bảng mã: file gốc mã hóa Windows-1252, đọc sai sẽ lỗi tên sản phẩm có ký tự đặc biệt
df = pd.read_csv(ROOT / "data" / "raw" / "Superstore.csv", encoding="cp1252")
log.append(("Tên sản phẩm có ký tự ngoài ASCII – đọc bằng mã Windows-1252, lưu lại UTF-8",
            int(df["Product Name"].str.contains(r"[^\x00-\x7f]").sum())))

# 2. Chuẩn hóa tên cột: chữ thường, dấu gạch dưới
df.columns = df.columns.str.lower().str.replace(r"[ -]", "_", regex=True)

# 3. Kiểu ngày (định dạng gốc tháng/ngày/năm)
for c in ["order_date", "ship_date"]:
    df[c] = pd.to_datetime(df[c], format="%m/%d/%Y")

# 4. Dòng trùng lặp (giống hệt nhau trừ row_id)
dup = df.drop(columns="row_id").duplicated()
log.append(("Dòng trùng lặp (trùng mọi cột trừ row_id) – loại bỏ", int(dup.sum())))
df = df[~dup].copy()

# 5. Mã bưu chính mất số 0 ở đầu (vd. 2908 -> 02908) – bổ sung cho đủ 5 chữ số
short_zip = df["postal_code"].astype(str).str.len() < 5
log.append(("Mã bưu chính 4 chữ số (mất số 0 đầu) – bổ sung thành 5 chữ số", int(short_zip.sum())))
df["postal_code"] = df["postal_code"].astype(str).str.zfill(5)

# 6. Một product_id ứng với nhiều tên sản phẩm -> tạo khóa thay thế product_key theo cặp (product_id, product_name)
multi = df.groupby("product_id")["product_name"].nunique()
log.append(("product_id ứng với nhiều tên sản phẩm – tạo khóa thay thế product_key", int((multi > 1).sum())))

dim_product = (df[["product_id", "product_name", "category", "sub_category"]]
               .drop_duplicates().sort_values(["product_id", "product_name"]).reset_index(drop=True))
dim_product.insert(0, "product_key", dim_product.index + 1)

dim_customer = (df[["customer_id", "customer_name", "segment"]]
                .drop_duplicates().sort_values("customer_id").reset_index(drop=True))

dim_geography = (df[["country", "region", "state", "city", "postal_code"]]
                 .drop_duplicates().sort_values(["region", "state", "city", "postal_code"]).reset_index(drop=True))
dim_geography.insert(0, "geo_key", dim_geography.index + 1)

# 7. Bảng chiều ngày: liên tục từ ngày đầu đến cuối năm cuối cùng
dates = pd.date_range(df["order_date"].min().replace(month=1, day=1),
                      df["order_date"].max().replace(month=12, day=31), freq="D")
dim_date = pd.DataFrame({"date": dates.date, "year": dates.year, "quarter": "Q" + dates.quarter.astype(str),
                         "month": dates.month, "month_name": dates.strftime("%b"),
                         "year_month": dates.strftime("%Y-%m")})

# 8. Bảng sự kiện: gắn khóa sản phẩm và địa lý
fact = (df.merge(dim_product[["product_key", "product_id", "product_name"]], on=["product_id", "product_name"])
          .merge(dim_geography[["geo_key", "city", "state", "postal_code"]], on=["city", "state", "postal_code"]))
fact["ship_days"] = (fact["ship_date"] - fact["order_date"]).dt.days
fact_sales = fact[["row_id", "order_id", "order_date", "ship_date", "ship_mode", "ship_days", "customer_id",
                   "product_key", "geo_key", "sales", "quantity", "discount", "profit"]].sort_values("row_id")
assert len(fact_sales) == len(df), "Số dòng bảng sự kiện phải bằng số dòng sau làm sạch"

for name, t in [("fact_sales", fact_sales), ("dim_date", dim_date), ("dim_product", dim_product),
                ("dim_customer", dim_customer), ("dim_geography", dim_geography)]:
    t.to_csv(MODEL / f"{name}.csv", index=False, date_format="%Y-%m-%d")
    print(f"{name:14s} {len(t):>6,} dòng")

pd.DataFrame(log, columns=["van_de", "so_dong"]).to_csv(TABLES / "data_quality_log.csv", index=False)
print(pd.DataFrame(log, columns=["van_de", "so_dong"]).to_string(index=False))
