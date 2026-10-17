// Bảng chiều sản phẩm. Một product_id có thể có nhiều tên -> khóa thay thế product_key
let
    Source  = Table.Distinct(Table.SelectColumns(Superstore_Clean, {"product_id", "product_name", "category", "sub_category"})),
    Sorted  = Table.Sort(Source, {{"product_id", Order.Ascending}, {"product_name", Order.Ascending}}),
    Indexed = Table.AddIndexColumn(Sorted, "product_key", 1, 1, Int64.Type)
in
    Table.ReorderColumns(Indexed, {"product_key", "product_id", "product_name", "category", "sub_category"})
