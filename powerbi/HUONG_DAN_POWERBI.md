# Hướng dẫn dựng dashboard Power BI – Superstore

Thời gian ước tính: 60–90 phút. Cần Power BI Desktop (Windows, miễn phí).

## Cách 1 (khuyên dùng) – làm sạch bằng Power Query

1. `Home > Transform data` → `New Source > Blank Query` → `Advanced Editor`, dán code từng file trong `powerquery/`, đặt tên query đúng như sau:

   | File | Tên query | Load? |
   |---|---|---|
   | `00_Superstore_Clean.m` | `Superstore_Clean` | Không (bỏ chọn *Enable load*) |
   | `01_DimProduct.m` | `DimProduct` | Có |
   | `02_DimCustomer.m` | `DimCustomer` | Có |
   | `03_DimGeography.m` | `DimGeography` | Có |
   | `04_DimDate.m` | `DimDate` | Có |
   | `05_FactSales.m` | `FactSales` | Có |

2. Trong `00_Superstore_Clean.m`, sửa `FilePath` thành đường dẫn tới `data/raw/Superstore.csv` trên máy bạn.
3. `Close & Apply`.

## Cách 2 – nạp sẵn bảng đã tách

`Get data > Text/CSV`, nạp 5 file trong `data/model/` (đổi tên thành `FactSales`, `DimProduct`, `DimCustomer`, `DimGeography`, `DimDate`).

## Mô hình dữ liệu dạng sao

```
DimDate[date]                 1 ── * FactSales[order_date]
DimProduct[product_key]       1 ── * FactSales[product_key]
DimCustomer[customer_id]      1 ── * FactSales[customer_id]
DimGeography[geo_key]         1 ── * FactSales[geo_key]
```

Chọn `DimDate` → `Mark as date table` → cột `date`. Ẩn các cột khóa trong bảng sự kiện.

## Measure

Dán các measure trong `measures.dax`. Với measure Top N: `Modeling > New parameter > Numeric range`, đặt tên `TopN`, từ 5 đến 20, mặc định 10.

## Bố cục dashboard (3 trang)

**Trang 1 – Tổng quan**
- Thẻ KPI: `Doanh thu`, `Loi nhuan`, `Bien loi nhuan`, `So don`, `Tang truong YoY`
- Biểu đồ đường: `Doanh thu` theo `DimDate[month_name]`, legend `DimDate[year]`
- Biểu đồ cột: `Doanh thu` và `Bien loi nhuan` theo `DimProduct[category]` (hai biểu đồ riêng, không dùng trục kép)
- Slicer: `DimDate[year]`, `DimCustomer[segment]`

**Trang 2 – Sản phẩm**
- Biểu đồ thanh ngang: `Loi nhuan` theo `DimProduct[sub_category]`, màu theo measure `Mau loi nhuan` (nhóm lỗ màu cam)
- Bảng: `DimProduct[product_name]`, `Hang san pham`, `Doanh thu Top N`, `Loi nhuan` (lọc `Doanh thu Top N` không trống) + slicer tham số `TopN`
- Hierarchy drill-down: `category` → `sub_category` → `product_name`

**Trang 3 – Khu vực & chiết khấu**
- Bản đồ hoặc biểu đồ thanh: `Doanh thu`, `Bien loi nhuan` theo `DimGeography[region]` → drill-down `state`
- Biểu đồ cột: `Bien loi nhuan` theo nhóm chiết khấu (tạo cột tính toán trong `FactSales`):

```DAX
Muc chiet khau =
SWITCH ( TRUE (),
    FactSales[discount] = 0,    "0%",
    FactSales[discount] <= 0.2, "1–20%",
    FactSales[discount] <= 0.4, "21–40%",
    "> 40%" )
```

## Đối chiếu số liệu

Số trên dashboard (không lọc) phải khớp với sheet `Doi_chieu` trong `excel/doi_chieu_so_lieu.xlsx`:

| Chỉ số | Giá trị |
|---|---|
| Doanh thu 2014–2017 | $2.296.919,49 |
| Lợi nhuận | $286.409,08 |
| Biên lợi nhuận | 12,47% |
| Số đơn | 5.009 |
| Doanh thu 2017 / tăng trưởng YoY | $733.215,26 / +20,36% |
| Biên LN Furniture / Office Supplies / Technology | 2,49% / 17,04% / 17,40% |

Lưu file thành `powerbi/retail_sales_dashboard.pbix`, chụp ảnh từng trang vào `powerbi/screenshots/`, rồi commit và push.
