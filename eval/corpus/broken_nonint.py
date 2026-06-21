# 陰性対照: int に変換せず文字列のまま返すバグ。list ではあるが要素が str → int要素NG。
def parse_int_list(s):
    return [tok.strip() for tok in s.split(",") if tok.strip()]
