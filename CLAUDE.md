# CLAUDE.md — fuzz-robust-parser-agent

このリポジトリは「任意の文字列からカンマ区切りの整数を取り出す」堅牢パーサのエージェントと、その採点係（ファジング＝暗黙オラクル）です。
正解は与えず、大量のランダム入力で「例外を投げない・必ず list を返す・要素は int」という不変条件が破れないかで判定します。

## 確認のしかた

- `python eval/oracle.py --selftest` … 採点係が正しいか（正例=PASS／既知バグ=FAIL）
- `python eval/oracle.py --candidate candidate` … エージェントの答え（`eval/corpus/candidate.py`）を採点
- `python eval/oracle.py` … お手本(reference.py)を採点

## いじるときの約束（評価駆動 / EDD）

- 先に eval（合否の基準）を満たすことを確認してから「完成」とする。雰囲気で done にしない。
- `eval/corpus/reference.py` と `broken_*.py` は採点係の検証用。むやみに変えない。
- Python 標準ライブラリのみ。秘密情報・個人情報・客先コードを入れない。

## ファイルの役割

- `.claude/agents/fuzz-robust-parser-agent.md` … エージェント定義
- `eval/oracle.py` … 採点係（ファジング／暗黙オラクル）／`design/design.md` … 設計／`README.md` … 説明
