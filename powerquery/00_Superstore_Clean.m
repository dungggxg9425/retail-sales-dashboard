// Truy vấn trung gian: đọc và làm sạch file gốc. Đặt tên query: Superstore_Clean
// (Bỏ chọn "Enable load" cho query này – chỉ dùng làm nguồn cho các bảng bên dưới)
// Sửa đường dẫn FilePath cho đúng vị trí file trên máy bạn.
let
    FilePath = "C:\retail-sales-dashboard\data\raw\Superstore.csv",
    // 1252 = bảng mã Windows-1252: đọc đúng tên sản phẩm có ký tự đặc biệt
    Source   = Csv.Document(File.Contents(FilePath), [Delimiter = ",", Columns = 21, Encoding = 1252, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    // Chuẩn hóa tên cột: chữ thường, dấu gạch dưới
    Renamed  = Table.TransformColumnNames(Promoted, each Text.Lower(Text.Replace(Text.Replace(_, " ", "_"), "-", "_"))),
    // Ngày gốc dạng tháng/ngày/năm -> dùng culture en-US
    Typed    = Table.TransformColumnTypes(Renamed, {
                 {"row_id", Int64.Type}, {"order_date", type date}, {"ship_date", type date},
                 {"sales", type number}, {"quantity", Int64.Type}, {"discount", type number}, {"profit", type number}}, "en-US"),
    // Mã bưu chính mất số 0 đầu -> bổ sung đủ 5 chữ số
    ZipFixed = Table.TransformColumns(Typed, {{"postal_code", each Text.PadStart(Text.From(_), 5, "0"), type text}}),
    // Loại dòng trùng lặp ở mọi cột trừ row_id
    Deduped  = Table.Distinct(ZipFixed, List.RemoveItems(Table.ColumnNames(ZipFixed), {"row_id"})),
    ShipDays = Table.AddColumn(Deduped, "ship_days", each Duration.Days([ship_date] - [order_date]), Int64.Type)
in
    ShipDays
