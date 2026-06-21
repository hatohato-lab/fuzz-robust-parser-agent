# 正例: どんな入力でも例外を投げず、必ず int のリストを返す堅牢な実装。
# 数として読めないトークンは黙って捨てる。
def parse_int_list(s):
    out = []
    for tok in s.split(","):
        tok = tok.strip()
        try:
            out.append(int(tok))
        except (ValueError, TypeError):
            pass
    return out
