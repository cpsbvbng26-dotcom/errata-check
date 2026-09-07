#!/usr/bin/env python3
"""errata_check.py 自身を検査する。

    python3 tests/check_tool.py

**検査の道具は、通ることでは信用できない。**何も見ていなくても全部通るからである。
だから、通る状態を作ってから**一つずつ壊し、壊したところがちょうど落ちること**を
確かめる。落ちなければ、その検査は何も見ていない。

中身が既知の PDF を tests/make_pdf.py で作るので、本物の論文は要らない。
"""

import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

from errata_check import digest  # noqa: E402
from make_pdf import make  # noqa: E402

passed, failures = 0, []

QUOTES = [
    ("本文", "We verified both cases computationally "
             "(script demo_verification.py, included with this submission)"),
    ("謝辞", "the verification script (demo_verification.py) is distributed "
             "together with this PDF"),
]

PAPER_LINES = [
    "A Demonstration Paper",
    QUOTES[0][1] + ".",
    "Acknowledgments. This manuscript was prepared with assistance; "
    + QUOTES[1][1] + ".",
    "References.",
]

ERRATA = """# 正誤表

最終更新: 2026年9月7日

## E1 — 同梱を謳う検証スクリプトは、存在しない

| 箇所 | 印字されている記述（原文のまま） |
| --- | --- |
| 本文 | {q0} |
| 謝辞 | {q1} |

検証は 4 項目である。

この項目は解決しません。果たされなかった約束として残します。

（2026年9月6日、著者に確認）
""".format(q0=QUOTES[0][1], q1=QUOTES[1][1])

COUNTER = """print("4 checks, 4 passed")
"""

SPEC = """
[document]
path = "ERRATA.md"

[[source]]
id = "paper"
path = "paper.pdf"
sha256 = "{sha}"

[[count]]
source = "paper"
group = "promise"
expect = 2

[[quote]]
source = "paper"
group = "promise"
where = "本文"
text = "{q0}"

[[quote]]
source = "paper"
group = "promise"
where = "謝辞"
text = "{q1}"

[[quote]]
source = "paper"
where = "正しい識別子"
text = "10.5281/zenodo.99999999"
present = false

[[absent]]
glob = "**/demo_verification.py"
reason = "同梱を謳っているが存在しない"

[[number]]
label = "検証の件数"
command = "python3 count.py"
extract = "(\\\\d+) checks"
pattern = "検証は (\\\\d+) 項目"

[[open_item]]
id = "E1"
heading_pattern = "^## E1 —"
must_say = ["この項目は解決しません"]
must_not_say = ["解決済み"]

[dates]
stamp_pattern = "最終更新: (\\\\d{{4}})年(\\\\d{{1,2}})月(\\\\d{{1,2}})日"
any_pattern = "(\\\\d{{4}})年(\\\\d{{1,2}})月(\\\\d{{1,2}})日"
"""


def build(tmp):
    """通る状態の一式を作る。"""
    with open(os.path.join(tmp, "paper.pdf"), "wb") as fh:
        fh.write(make(PAPER_LINES))
    sha = digest(os.path.join(tmp, "paper.pdf"))
    for name, body in (("ERRATA.md", ERRATA), ("count.py", COUNTER),
                       ("audit.toml", SPEC.format(sha=sha, q0=QUOTES[0][1],
                                                  q1=QUOTES[1][1]))):
        with io.open(os.path.join(tmp, name), "w", encoding="utf-8") as fh:
            fh.write(body)
    return sha


def rebuild_pdf(tmp, lines):
    """PDF を作り直す。sha256 も宣言に入れ直す（凍結の検査と混ざらないように）。"""
    with open(os.path.join(tmp, "paper.pdf"), "wb") as fh:
        fh.write(make(lines))
    sha = digest(os.path.join(tmp, "paper.pdf"))
    p = os.path.join(tmp, "audit.toml")
    with io.open(p, encoding="utf-8") as fh:
        s = fh.read()
    s = re.sub(r'sha256 = "[0-9a-f]+"', 'sha256 = "%s"' % sha, s)
    with io.open(p, "w", encoding="utf-8") as fh:
        fh.write(s)


def audit(tmp):
    """走らせて (終了コード, 落ちた検査の名前) を返す。"""
    r = subprocess.run([sys.executable, os.path.join(ROOT, "errata_check.py"),
                        os.path.join(tmp, "audit.toml")],
                       capture_output=True, text=True)
    bad = [ln.strip()[6:].strip() for ln in r.stdout.splitlines()
           if ln.strip().startswith("FAIL")]
    return r.returncode, bad, r.stdout


def edit(tmp, name, old, new):
    p = os.path.join(tmp, name)
    with io.open(p, encoding="utf-8") as fh:
        s = fh.read()
    assert old in s, "置換対象が見つかりません: " + old[:40]
    with io.open(p, "w", encoding="utf-8") as fh:
        fh.write(s.replace(old, new, 1))


def check(label, cond, detail=""):
    global passed
    if cond:
        passed += 1
        print("  PASS  " + label + (("  " + detail) if detail else ""))
    else:
        failures.append(label)
        print("  FAIL  " + label + (("  " + detail) if detail else ""))


def case(label, mutate, expect):
    """壊してから走らせ、期待した検査だけが落ちることを見る。"""
    tmp = tempfile.mkdtemp()
    try:
        build(tmp)
        mutate(tmp)
        code, bad, out = audit(tmp)
        hit = [b for b in bad if expect in b]
        check(label, code == 1 and bool(hit),
              ("落ちた: " + "; ".join(bad[:2])) if bad else "何も落ちなかった")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


print("\n1. 壊していない状態")
tmp = tempfile.mkdtemp()
try:
    build(tmp)
    code, bad, out = audit(tmp)
    check("そのままなら全部通る", code == 0 and not bad,
          "落ちた: " + "; ".join(bad) if bad else "")
    check("検査が 10 件以上走っている", out.count("PASS") >= 10,
          "%d 件" % out.count("PASS"))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n2. 一つずつ壊す")

case("正誤表の引用を一字変えると落ちる",
     lambda t: edit(t, "ERRATA.md", "included with this submission",
                    "included with this submision"),
     "同じ引用が正誤表にもある")

case("宣言の引用が一次資料に無いと落ちる",
     lambda t: edit(t, "audit.toml", "is distributed together with this PDF",
                    "is bundled together with this PDF"),
     "の記述が一次資料にある")

case("無いはずの記述が一次資料にあると落ちる",
     lambda t: rebuild_pdf(t, PAPER_LINES + ["See DOI: 10.5281/zenodo.99999999."]),
     "の記述が一次資料に無い")

case("引用の件数を偽ると落ちる",
     lambda t: edit(t, "audit.toml", "expect = 2", "expect = 3"),
     "記述が 3 箇所宣言されている")

case("一次資料が差し替わると落ちる",
     lambda t: open(os.path.join(t, "paper.pdf"), "ab").write(b"\n% touched\n"),
     "差し替わっていない")

case("sha256 の宣言が無いと通ったことにしない",
     lambda t: edit(t, "audit.toml", "sha256 = ", "# sha256 = "),
     "sha256 が宣言されている")

case("無いはずのファイルがあると落ちる",
     lambda t: open(os.path.join(t, "demo_verification.py"), "w").write("# \n"),
     "存在しない")

case("名乗る件数がコマンドの結果とずれると落ちる",
     lambda t: edit(t, "ERRATA.md", "検証は 4 項目", "検証は 7 項目"),
     "実際と一致する")

case("コマンドの側が変わってもずれを捕まえる",
     lambda t: edit(t, "count.py", "4 checks, 4 passed", "9 checks, 9 passed"),
     "実際と一致する")

case("未解決の宣言が消えると落ちる",
     lambda t: edit(t, "ERRATA.md", "この項目は解決しません", "対応しました"),
     "を保っている"),

case("「解決済み」と書き換わると落ちる",
     lambda t: edit(t, "ERRATA.md", "果たされなかった約束として残します",
                    "解決済みです"),
     "と言っていない")

case("見出しが消えると落ちる",
     lambda t: edit(t, "ERRATA.md", "## E1 —", "## 旧 E1 —"),
     "見出しがある")

case("最終更新が本文の日付より古いと落ちる",
     lambda t: edit(t, "ERRATA.md", "最終更新: 2026年9月7日",
                    "最終更新: 2026年9月5日"),
     "古くない")

print("\n3. 落ちないことも見る（偽陽性を出さない）")
tmp = tempfile.mkdtemp()
try:
    build(tmp)
    # 空白と改行の入り方が変わっても、引用は一致すること
    edit(tmp, "ERRATA.md", "| 謝辞 | the verification script",
         "| 謝辞 | the  verification\nscript")
    code, bad, out = audit(tmp)
    check("空白や改行の違いでは落ちない", code == 0, "; ".join(bad))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
