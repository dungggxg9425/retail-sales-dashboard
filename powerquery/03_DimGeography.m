// Bảng chiều địa lý (khóa geo_key theo thành phố + bang + mã bưu chính)
let
    Source  = Table.Distinct(Table.SelectColumns(Superstore_Clean, {"country", "region", "state", "city", "postal_code"})),
    Sorted  = Table.Sort(Source, {{"region", Order.Ascending}, {"state", Order.Ascending}, {"city", Order.Ascending}, {"postal_code", Order.Ascending}}),
    Indexed = Table.AddIndexColumn(Sorted, "geo_key", 1, 1, Int64.Type)
in
    Indexed
