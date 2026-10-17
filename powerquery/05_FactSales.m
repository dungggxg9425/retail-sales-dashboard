// Bảng sự kiện bán hàng: gắn khóa sản phẩm và địa lý, bỏ các cột mô tả đã nằm ở bảng chiều
let
    Src     = Superstore_Clean,
    JoinP   = Table.NestedJoin(Src, {"product_id", "product_name"}, DimProduct, {"product_id", "product_name"}, "p", JoinKind.Inner),
    ExpP    = Table.ExpandTableColumn(JoinP, "p", {"product_key"}),
    JoinG   = Table.NestedJoin(ExpP, {"city", "state", "postal_code"}, DimGeography, {"city", "state", "postal_code"}, "g", JoinKind.Inner),
    ExpG    = Table.ExpandTableColumn(JoinG, "g", {"geo_key"}),
    Keep    = Table.SelectColumns(ExpG, {"row_id", "order_id", "order_date", "ship_date", "ship_mode", "ship_days",
                                         "customer_id", "product_key", "geo_key", "sales", "quantity", "discount", "profit"})
in
    Table.Sort(Keep, {{"row_id", Order.Ascending}})
