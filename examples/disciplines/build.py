#!/usr/bin/env python3
"""分野ごとの見本の一式を作り直す。

    python3 examples/disciplines/build.py

一次資料を二つ置く。**PDF だけが対象ではない**ことを示すためでもある。

    paper.pdf   実証系の論文を模した合成の PDF（検定統計量・平均・人数・識別子）
    record.md   史料のノートを模した平文（和暦）

どちらも合成である。本物を使うと、通ったのが道具のおかげなのか資料のおかげ
なのかが分からなくなる。
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

from make_pdf import make          # noqa: E402
from errata_check import digest     # noqa: E402

PAPER = [
    "A Demonstration Study",
    "Takuya Nemoto  ORCID 0009-0000-1406-0547",
    "Method. Of 120 participants randomised, 112 were analysed and 8 were lost",
    "to follow-up.",
    "Results. The groups differed on the primary measure, t(28) = 2.14, p = .04.",
    "A second analysis gave F(3, 20) = 3.10, p = .049, and the association was",
    "chi2(1) = 3.84, p = .05.",
    "Table 1. Mean score 3.44 (n = 25); control mean 3.40 (n = 25).",
    "Reference. Knuth, D. (1997). The Art of Computer Programming.",
    "ISBN 978-0-13-235088-4. Journal ISSN 0378-5955.",
]

RECORD = """# 史料ノート

最終更新: 2026年9月7日

## 出典

海軍公報（部内限）号外、昭和十八年九月十一日。

叙勲の記載にある年は昭和十八年である。

## E1 — 西暦の併記が無い

原本には西暦の併記が無い。**この項目は解決しません。**原本を直せないため、
ここに換算を書いて残す。

## E2 — 論文に印字された p が誤っている

`F(3, 20) = 3.10` から計算すると p = .0499 であり、印字されている `.049` とは
合わない。**この項目も解決しません。**論文はもう直せない。

指摘そのものが誤っていないかどうかは、audit.toml の `consistent = false` が
押さえている。**「誤りである」という主張も検査の対象にする。**
"""

SPEC = '''# 分野ごとの見本。
#
#     python3 errata_check.py examples/disciplines/audit.toml
#
# 一次資料はどちらも合成である。**引用の一致だけが検査ではない**ことを示すために、
# 検定統計量・GRIM・識別子・算術・元号を一通り入れてある。

[document]
path = "record.md"

[[source]]
id = "paper"
path = "paper.pdf"
sha256 = "{sha}"

[[source]]
id = "record"
path = "record.md"
sha256 = "{sha2}"

# ------------------------------------------------- 検定（statcheck と同じ考え方）
#
# 印字された統計量と自由度から p を計算し直し、印字された p と合うかを見る。
# 合わなければ、統計量・自由度・p のどれかが誤っている。

[[statistic]]
source = "paper"
where = "結果 1"
text = "t(28) = 2.14, p = .04"
test = "t"
df = [28]
value = 2.14
reported = "p = .04"

[[statistic]]
source = "paper"
where = "結果 2"
text = "F(3, 20) = 3.10, p = .049"
test = "F"
df = [3, 20]
value = 3.10
reported = "p = .049"
consistent = false          # 正誤表が「ここは誤り」と述べている箇所。
                            # 誤っていることのほうを検査する

[[statistic]]
source = "paper"
where = "結果 3"
text = "chi2(1) = 3.84, p = .05"
test = "chi2"
df = [1]
value = 3.84
reported = "p = .05"

# ------------------------------------------------------- GRIM
#
# 整数を n 人ぶん平均した値は、n をかけると整数にならなければならない。
# 到達できない平均が印字されていれば、平均か人数のどちらかが誤っている。

[[grim]]
source = "paper"
where = "表 1"
text = "Mean score 3.44 (n = 25)"
mean = 3.44
n = 25

[[grim]]
source = "paper"
where = "表 1・対照"
text = "control mean 3.40 (n = 25)"
mean = 3.40
n = 25

# ------------------------------------------------------- 識別子
#
# 検査数字（チェックディジット）が合っているか。一桁でも書き写しを誤れば落ちる。

[[identifier]]
source = "paper"
kind = "orcid"
value = "0009-0000-1406-0547"

[[identifier]]
source = "paper"
kind = "isbn13"
value = "978-0-13-235088-4"

[[identifier]]
source = "paper"
kind = "issn"
value = "0378-5955"

# ------------------------------------------------------- 算術
#
# 臨床試験の流れ図に効く。無作為化された数が、解析と脱落の和に一致するか。

[[arithmetic]]
label = "無作為化 120 = 解析 112 + 脱落 8"
source = "paper"
texts = ["120 participants randomised", "112 were analysed", "8 were lost"]
op = "sum"
values = [112, 8]
equals = 120

# ------------------------------------------------------- 元号
#
# 和暦と西暦の対応。史料を扱うときに効く。

[[era]]
source = "record"
text = "昭和十八年"
gregorian = 1943

[[open_item]]
id = "E1"
heading_pattern = "^## E1 —"
must_say = ["この項目は解決しません"]

[dates]
stamp_pattern = "最終更新: (\\\\d{{4}})年(\\\\d{{1,2}})月(\\\\d{{1,2}})日"
any_pattern = "(\\\\d{{4}})年(\\\\d{{1,2}})月(\\\\d{{1,2}})日"
'''

with open(os.path.join(HERE, "paper.pdf"), "wb") as fh:
    fh.write(make(PAPER))
with io.open(os.path.join(HERE, "record.md"), "w", encoding="utf-8") as fh:
    fh.write(RECORD)
sha = digest(os.path.join(HERE, "paper.pdf"))
sha2 = digest(os.path.join(HERE, "record.md"))
with io.open(os.path.join(HERE, "audit.toml"), "w", encoding="utf-8") as fh:
    fh.write(SPEC.format(sha=sha, sha2=sha2))
print("作り直しました。paper %s / record %s" % (sha[:12], sha2[:12]))
