// Bảng chiều ngày liên tục, phủ trọn các năm có dữ liệu
let
    StartDate = #date(Date.Year(List.Min(Superstore_Clean[order_date])), 1, 1),
    EndDate   = #date(Date.Year(List.Max(Superstore_Clean[order_date])), 12, 31),
    Dates     = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1, 0, 0, 0)),
    T         = Table.FromList(Dates, Splitter.SplitByNothing(), {"date"}),
    Typed     = Table.TransformColumnTypes(T, {{"date", type date}}),
    AddYear   = Table.AddColumn(Typed, "year", each Date.Year([date]), Int64.Type),
    AddQ      = Table.AddColumn(AddYear, "quarter", each "Q" & Text.From(Date.QuarterOfYear([date])), type text),
    AddMonth  = Table.AddColumn(AddQ, "month", each Date.Month([date]), Int64.Type),
    AddMName  = Table.AddColumn(AddMonth, "month_name", each Date.ToText([date], "MMM", "en-US"), type text),
    AddYM     = Table.AddColumn(AddMName, "year_month", each Date.ToText([date], "yyyy-MM"), type text)
in
    AddYM
