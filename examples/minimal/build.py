#!/usr/bin/env python3
"""この見本の一式を作り直す。

    python3 examples/minimal/build.py

paper.pdf は tests/make_pdf.py で作った合成の PDF である。本物の論文を置くと、
見本が通ったのが道具のおかげなのかその PDF のおかげなのか分からなくなる。
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "errata-check"))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "..", "tests"))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "tests")))

from make_pdf import make  # noqa: E402
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
from errata_check import digest  # noqa: E402

Q1 = ("We verified both cases computationally "
      "(script demo_verification.py, included with this submission)")
Q2 = ("the verification script (demo_verification.py) is distributed "
      "together with this PDF")

LINES = [
    "A Demonstration Paper",
    "Takuya Nemoto",
    Q1 + ".",
    "Acknowledgments. " + Q2 + ".",
    "References. Nemoto, T. (2026). An Earlier Version. Zenodo. "
    "DOI: 10.5281/zenodo.00000001.",
]

ERRATA = """# 正誤表 —— A Demonstration Paper

最終更新: 2026年9月7日

## E1 — 同梱を謳う検証スクリプトは、存在しない

この論文は 2 箇所で、検証スクリプトが PDF と一緒に配布されていると述べています。

| 箇所 | 印字されている記述（原文のまま） |
| --- | --- |
| 本文 | {q1} |
| 謝辞 | {q2} |

**どちらの箇所も、指しているファイルは存在しません。**

この項目は解決しません。果たされなかった約束として残します。

## E2 — 参考文献が旧版の DOI を指している

参考文献は `10.5281/zenodo.00000001` を引いていますが、これは初版の DOI です。
改訂版は `10.5281/zenodo.00000002` で、**論文中には印字されていません。**

## 検証

この正誤表の記述は 3 項目の検査で当たっています。
"""

COUNTER = 'print("3 checks, 3 passed")\n'

SPEC = '''# errata-check の宣言の見本。
#
#     python3 errata_check.py examples/minimal/audit.toml
#
# 一次資料（paper.pdf）は凍結されている。直せるのは ERRATA.md のほうである。
# この宣言は「ERRATA.md が paper.pdf からずれていないこと」を検査にする。

[document]
path = "ERRATA.md"

[[source]]
id = "paper"
path = "paper.pdf"
sha256 = "{sha}"

# 数え落としを落とすため、件数も宣言する。
# 「三箇所だと思っていたら六箇所だった」を止めるための欄である。
[[count]]
source = "paper"
group = "promise"
expect = 2

# 「印字されている」と述べたものは、本当に印字されているか
[[quote]]
source = "paper"
group = "promise"
where = "本文"
text = "{q1}"

[[quote]]
source = "paper"
group = "promise"
where = "謝辞"
text = "{q2}"

# 「印字されていない」と述べたものは、本当に無いか
[[quote]]
source = "paper"
where = "改訂版の DOI"
text = "10.5281/zenodo.00000002"
present = false

# 旧版の DOI は、確かに印字されている
[[quote]]
source = "paper"
where = "参考文献"
text = "DOI: 10.5281/zenodo.00000001"
in_document = false      # 正誤表は前後を変えて引いているので、そちらは見ない

# 同梱を謳われたファイルは、本当に無いか
[[absent]]
glob = "**/demo_verification.py"
reason = "同梱を謳っているが存在しない"

# 名乗る件数が、実際に走らせた結果と一致するか
[[number]]
label = "検査の件数"
command = "python3 count.py"
extract = "(\\\\d+) checks"
pattern = "(\\\\d+) 項目の検査"

# 解決しないと決めた項目が、こっそり解決済みに書き換わっていないか
[[open_item]]
id = "E1"
heading_pattern = "^## E1 —"
must_say = ["この項目は解決しません"]
must_not_say = ["解決済み", "修正しました"]

[dates]
stamp_pattern = "最終更新: (\\\\d{{4}})年(\\\\d{{1,2}})月(\\\\d{{1,2}})日"
any_pattern = "(\\\\d{{4}})年(\\\\d{{1,2}})月(\\\\d{{1,2}})日"
'''

with open(os.path.join(HERE, "paper.pdf"), "wb") as fh:
    fh.write(make(LINES))
sha = digest(os.path.join(HERE, "paper.pdf"))
for name, body in (("ERRATA.md", ERRATA.format(q1=Q1, q2=Q2)),
                   ("count.py", COUNTER),
                   ("audit.toml", SPEC.format(sha=sha, q1=Q1, q2=Q2))):
    with io.open(os.path.join(HERE, name), "w", encoding="utf-8") as fh:
        fh.write(body)
print("作り直しました。sha256 =", sha)
