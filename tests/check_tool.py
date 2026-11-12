#!/usr/bin/env python3
"""errata_check.py 自身を検査する。

    python3 tests/check_tool.py

**検査の道具は、通ることでは信用できない。**何も見ていなくても全部通るからである。
だから、通る状態を作ってから**一つずつ壊し、壊したところがちょうど落ちること**を
確かめる。落ちなければ、その検査は何も見ていない。

中身が既知の PDF を tests/make_pdf.py で作るので、本物の論文は要らない。
"""

import io
import json
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

from errata_check import (digest, p_value, grim_ok, checksum_ok,  # noqa: E402
                          era_to_gregorian)
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

case("宣言の表の名前を書き間違えると落ちる",
     lambda t: edit(t, "audit.toml", "[[open_item]]", "[[open_items]]"),
     "宣言に知らない表や鍵が無い")

case("宣言の項目の鍵を書き間違えると落ちる",
     lambda t: edit(t, "audit.toml", 'reason = "同梱を謳っているが存在しない"',
                    'reson = "同梱を謳っているが存在しない"'),
     "宣言に知らない表や鍵が無い")

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

print("\n3. 分布を、公表されている数値表と突き合わせる")

# 実装が正しいかどうかは、実装だけでは分からない。外の値と当たる。
# 出典は標準的な統計数値表の 5% 点・1% 点。
TABLE_POINTS = [
    ("t(0.05, df=10) = 2.228", p_value("t", 2.228, [10]), 0.05, 5e-4),
    ("t(0.01, df=10) = 3.169", p_value("t", 3.169, [10]), 0.01, 5e-4),
    ("t(0.05, df=1) = 12.706", p_value("t", 12.706, [1]), 0.05, 5e-5),
    ("t 片側は両側の半分", p_value("t", 2.228, [10], "one"), 0.025, 5e-4),
    ("chi2(0.05, df=1) = 3.841", p_value("chi2", 3.841, [1]), 0.05, 5e-5),
    ("chi2(0.05, df=10) = 18.307", p_value("chi2", 18.307, [10]), 0.05, 5e-5),
    ("chi2(0.01, df=5) = 15.086", p_value("chi2", 15.086, [5]), 0.01, 5e-5),
    ("F(0.05, 1, 10) = 4.965", p_value("F", 4.965, [1, 10]), 0.05, 5e-4),
    ("F(0.05, 3, 20) = 3.098", p_value("F", 3.098, [3, 20]), 0.05, 5e-4),
    ("F(0.01, 2, 30) = 5.390", p_value("F", 5.390, [2, 30]), 0.01, 5e-4),
    ("r = 0.5, n = 30 → p ≈ .0049", p_value("r", 0.5, [30]), 0.00485, 5e-4),
]
for label, got, want, tol in TABLE_POINTS:
    check(label, abs(got - want) < tol, "計算 %.6f / 表 %.4f" % (got, want))

print("\n4. GRIM・検査数字・元号を、手で分かる値で当たる")

for mean, n, want in ((3.44, 25, True), (3.42, 25, False), (3.40, 25, True),
                      (2.5, 4, True), (2.6, 4, False),
                      (0.53, 15, True), (0.54, 15, False)):
    check("GRIM  平均 %s / n = %d → %s" % (mean, n, "到達できる" if want else "できない"),
          grim_ok(mean, n, len(str(mean).split(".")[1])) == want)

for kind, value, want in (
    ("orcid", "0009-0000-1406-0547", True),
    ("orcid", "0009-0000-1406-0548", False),
    ("orcid", "0000-0002-1825-0097", True),      # ORCID の公開例（X 以外）
    ("isbn13", "978-0-13-235088-4", True),
    ("isbn13", "978-0-13-235088-5", False),
    ("isbn10", "0-306-40615-2", True),
    ("isbn10", "0-306-40615-3", False),
    ("issn", "0378-5955", True),
    ("issn", "0378-5956", False),
):
    check("%s %s → %s" % (kind, value, "合う" if want else "合わない"),
          checksum_ok(kind, value) == want)

for text, want in (("昭和十八年", 1943), ("昭和二十年", 1945), ("令和元年", 2019),
                   ("平成31年", 2019), ("明治元年", 1868), ("大正十五年", 1926),
                   ("享保十年", None)):
    check("元号  %s → %s" % (text, want), era_to_gregorian(text) == want,
          "換算 %s" % era_to_gregorian(text))

print("\n5. 分野ごとの見本を、一つずつ壊す")

DISC = os.path.join(ROOT, "examples", "disciplines")


def disc_case(label, mutate, expect):
    tmp = tempfile.mkdtemp()
    try:
        dst = os.path.join(tmp, "disciplines")
        shutil.copytree(DISC, dst)
        mutate(dst)
        r = subprocess.run([sys.executable, os.path.join(ROOT, "errata_check.py"),
                            os.path.join(dst, "audit.toml")],
                           capture_output=True, text=True)
        bad = [ln.strip()[6:].strip() for ln in r.stdout.splitlines()
               if ln.strip().startswith("FAIL")]
        check(label, r.returncode == 1 and any(expect in b for b in bad),
              ("落ちた: " + "; ".join(bad[:2])) if bad else "何も落ちなかった")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


disc_case("印字された p を偽ると落ちる",
          lambda d: edit(d, "audit.toml", 'reported = "p = .04"', 'reported = "p = .004"'),
          "p が計算し直した値と合う")

disc_case("自由度を偽ると落ちる",
          lambda d: edit(d, "audit.toml", "df = [28]", "df = [8]"),
          "p が計算し直した値と合う")

disc_case("到達できない平均を到達できると宣言すると落ちる",
          lambda d: edit(d, "audit.toml", "mean = 3.44", "mean = 3.42"),
          "到達できる値である")

disc_case("ORCID を一桁変えると落ちる",
          lambda d: edit(d, "audit.toml", "0009-0000-1406-0547", "0009-0000-1406-0548"),
          "検査数字が合っている")

disc_case("ISBN を一桁変えると落ちる",
          lambda d: edit(d, "audit.toml", "978-0-13-235088-4", "978-0-13-235088-5"),
          "検査数字が合っている")

disc_case("内訳の和が合わないと落ちる",
          lambda d: edit(d, "audit.toml", "values = [112, 8]", "values = [112, 9]"),
          "無作為化 120")

disc_case("和暦と西暦の対応が違うと落ちる",
          lambda d: edit(d, "audit.toml", "gregorian = 1943", "gregorian = 1944"),
          "昭和十八年 = 1944 年")

disc_case("平文の一次資料が差し替わっても落ちる",
          lambda d: open(os.path.join(d, "record.md"), "a").write("\n追記\n"),
          "record が差し替わっていない")

print("\n7. 見本そのものが通る")
for name in ("minimal", "disciplines"):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "errata_check.py"),
                        os.path.join(ROOT, "examples", name, "audit.toml")],
                       capture_output=True, text=True)
    check("examples/%s が通る" % name, r.returncode == 0,
          r.stdout.strip().splitlines()[-1] if r.stdout else "")

print("\n8. 落ちないことも見る（偽陽性を出さない）")
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

print("\n6. 参考文献の見本を、一つずつ壊す")

REFS = os.path.join(ROOT, "examples", "references")


def ref_case(label, mutate, expect):
    tmp = tempfile.mkdtemp()
    try:
        dst = os.path.join(tmp, "references")
        shutil.copytree(REFS, dst)
        mutate(dst)
        r = subprocess.run([sys.executable, os.path.join(ROOT, "errata_check.py"),
                            os.path.join(dst, "audit.toml")],
                           capture_output=True, text=True)
        bad = [ln.strip()[6:].strip() for ln in r.stdout.splitlines()
               if ln.strip().startswith("FAIL")]
        check(label, r.returncode == 1 and any(expect in b for b in bad),
              ("落ちた: " + "; ".join(bad[:2])) if bad else "何も落ちなかった")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


ref_case("箇所（locus）を消すと落ちる",
         lambda d: edit(d, "audit.toml", 'locus = "§1067"', 'locus = ""'),
         "箇所（locus）がある")

ref_case("何を支えているか書かないと落ちる",
         lambda d: edit(d, "audit.toml",
                        'supports = "「力への意志」という語の出どころ。主張そのものは支えていない"',
                        'supports = ""'),
         "何を支えているか書いてある")

ref_case("決めていない使い方を書くと落ちる",
         lambda d: edit(d, "audit.toml", 'role = "対立見解"', 'role = "参考"'),
         "使い方が決めた語である")

# 本文は触らない。触ると sha256 の側が落ちて、見たい失敗が紛れる。
# 宣言の側だけを動かす。

ref_case("宣言し忘れた引用があると落ちる",
         lambda d: edit(d, "audit.toml", 'key = "Foucault 1988"', 'key = "Rawls 1971"'),
         "本文の引用がすべて宣言されている")

ref_case("使っていない参考文献を宣言すると落ちる",
         lambda d: edit(d, "audit.toml", 'key = "Foucault 1988"', 'key = "Rawls 1971"'),
         "宣言した参考文献がすべて使われている")

# **向きが逆の抜け。**本文で名を挙げておきながら参考文献欄に無い相手は、
# 年号つきの引用の形をとらないと reference_policy の網に掛からない。

ref_case("本文だけに出る名が本文から消えると落ちる",
         lambda d: edit(d, "essay.md",
                        "自己への配慮を精神の修練として読む線もある (Hadot)。",
                        "自己への配慮を精神の修練として読む線もある。"),
         "が本文にある")

ref_case("本文だけに出る名が参考文献欄に現れると落ちる",
         lambda d: edit(d, "essay.md",
                        "- Foucault, M. (1988). Technologies of the Self.",
                        "- Foucault, M. (1988). Technologies of the Self.\n- Hadot, P. (1995). Philosophy as a Way of Life."),
         "が参考文献欄に無い")


print("\n9. 自分で名乗っている「壊す先の数」が、実際の数と合っている")

# この道具の主張は「散文に書いた数は機械で確かめられる」である。
# その主張は、この道具自身の散文にも掛かる。掛けなければ、ここが最初にずれる。
SELF = io.open(os.path.abspath(__file__), encoding="utf-8").read()
BREAKS = (len(re.findall(r"^\s*case\(", SELF, re.M))
          + len(re.findall(r"^disc_case\(", SELF, re.M))
          + len(re.findall(r"^ref_case\(", SELF, re.M)))

for rel, pattern in [("README.md", r"壊す先は (\d+) 通り"),
                     ("README.en.md", r"break it in (\d+) distinct ways"),
                     ("CITATION.cff", r"(\d+) 通りに壊して"),
                     (".zenodo.json", r"breaking it in (\d+) distinct ways")]:
    text = io.open(os.path.join(ROOT, rel), encoding="utf-8").read()
    m = re.search(pattern, text)
    check("%s が名乗る数が実際と合う" % rel,
          m is not None and int(m.group(1)) == BREAKS,
          ("名乗り %s / 実際 %d" % (m.group(1), BREAKS)) if m
          else "名乗っている箇所が見つからない")


# ------------------------------------------------- 版と表題の食い違い
#
# **v0.2.0 のタグから 87 行離れたまま、__version__ が 0.2.0 を名乗っていた。**
# 同じ番号が別の中身を指す —— この道具が捕まえるために書かれたものそのものである。
# 版を書いている場所は四つあり、そのどれかが遅れると同じことが起きる。
#
# 表題も同じ形の穴を持っていた。**.zenodo.json は GitHub からの登録に使われるので、
# ここが古いままだと、Zenodo の頁で手で直した表題が次のリリースで戻る。**

TOOL_SRC = io.open(os.path.join(ROOT, "errata_check.py"), encoding="utf-8").read()
VERSION = re.search(r'__version__ = "([^"]+)"', TOOL_SRC).group(1)

_pyproject = io.open(os.path.join(ROOT, "pyproject.toml"), encoding="utf-8").read()
_citation = io.open(os.path.join(ROOT, "CITATION.cff"), encoding="utf-8").read()
_changelog = io.open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read()
_zenodo = json.loads(io.open(os.path.join(ROOT, ".zenodo.json"), encoding="utf-8").read())
_paper = io.open(os.path.join(ROOT, "paper.md"), encoding="utf-8").read()

# README は「PDF を読むところだけが pypdf を使い、それ以外は標準ライブラリだけで動く」と書く。
# その主張は、道具が読み込むモジュールを数えれば確かめられる。**書いただけにしない。**
# 新しい検査を足すと、ここを引く文書の数が動くので、pyproject.toml の組に入れて見る。
import ast  # noqa: E402

_imported = set()
for _node in ast.walk(ast.parse(TOOL_SRC)):
    if isinstance(_node, ast.Import):
        _imported.update(a.name.split(".")[0] for a in _node.names)
    elif isinstance(_node, ast.ImportFrom) and _node.level == 0 and _node.module:
        _imported.add(_node.module.split(".")[0])
_STDLIB = getattr(sys, "stdlib_module_names", None)
_outside = sorted(m for m in _imported if _STDLIB is not None and m not in _STDLIB and m != "__future__")
_deps = re.search(r"^dependencies = \[\]$", _pyproject, re.M)
_pdf_extra = re.search(r'^pdf = \["pypdf[^"]*"\]$', _pyproject, re.M)
_stdlib_only = (_STDLIB is not None and _outside == ["pypdf"]
                and _deps is not None and _pdf_extra is not None)
_stdlib_detail = ("標準ライブラリの外: %s / dependencies = [] %s / pdf = [pypdf] %s"
                  % (", ".join(_outside) or "無し", "有り" if _deps else "無し",
                     "有り" if _pdf_extra else "無し")) if _STDLIB is not None \
    else "sys.stdlib_module_names が無い（Python 3.10 以降で走らせる）"

for rel, pattern, text, extra, extra_label in [
        ("pyproject.toml", r'^version = "([^"]+)"', _pyproject, _stdlib_only,
         "。依存は無く、道具が読むのは標準ライブラリと PDF のときの pypdf だけである"),
        ("CITATION.cff", r"^version: (\S+)", _citation, True, ""),
        ("CHANGELOG.md", r"^## \[([0-9][^\]]*)\]", _changelog, True, "")]:
    m = re.search(pattern, text, re.M)
    check("%s の版が __version__ と合う%s" % (rel, extra_label),
          m is not None and m.group(1).strip('"') == VERSION and extra,
          (("名乗り %s / 実際 %s" % (m.group(1), VERSION)) if m else "版の記述が見つからない")
          + ("" if extra else "  " + _stdlib_detail))

# README の引用欄も版を名乗っている。**v0.3.0 を出したあとも「v0.2.0（いまの版）」の
# まま 19 日残っていた。**上の四つと違ってどの検査も見ていなかったので、誰も気付かなかった。
_readme = io.open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
_released = re.search(r"^## \[([0-9][^\]]*)\]", _changelog, re.M).group(1)
_released_doi = re.search(r"^## \[" + re.escape(_released) + r"\][^\n]*\n+DOI: `([^`]+)`",
                          _changelog, re.M)
_current = re.search(r"^\| v([0-9][^ ]*)（いまの版） \| \[([^\]]+)\]", _readme, re.M)
# 引用欄の表は、版ごとの DOI と公開日を並べる。**行の全部を変更履歴の版の欄と突き合わせる。**
# 一行だけ見ていると、古い版の DOI が書き換わっても通る。
_releases = re.findall(r"^## \[([0-9][^\]]*)\] — (\d{4}-\d{2}-\d{2})\n+DOI: `([^`]+)`",
                       _changelog, re.M)


def _release_rows(text, current):
    """README の版の表を (版, 公開日, DOI) の並びで返す。DOI のリンク先も文字と同じであること。"""
    rows = re.findall(r"^\| v([0-9][^ ]*?)(?:" + current + r")? \| \[([^\]]+)\]"
                      r"\(https://doi\.org/([^)]+)\) \| (\d{4}-\d{2}-\d{2}) \| "
                      r"\[([^\]]+)\]\(CHANGELOG\.md#([^)]+)\) \|$", text, re.M)
    return [(v, date, doi) for v, doi, href, date, label, anchor in rows
            if doi == href and label == v
            and anchor == v.replace(".", "") + "--" + date]


_rows_ja = _release_rows(_readme, "（いまの版）")
check("README の「いまの版」が、変更履歴の最新の版と DOI に合い、版の表の全行が変更履歴の版の欄と合う",
      _current is not None and _released_doi is not None
      and (_current.group(1), _current.group(2)) == (_released, _released_doi.group(1))
      and len(_releases) > 0 and _rows_ja == [(v, d, doi) for v, d, doi in _releases],
      ("README %s %s / 変更履歴 %s %s / 表の行 %d が合う、変更履歴の版 %d" % (
          _current.group(1), _current.group(2), _released,
          _released_doi.group(1) if _released_doi else "?",
          sum(a == b for a, b in zip(_rows_ja, _releases)), len(_releases)))
      if _current else "README に「いまの版」の行が見つからない")

# README は宣言に書ける名前を並べ、その数を名乗っている。道具の KNOWN_TABLES と
# 一つでも食い違えば、利用者は README を信じて書いた宣言で落とされる。
from errata_check import KNOWN_TABLES  # noqa: E402
_fmt = re.search(r"### 宣言の書式は固定する.*?次の (\d+) 個です。\s*```\n(.*?)```", _readme, re.S)
_listed = set(_fmt.group(2).split()) if _fmt else set()
check("README が並べる宣言の名前が、道具の KNOWN_TABLES と一致する",
      _fmt is not None and _listed == set(KNOWN_TABLES)
      and int(_fmt.group(1)) == len(KNOWN_TABLES),
      ("名乗り %s 個 / 並べた %d 個 / 道具 %d 個" % (_fmt.group(1), len(_listed), len(KNOWN_TABLES)))
      if _fmt else "README に「宣言の書式は固定する」の節が見つからない")

# 英語の README は日本語の README の写しである。**写しの数が元とずれれば、英語で読む人だけが
# 古い数を信じる。**版・宣言の名前・名乗る項目数を、日本語の側と同じ物差しで突き合わせる。
_readme_en = io.open(os.path.join(ROOT, "README.en.md"), encoding="utf-8").read()
_current_en = re.search(r"^\| v([0-9][^ ]*) \(current\) \| \[([^\]]+)\]", _readme_en, re.M)
check("英語の README の「current」が、変更履歴の最新の版と DOI に合い、版の表の全行が変更履歴の版の欄と合う",
      _current_en is not None and _released_doi is not None
      and (_current_en.group(1), _current_en.group(2)) == (_released, _released_doi.group(1))
      and _release_rows(_readme_en, r" \(current\)") == [(v, d, doi) for v, d, doi in _releases],
      ("README.en %s %s / 変更履歴 %s / 表の行 %d が合う、変更履歴の版 %d" % (
          _current_en.group(1), _current_en.group(2), _released,
          sum(a == b for a, b in zip(_release_rows(_readme_en, r" \(current\)"), _releases)),
          len(_releases)))
      if _current_en else "英語の README に「current」の行が見つからない")

_fmt_en = re.search(r"### The declaration format is fixed.*?the following (\d+) names:\s*```\n(.*?)```",
                    _readme_en, re.S)
_listed_en = set(_fmt_en.group(2).split()) if _fmt_en else set()
check("英語の README が並べる宣言の名前が、道具の KNOWN_TABLES と一致する",
      _fmt_en is not None and _listed_en == set(KNOWN_TABLES)
      and int(_fmt_en.group(1)) == len(KNOWN_TABLES),
      ("名乗り %s 個 / 並べた %d 個" % (_fmt_en.group(1), len(_listed_en)))
      if _fmt_en else "英語の README に宣言の書式の節が見つからない")

_nums_ja = (re.findall(r"# (\d+) 項目", _readme) + re.findall(r"（(\d+) 項目）", _readme)
            + re.findall(r"(\d+) 点で突き合わせ", _readme))
_nums_en = (re.findall(r"# (\d+) checks", _readme_en) + re.findall(r"\((\d+) checks\)", _readme_en)
            + re.findall(r"(\d+) points\*\* of the", _readme_en))
# 見本の項目数は、README と CI の題が名乗り、ここで走らせた数と突き合わせる。
# 名乗りが三箇所にあり、どれにも検査が掛かっていなかった。項目は増やさず、この検査に畳む
# （この検査の数は、ほかのリポジトリと頁にも写してある）。
_ran, _said = {}, {}
for _ex in ("minimal", "disciplines", "references"):
    _r = subprocess.run([sys.executable, os.path.join(ROOT, "errata_check.py"),
                         os.path.join(ROOT, "examples", _ex, "audit.toml")], capture_output=True, text=True)
    _m = re.search(r"(\d+) 件すべて通りました。", _r.stdout)
    _ran[_ex] = int(_m.group(1)) if _m else None
_said["minimal"] = re.findall(r"examples/minimal/audit\.toml\s+# (\d+) 項目", _readme)
_said["disciplines"] = re.findall(r"examples/disciplines/audit\.toml\s+# (\d+) 項目", _readme)
_said["references"] = re.findall(r"\(examples/references/\)（(\d+) 項目）", _readme)
_ci = re.search(r"見本 (\d+) \+ (\d+) \+ (\d+) 項目",
                io.open(os.path.join(ROOT, ".github", "workflows", "verify.yml"), encoding="utf-8").read())
for _i, _ex in enumerate(("minimal", "disciplines", "references")):
    _said[_ex] = [int(x) for x in _said[_ex]] + ([int(_ci.group(_i + 1))] if _ci else [])
# README の「N 点で突き合わせて」も、3 節で当てた点の数と合うこと。
_points = re.findall(r"(\d+) 点で突き合わせ", _readme)
_samples_ok = bool(_points) and all(int(x) == len(TABLE_POINTS) for x in _points) and all(_ran[x] is not None and len(_said[x]) >= 2 and set(_said[x]) == {_ran[x]} for x in _ran)
check("英語の README が名乗る項目数が、日本語の README と同じ並びで一致し、見本の数と数値表の点の数が実際と合う",
      len(_nums_ja) > 0 and _nums_ja == _nums_en and _samples_ok,
      "日本語 %s / 英語 %s / 見本 走らせた %s・名乗り %s / 数値表 %d 点・名乗り %s" % (_nums_ja, _nums_en, _ran, _said, len(TABLE_POINTS), _points))

_paper_title = re.search(r"^title: '([^']+)'", _paper, re.M).group(1)
# SUBMIT.md の点検表は、paper.md に JOSS が求める節と語数を「済み」としている。
# **済みと書いた欄は、paper.md を読めば確かめられる。**節の名前と語数の範囲は
# SUBMIT.md の側から読み、ここに書き写さない。
_submit = io.open(os.path.join(ROOT, "SUBMIT.md"), encoding="utf-8").read()
_sections = re.search(r"^- \[x\] `paper\.md` に、JOSS が求める節がある：(.+)$", _submit, re.M)
_bounds = re.search(r"^- \[x\] `paper\.md` の本文が (\d+)〜(\d+) 語に収まる", _submit, re.M)
_rule = re.search(r"^語数は (\d+)〜(\d+) 語と決まっています。", _submit, re.M)
_body = re.sub(r"<!--.*?-->", "", re.sub(r"^---\n.*?\n---\n", "", _paper, flags=re.S), flags=re.S)
_words = len(_body.split())
_wanted = re.findall(r"`([^`]+)`", _sections.group(1)) if _sections else []
_missing = [h for h in _wanted if not re.search(r"^# " + re.escape(h) + r"$", _body, re.M)]
# 2026-11-12（三度目の見落とし）。所属は著者の在籍先として ZEN University, Japan の一つだけを書く。
# JOSS の論文の手引きは、著者とその所属の一覧を求める。所属を書くと、道具が大学の仕事か、
# 大学が認めたものと読まれうる。本文に、大学の仕事ではなく、大学が認めてもいないと一文で書く。
# 肩書きは書かない。壊した写しで落ちることも、ここで見る。
_AFFIL = "affiliations:\n  - name: ZEN University, Japan\n    index: 1\n"
_NOT_UNIV = "`errata-check` is not a project of ZEN University, and the university does not endorse it."


def _affil_ok(paper):
    head = re.match(r"^---\n(.*?)\n---\n", paper, re.S)
    body = re.sub(r"<!--.*?-->", "", paper[head.end():] if head else "", flags=re.S)
    return (head is not None and _AFFIL in paper
            and len(re.findall(r"^  - name:", head.group(1), re.M)) == 2
            and _NOT_UNIV in " ".join(body.split()))


_affil_breaks = [
    _paper.replace("`errata-check` is not a project", "`errata-check` is a project"),
    _paper.replace("the university does\nnot endorse it.", "the university endorses it."),
    _paper.replace("  - name: ZEN University, Japan\n", "  - name: ZEN University, Japan\n    index: 1\n  - name: Independent\n"),
    _paper.replace(_AFFIL, ""),
]
check(".zenodo.json の表題が paper.md と揃い、SUBMIT.md の点検表が済みとした節と語数を paper.md が満たし、"
      "所属は ZEN University, Japan の一つだけで、本文が大学の仕事ではなく大学が認めてもいないと書く（壊した写しでは落ちる）",
      _zenodo["title"].startswith(_paper_title)
      and len(_wanted) > 0 and not _missing
      and _bounds is not None and int(_bounds.group(1)) <= _words <= int(_bounds.group(2))
      and _rule is not None and _rule.groups() == _bounds.groups()
      and _affil_ok(_paper) and all(b != _paper and not _affil_ok(b) for b in _affil_breaks),
      "語数 %d / 範囲 %s / 欠けた節 %s / 所属の一文 %s / 壊した写しで落ちる %s" % (
          _words, ("%s〜%s" % _bounds.groups()) if _bounds else "SUBMIT.md に無い",
          ", ".join(_missing) or ("無し" if _wanted else "SUBMIT.md に節の並びが無い"),
          "有り" if _affil_ok(_paper) else "無し",
          sum(1 for b in _affil_breaks if b != _paper and not _affil_ok(b))))

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
