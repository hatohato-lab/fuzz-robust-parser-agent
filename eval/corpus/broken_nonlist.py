# 陰性対照: list でなく tuple を返すバグ。例外は出さないが返り値の型が違う → listNG。
def parse_int_list(s):
    out = []
    for tok in s.split(","):
        tok = tok.strip()
        try:
            out.append(int(tok))
        except (ValueError, TypeError):
            pass
    return tuple(out)
