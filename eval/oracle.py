#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oracle.py — ファジング（暗黙オラクル）。

「正しい出力」を一切与えない。代わりに、当たり前に守るべき不変条件だけを定め、
大量のランダム文字列を流して破れないかを試す:
  (a) 無例外 : どんな入力でも例外を投げない。
  (b) list   : 返り値は必ずリスト。
  (c) int要素: リストの要素は必ず整数。
1件でも破れたら FAIL。種を固定するので再現可能。

使い方:
  python oracle.py                  # reference.py（正例）を採点
  python oracle.py --candidate NAME # NAME.py を採点
  python oracle.py --selftest       # オラクル自身を検証（正例→PASS / 既知バグ→FAIL）
終了コード: PASS（または selftest 期待どおり）で 0、それ以外 1。
"""
import argparse
import importlib.util
import random
import sys
from pathlib import Path

# Windows コンソール(cp932)でも日本語・記号を出せるよう出力を UTF-8 に統一。
# Linux/Mac は元から UTF-8 なので無害。これが無いと Windows で print が落ちる。
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

EVAL = Path(__file__).resolve().parent
CORPUS = EVAL / "corpus"
N = 5000        # ランダム入力の本数
SEED = 12345    # 種固定（再現可能）
# 数字・カンマ・空白・符号・英字・記号・全角を混ぜる（"," と " " は多めに）
ALPHABET = "0123456789" + ",,,," + "    " + "+-" + "abcXYZ" + ".:;_" + "\t" + "０１２３＋－　"

# 手で選んだ際どい入力（境界・退化ケース）
SEED_CASES = [
    "", ",", ",,,", " ", "   ", "1", "-1", "+2", "1,2,3", " 4 , 5 ",
    "1,x,3", "abc", "1.5,2", "999999999999999999", "０１", "\t", ",1,", "1, ,2",
]


def fuzz_inputs(n):
    random.seed(SEED)
    cases = list(SEED_CASES)
    for _ in range(n):
        length = random.randint(0, 20)
        cases.append("".join(random.choice(ALPHABET) for _ in range(length)))
    return cases


def load(path):
    spec = importlib.util.spec_from_file_location("cand_" + path.stem, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    if not hasattr(m, "parse_int_list"):
        raise AttributeError(f"{path.name} に parse_int_list(s) が無い")
    return m.parse_int_list


def evaluate(fn):
    for s in fuzz_inputs(N):
        try:
            out = fn(s)
        except Exception as e:  # (a) 無例外
            return ("FAIL", f"例外を投げた: 入力 {s!r} → {type(e).__name__}: {e}")
        if not isinstance(out, list):  # (b) list
            return ("FAIL", f"list を返さない: 入力 {s!r} → {type(out).__name__}")
        for x in out:  # (c) int要素
            if not isinstance(x, int) or isinstance(x, bool):
                return ("FAIL", f"int 以外を含む: 入力 {s!r} → {out!r}")
    return ("PASS", f"{len(SEED_CASES)}+{N} 件で不変条件を維持（無例外・list・全要素int）")


def grade(path):
    try:
        fn = load(path)
    except Exception as e:
        return ("FAIL", f"読込失敗: {e}")
    try:
        return evaluate(fn)
    except Exception as e:
        return ("FAIL", f"実行エラー: {type(e).__name__}: {e}")


def table(rows, title):
    print(f"\n### {title}")
    print("| 対象 | 判定 | 詳細 |")
    print("|---|---|---|")
    for n, v, d in rows:
        print(f"| {n} | {v} | {d} |")


def selftest():
    print("# オラクル自己検証 — ファジング（暗黙オラクル）整数リストパーサ")
    rv, rd = grade(CORPUS / "reference.py")
    table([("reference", rv, rd)], "① 正しい堅牢パーサ reference（PASS であるべき）")
    controls = [
        ("broken_crashes.py", "非数で例外 → 無例外NG"),
        ("broken_nonlist.py", "tuple を返す → listNG"),
        ("broken_nonint.py", "文字列のまま返す → int要素NG"),
    ]
    brows, caught = [], True
    for f, why in controls:
        v, d = grade(CORPUS / f)
        ok = (v == "FAIL")
        caught = caught and ok
        brows.append((f, v, ("検出OK " if ok else "検出NG ") + d))
    table(brows, "② 壊れた実装（FAIL であるべき）")
    valid = (rv == "PASS") and caught
    print(f"\n## オラクル判定: {'PASS（バグを捕まえ正例を通す＝信頼できる）' if valid else 'FAIL（オラクル自体に欠陥）'}")
    return valid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", default="reference")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    v, d = grade(CORPUS / f"{a.candidate}.py")
    table([(f"{a.candidate}.py", v, d)], "採点（ファジング）")
    sys.exit(0 if v == "PASS" else 1)


if __name__ == "__main__":
    main()
