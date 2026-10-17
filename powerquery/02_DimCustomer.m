// Bảng chiều khách hàng
let
    Source = Table.Distinct(Table.SelectColumns(Superstore_Clean, {"customer_id", "customer_name", "segment"}))
in
    Table.Sort(Source, {{"customer_id", Order.Ascending}})
