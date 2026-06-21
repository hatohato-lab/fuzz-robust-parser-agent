# 陰性対照: 例外を投げるバグ。非数トークンで int() が ValueError を出す → 無例外NG。
def parse_int_list(s):
    return [int(tok) for tok in s.split(",")]
