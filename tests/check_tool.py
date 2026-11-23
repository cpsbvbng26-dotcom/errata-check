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

# ------------------------------------------------- 版を切るコミットの形（2026-11-23）
#
# **v0.3.0 のタグの中の CITATION.cff は 0.2.0 を名乗ったままだった（self-correction の TL-002）。**
# タグを切るのは運営者のアカウントで、作業環境からは切れない。だから、タグが指すコミットそのものが
# 揃っていなければならない。そのコミットには、自分の版の DOI がまだ無い（Zenodo は Release のあとに付ける）。
# 決めた形は二つだけである。SUBMIT.md の「版の番号について」に、決めたことと理由を書いてある。
#
#   版と版のあいだ  四か所は最後に出した版を名乗る。CITATION.cff の date-released と doi、pyproject.toml の
#                   Archive は、変更履歴のその版の欄の日付と DOI に合う。変更は「## 未リリース」に溜める。
#   版を切るコミット  四か所が新しい版を名乗る。変更履歴のいちばん上の版の欄は、DOI の行の代わりに
#                   RELEASE_MARKER を持つ。CITATION.cff に doi は無く、pyproject.toml に Archive は無い。
#                   ほかの版の欄は、どれも DOI を持つ。
#
# 出していない版の番号を、版と版のあいだに名乗らない。名乗れば、出していない版を出したと書くことになる。
RELEASE_MARKER = "DOI: 未付与（Release と Zenodo の版ができたあとに、受け取った番号をここに書きます）"


def _releases_of(changelog):
    """変更履歴の版の欄のうち、DOI のあるものを (版, 公開日, DOI) の並びで返す。"""
    return re.findall(r"^## \[([0-9][^\]]*)\] — (\d{4}-\d{2}-\d{2})\n+DOI: `([^`]+)`", changelog, re.M)


def version_problems(tool_src, pyproject, citation, changelog):
    """版を書いている四か所が、変更履歴の版の欄と同じ一つの版を指すかを見る。食い違いを場所ごとに返す。"""
    p = {"pyproject.toml": [], "CITATION.cff": [], "CHANGELOG.md": []}
    m = re.search(r'^__version__ = "([^"]+)"$', tool_src, re.M)
    ver = m.group(1) if m else None
    heads = re.findall(r"^## \[([0-9][^\]]*)\] — (\d{4}-\d{2}-\d{2})\n\n([^\n]*)$", changelog, re.M)
    if len(re.findall(r"^## \[", changelog, re.M)) != len(heads) or not heads:
        p["CHANGELOG.md"].append("版の欄の見出しが「## [版] — 日付」と空行と DOI の行の形でない")
        return p
    if len(re.findall(r"^## 未リリース$", changelog, re.M)) > 1:
        p["CHANGELOG.md"].append("「## 未リリース」が二つある")
    dois = {}
    for i, (v, d, line) in enumerate(heads):
        mm = re.fullmatch(r"DOI: `(10\.\d{4,9}/\S+)`", line)
        if mm:
            dois[v] = mm.group(1)
        elif i == 0 and line == RELEASE_MARKER:
            dois[v] = None
        else:
            p["CHANGELOG.md"].append("%s の欄の DOI の行が決めた形でない（%s）" % (v, line[:30]))
    top, top_date = heads[0][0], heads[0][1]
    want = dois.get(top)
    if ver != top:
        p["CHANGELOG.md"].append("いちばん上の版 %s / __version__ %s" % (top, ver))
    mv = re.search(r'^version = "([^"]+)"$', pyproject, re.M)
    if not mv or mv.group(1) != ver:
        p["pyproject.toml"].append("版 %s / __version__ %s" % (mv.group(1) if mv else "無し", ver))
    arch = re.findall(r'^Archive = "([^"]*)"$', pyproject, re.M)
    if arch != (["https://doi.org/" + want] if want else []):
        p["pyproject.toml"].append("Archive %s / 版の DOI %s" % (",".join(arch) or "無し", want or "まだ無い"))
    cv = re.search(r'^version: "?([^"\s]+)"?$', citation, re.M)
    if not cv or cv.group(1) != ver:
        p["CITATION.cff"].append("version %s / __version__ %s" % (cv.group(1) if cv else "無し", ver))
    cd = re.search(r'^date-released: "?(\d{4}-\d{2}-\d{2})"?$', citation, re.M)
    if not cd or cd.group(1) != top_date:
        p["CITATION.cff"].append("date-released %s / 変更履歴 %s" % (cd.group(1) if cd else "無し", top_date))
    ctop = re.findall(r"^doi: (\S+)$", citation, re.M)
    if ctop != ([want] if want else []):
        p["CITATION.cff"].append("doi %s / 版の DOI %s" % (",".join(ctop) or "無し", want or "まだ無い"))
    ids = re.findall(r"^  - type: doi\n    value: (\S+)\n    description: v(\S+) ", citation, re.M)
    if len(re.findall(r"^  - type: doi$", citation, re.M)) != len(ids):
        p["CITATION.cff"].append("identifiers の DOI に、どの版のものかの名乗りが無い")
    for val, v in ids:
        if dois.get(v) != val:
            p["CITATION.cff"].append("identifiers の v%s の DOI %s / 変更履歴 %s" % (v, val, dois.get(v)))
    if want and (want, top) not in ids:
        p["CITATION.cff"].append("identifiers に v%s の DOI が無い" % top)
    return p


def release_commit(tool_src, pyproject, citation, changelog, new, date):
    """版を切るコミットを、いまの中身から作る。決めた形をそのとおりに当てたもの。"""
    old = re.search(r'^__version__ = "([^"]+)"$', tool_src, re.M).group(1)
    return (tool_src.replace('__version__ = "%s"' % old, '__version__ = "%s"' % new),
            re.sub(r'^Archive = .*\n', "", pyproject.replace('version = "%s"' % old, 'version = "%s"' % new),
                   flags=re.M),
            re.sub(r'^doi: .*\n', "", re.sub(r'^date-released: .*$', 'date-released: "%s"' % date,
                                             citation.replace("version: %s" % old, "version: %s" % new),
                                             flags=re.M), flags=re.M),
            changelog.replace("## 未リリース\n", "## [%s] — %s\n\n%s\n" % (new, date, RELEASE_MARKER), 1))


_VP = version_problems(TOOL_SRC, _pyproject, _citation, _changelog)
_RC = release_commit(TOOL_SRC, _pyproject, _citation, _changelog, "9.9.9", "2099-12-31")
_PREV_DOI = _releases_of(_changelog)[1][2]
_DATE = re.search(r'^date-released: "?(\d{4}-\d{2}-\d{2})"?$', _citation, re.M).group(1)
# 壊した写し。どれも、決めた二つの形のどちらにも当たらない。版と日付と DOI は、いまの中身から取る。
_version_breaks = [
    ("CITATION.cff の date-released を変更履歴と違えて書く",
     (TOOL_SRC, _pyproject, _citation.replace(_DATE, "2099-01-01"), _changelog)),
    ("CITATION.cff の doi を前の版の DOI にする",
     (TOOL_SRC, _pyproject, re.sub(r"^doi: .*$", "doi: " + _PREV_DOI, _citation, flags=re.M), _changelog)),
    ("pyproject.toml の Archive を前の版の DOI にする",
     (TOOL_SRC, re.sub(r'^Archive = .*$', 'Archive = "https://doi.org/%s"' % _PREV_DOI, _pyproject, flags=re.M),
      _citation, _changelog)),
    ("identifiers の版の名乗りを別の版にする",
     (TOOL_SRC, _pyproject, re.sub(r"description: v\S+ の版 DOI", "description: v9.9.8 の版 DOI", _citation),
      _changelog)),
    ("変更履歴に欄を作らずに、四か所の版だけを上げる",
     (_RC[0], _RC[1], _RC[2], _changelog)),
    ("版を切るコミットで、CITATION.cff に前の版の doi を残す",
     (_RC[0], _RC[1], _citation.replace("version: " + VERSION, "version: 9.9.9").replace(_DATE, "2099-12-31"),
      _RC[3])),
    ("版を切るコミットで、pyproject.toml に前の版の Archive を残す",
     (_RC[0], _pyproject.replace('version = "%s"' % VERSION, 'version = "9.9.9"'), _RC[2], _RC[3])),
    ("版を切るコミットの DOI の行を、決めた文と違えて書く",
     (_RC[0], _RC[1], _RC[2], _RC[3].replace(RELEASE_MARKER, "DOI: 未付与"))),
    ("二つ目の版の欄から DOI の行を消す",
     (TOOL_SRC, _pyproject, _citation, _changelog.replace("DOI: `%s`\n" % _PREV_DOI, "", 1))),
]
# 写しが本当に元と違うこと（置き換えが空振りすれば、壊したことにならない）。
assert all(args != (TOOL_SRC, _pyproject, _citation, _changelog) and args != _RC for _, args in _version_breaks)
_version_break_ok = sum(1 for _, args in _version_breaks if any(version_problems(*args).values()))
_rc_problems = version_problems(*_RC)

for rel, extra, extra_label in [
        ("pyproject.toml", _stdlib_only,
         "。依存は無く、道具が読むのは標準ライブラリと PDF のときの pypdf だけである。Archive は名乗る版の DOI を指す"),
        ("CITATION.cff", True, "。date-released と doi と identifiers も、変更履歴のその版の欄と合う"),
        ("CHANGELOG.md", not any(_rc_problems.values()) and _version_break_ok == len(_version_breaks),
         "。版を切るコミットの形も通り、決めた二つの形に当たらない写し %d 通りは落ちる" % len(_version_breaks))]:
    check("%s の版が __version__ と合う%s" % (rel, extra_label),
          not _VP[rel] and extra,
          (" / ".join(_VP[rel]) or "版 %s" % VERSION)
          + ("" if rel != "pyproject.toml" or _stdlib_only else "  " + _stdlib_detail)
          + ("" if rel != "CHANGELOG.md" else "  版を切るコミット %s / 落ちた写し %d / %d" % (
              " / ".join(sum(_rc_problems.values(), [])) or "通る", _version_break_ok, len(_version_breaks))))

# README の引用欄も版を名乗っている。**v0.3.0 を出したあとも「v0.2.0（いまの版）」の
# まま 19 日残っていた。**上の四つと違ってどの検査も見ていなかったので、誰も気付かなかった。
_readme = io.open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
_readme_en = io.open(os.path.join(ROOT, "README.en.md"), encoding="utf-8").read()


def _release_rows(text, current):
    """README の版の表を (版, 公開日, DOI) の並びで返す。DOI のリンク先も文字と同じであること。"""
    rows = re.findall(r"^\| v([0-9][^ ]*?)(?:" + current + r")? \| \[([^\]]+)\]"
                      r"\(https://doi\.org/([^)]+)\) \| (\d{4}-\d{2}-\d{2}) \| "
                      r"\[([^\]]+)\]\(CHANGELOG\.md#([^)]+)\) \|$", text, re.M)
    return [(v, date, doi) for v, doi, href, date, label, anchor in rows
            if doi == href and label == v
            and anchor == v.replace(".", "") + "--" + date]


def readme_release(readme, changelog, current):
    """README の「いまの版」が DOI のある最新の版を指し、版の表の全行が変更履歴の版の欄と合うか。
    版を切るコミットでは、いちばん上の版に DOI がまだ無い。README はその間、DOI のある版だけを並べる。"""
    rels = _releases_of(changelog)
    cur = re.search(r"^\| v([0-9][^ ]*)" + current + r" \| \[([^\]]+)\]", readme, re.M)
    rows = _release_rows(readme, current)
    ok = (cur is not None and len(rels) > 0 and (cur.group(1), cur.group(2)) == (rels[0][0], rels[0][2])
          and rows == rels)
    detail = ("README %s %s / 変更履歴 %s %s / 表の行 %d が合う、変更履歴の版 %d" % (
        cur.group(1), cur.group(2), rels[0][0] if rels else "?", rels[0][2] if rels else "?",
        sum(a == b for a, b in zip(rows, rels)), len(rels))) if cur else "README に「いまの版」の行が見つからない"
    return ok, detail


# 引用欄の表は、版ごとの DOI と公開日を並べる。**行の全部を変更履歴の版の欄と突き合わせる。**
# 一行だけ見ていると、古い版の DOI が書き換わっても通る。版を切るコミットでも同じ README のまま通ること。
_ok_ja, _detail_ja = readme_release(_readme, _changelog, "（いまの版）")
check("README の「いまの版」が、変更履歴の最新の版と DOI に合い、版の表の全行が変更履歴の版の欄と合う",
      _ok_ja and readme_release(_readme, _RC[3], "（いまの版）")[0], _detail_ja)

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
_ok_en, _detail_en = readme_release(_readme_en, _changelog, r" \(current\)")
check("英語の README の「current」が、変更履歴の最新の版と DOI に合い、版の表の全行が変更履歴の版の欄と合う",
      _ok_en and readme_release(_readme_en, _RC[3], r" \(current\)")[0], _detail_en)

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


def _git(*args):
    """git を走らせて標準出力を返す。失敗すれば None。"""
    try:
        r = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True, text=True)
    except OSError:
        return None
    return r.stdout if r.returncode == 0 else None


# 2026-11-23。JOSS の規程（openjournals/joss の docs/submitting.md）は、言語モデルの利用の開示に
# "The tools/models used (and versions)" を求める。どのモデルを使ったかは、コミットの Co-Authored-By に
# 一件ずつ残っている。**履歴に出てくるモデルを、開示の節がすべて名指ししていること。**
# 新しいモデルでコミットすれば、ここが落ちる。開示を書き足すまで通らない。
def trailer_models():
    out = _git("log", "--format=%(trailers:key=Co-Authored-By,valueonly,separator=%x0A)")
    if out is None:
        return None
    names = {re.sub(r"\s*<[^>]*>$", "", ln.strip()) for ln in out.splitlines() if ln.strip()}
    return sorted(n for n in names if n.startswith("Claude"))


_MODELS = trailer_models()
# 規程の三点（道具と版と場所／助力の中身／人が確かめたという言明）に、論文の手引き（docs/paper.md）の
# "how the quality and correctness of AI-generated content was verified" を足した四つの見出し。
_AI_LABELS = ["**Tools, models and where they were used.**", "**Nature and scope of assistance.**",
              "**How correctness was verified.**", "**Confirmation of review.**"]
_NUMBER_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]


def _flex(phrase):
    """語のあいだの空白と改行を問わない型。論文は行を折り返している。"""
    return r"\s+".join(re.escape(w) for w in phrase.split())


def paper_problems(paper, submit, readme, bib):
    """paper.md が、SUBMIT.md の点検表と規程と README と paper.bib に合っているか。食い違いの並びを返す。"""
    p = []
    sections = re.search(r"^- \[x\] `paper\.md` に、JOSS が求める節がある：(.+)$", submit, re.M)
    bounds = re.search(r"^- \[x\] `paper\.md` の本文が (\d+)〜(\d+) 語に収まる", submit, re.M)
    rule = re.search(r"^語数は (\d+)〜(\d+) 語と決まっています。", submit, re.M)
    title = re.search(r"^title: '([^']+)'", paper, re.M)
    body = re.sub(r"<!--.*?-->", "", re.sub(r"^---\n.*?\n---\n", "", paper, flags=re.S), flags=re.S)
    words = len(body.split())
    wanted = re.findall(r"`([^`]+)`", sections.group(1)) if sections else []
    missing = [h for h in wanted if not re.search(r"^# " + re.escape(h) + r"$", body, re.M)]
    if not wanted or missing:
        p.append("欠けた節 " + (", ".join(missing) or "SUBMIT.md に節の並びが無い"))
    if bounds is None or rule is None or rule.groups() != bounds.groups() \
            or not int(bounds.group(1)) <= words <= int(bounds.group(2)):
        p.append("語数 %d / 範囲 %s" % (words, ("%s〜%s" % bounds.groups()) if bounds else "SUBMIT.md に無い"))
    # 2026-10-07 に論文の手引きに足された決まり。表題は引用の情報に写るので、逆引用符を使わない。
    if title is None or "`" in title.group(1):
        p.append("表題に逆引用符がある")
    ai = re.search(r"^# AI usage disclosure\n(.*?)(?=^# )", body, re.M | re.S)
    ai = " ".join(ai.group(1).split()) if ai else ""
    if _MODELS is None or not _MODELS:
        p.append("履歴から Co-Authored-By のモデルが読めない")
    for m in (_MODELS or []) + ["Claude Code"]:
        if not re.search(_flex(m) + r"(?!\.?\d)", ai):
            p.append("開示の節が %s を名指ししていない" % m)
    for lab in _AI_LABELS + ["The language model is not an author."]:
        if lab not in ai:
            p.append("開示の節に %s が無い" % lab)
    # 散文に書いた数。設計の取捨の数は見出しの段落の数と、使っているリポジトリの数は README の並びと合う。
    design = re.search(r"^# Software design\n(.*?)(?=^# )", body, re.M | re.S)
    n_design = len(re.findall(r"^\*\*[^*]+\*\*", design.group(1), re.M)) if design else -1
    used = re.search(r"^## 使われている場所\n(.*?)(?=^## )", readme, re.M | re.S)
    n_used = len(re.findall(r"^- \[", used.group(1), re.M)) if used else -1
    for said, real in [(re.search(r"^(\w+) trade-offs shaped the implementation\.", body, re.M), n_design),
                       (re.search(r"across (\w+) repositories, run in continuous", body), n_used),
                       (re.search(r"^(\w+) repositories vendor the module", " ".join(body.split()).replace(". ", ".\n"), re.M),
                        n_used),
                       (re.search(r"by the (\w+) repositories that use the tool", " ".join(body.split())), n_used)]:
        if said is None or not 0 <= real < len(_NUMBER_WORDS) or said.group(1).lower() != _NUMBER_WORDS[real]:
            p.append("数 %s / 実際 %d" % (said.group(1) if said else "名乗りが無い", real))
    # 引いた鍵と paper.bib の鍵が一つずつ対応する。paper.bib の DOI は、README がすでに載せている番号だけ
    # （決めごと 1。登録機関の記録と突き合わせたのは SUBMIT.md の「paper.bib で確かめたもの」）。
    cited = set(re.findall(r"@([A-Za-z][\w-]*)", re.sub(r"`[^`]*`", "", body)))
    keys = set(re.findall(r"^@\w+\{([^,\s]+),", bib, re.M))
    if not keys or cited != keys:
        p.append("引いた鍵 %s / paper.bib の鍵 %s" % (sorted(cited), sorted(keys)))
    for d in re.findall(r"^\s*doi\s*=\s*\{([^}]+)\}", bib, re.M):
        if d not in readme:
            p.append("paper.bib の DOI %s が README に無い" % d)
    return p


# 2026-11-23。関門 1・3・4 の事実を SUBMIT.md に書いた。数えた先のコミットを固定し、そこまでを git から数え直す。
# 先端で数えると、次のコミットで数が動いて落ちる（cpsbvbng26-dotcom の CLAUDE.md、開示の無いマージの件数）。
# 浅い複製では数えられない。CI は fetch-depth: 0 で取り出す。
_GATE_SHA = r"^数えた先は `main` の `([0-9a-f]{40})` です。"
_GATE_SINCE = r"^- (\d{4}-\d{2}-\d{2}) 以降にマージした pull request："


def gate_lines(sha, since):
    """数えた先までの事実を、SUBMIT.md に書く形の行で返す。履歴が無ければ None。"""
    if _git("cat-file", "-e", sha + "^{commit}") is None or _git("merge-base", "--is-ancestor", sha, "HEAD") is None:
        return None
    log = _git("log", sha, "--format=%as|%P|%an|%(trailers:key=Co-Authored-By,valueonly,separator=;)")
    fp = _git("log", sha, "--first-parent", "--format=%cs|%s")
    if not log or fp is None:
        return None
    rows = [ln.split("|", 3) for ln in log.splitlines() if ln]
    dates = sorted(r[0] for r in rows)
    merges = [r for r in rows if len(r[1].split()) > 1]
    plain = [r for r in rows if len(r[1].split()) <= 1]
    months, days = {}, {}
    for d in dates:
        months[d[:7]] = months.get(d[:7], 0) + 1
    for d in sorted(set(dates)):
        days[d[:7]] = days.get(d[:7], 0) + 1
    prs = set()
    for ln in fp.splitlines():
        d, _, s = ln.partition("|")
        m = re.match(r"Merge pull request #(\d+)", s) or re.search(r"\(#(\d+)\)$", s)
        if m and d >= since:
            prs.add(int(m.group(1)))
    claude = [r for r in plain if any(t.strip().startswith("Claude") for t in r[3].split(";"))]
    rest = [r for r in plain if r not in claude]
    authors = {}
    for r in plain:
        authors[r[2]] = authors.get(r[2], 0) + 1
    return [
        "- 最初のコミットの日：%s" % dates[0],
        "- 最後のコミットの日：%s" % dates[-1],
        "- コミット：%d 件（マージを除くと %d 件、マージは %d 件）" % (len(rows), len(plain), len(merges)),
        "- 月ごとのコミット：" + "、".join("%s が %d 件" % kv for kv in sorted(months.items())),
        "- コミットのある日：%d 日（" % len(set(dates)) + "、".join("%s が %d 日" % kv for kv in sorted(days.items())) + "）",
        "- %s 以降にマージした pull request：%d 件" % (since, len(prs)),
        "- マージを除くコミットのうち、`Co-Authored-By` に Claude があるもの：%d 件。無い %d 件は%s" % (
            len(claude), len(rest),
            " dependabot のコミット" if all(r[2] == "dependabot[bot]" for r in rest) else "、dependabot 以外を含む"),
        "- マージを除くコミットの作者の名：" + "、".join(
            "%s が %d 件" % kv for kv in sorted(authors.items(), key=lambda kv: (-kv[1], kv[0]))),
    ]


def gate_problems(submit):
    sha = re.search(_GATE_SHA, submit, re.M)
    since = re.search(_GATE_SINCE, submit, re.M)
    if sha is None or since is None:
        return ["SUBMIT.md に数えた先か、pull request を数える日が無い"]
    lines = gate_lines(sha.group(1), since.group(1))
    if lines is None:
        return ["数えた先 %s が履歴に無い（浅い複製なら fetch-depth: 0 が要る）" % sha.group(1)[:7]]
    have = set(submit.splitlines())
    return ["git では「%s」" % ln for ln in lines if ln not in have]


_bib = io.open(os.path.join(ROOT, "paper.bib"), encoding="utf-8").read()
_PP = paper_problems(_paper, _submit, _readme, _bib)
_GP = gate_problems(_submit)

# 壊した写し。paper.md の側と SUBMIT.md の側の両方で、決めたことに当たらない形を作る。
_paper_breaks = [(b, _bib) for b in [
    _paper.replace("title: '", "title: '`", 1).replace(": deterministic", "`: deterministic", 1),
    _paper.replace("# Acknowledgements\n", ""),
    _paper.replace("# References", " ".join(["word"] * 400) + "\n\n# References"),
    re.sub(_flex("Claude Code"), "an agent", _paper),
    re.sub(_flex("The language model is not an author."), "", _paper),
    re.sub(r"^Four trade-offs", "Five trade-offs", _paper, flags=re.M),
    re.sub(_flex("across three repositories, run in continuous"), "across four repositories, run in continuous", _paper),
    re.sub(_flex("by the three repositories that use the tool"), "by the two repositories that use the tool", _paper),
    re.sub(_flex("Three repositories vendor the module"), "Two repositories vendor the module", _paper),
    _paper.replace("[@luger2022]", "[@luger2021]"),
] + [re.sub(_flex(lab), "", _paper) for lab in _AI_LABELS] + [
    # 履歴に出てくるモデルを、一つずつ開示から外す。後ろに版の続く名（5 と 5.5）を取り違えないことも見る。
    re.sub(_flex(m) + r"(?!\.?\d)", "a model", _paper) for m in (_MODELS or [])]] + [
    (_paper, _bib + "\n@misc{unused2026,\n  title = {Not cited},\n  year = {2026}\n}\n"),
    (_paper, _bib.replace("doi     = {10.3758/s13428-015-0664-2}", "doi     = {10.3758/s13428-015-0664-3}")),
]
_sec = re.search(r"^## 関門の数（git から数えた）\n.*?(?=^## )", _submit, re.M | re.S)
_gate_breaks = [_submit.replace(re.search(_GATE_SHA, _submit, re.M).group(1), "0" * 40)] if _sec else []
if _sec:
    # 箇条の数を一つずつずらす。pull request を数える日は外す（ずらしても正しいことがある）。
    for _ln in [x for x in _sec.group(0).splitlines() if x.startswith("- ") and not re.match(_GATE_SINCE, x)]:
        for _m in re.finditer(r"\d+", _ln):
            _bumped = _ln[:_m.start()] + str(int(_m.group(0)) + 1).zfill(len(_m.group(0))) + _ln[_m.end():]
            _gate_breaks.append(_submit.replace(_ln + "\n", _bumped + "\n", 1))
_paper_break_ok = sum(1 for b, bb in _paper_breaks
                      if (b, bb) != (_paper, _bib) and paper_problems(b, _submit, _readme, bb))
_gate_break_ok = sum(1 for b in _gate_breaks if b != _submit and gate_problems(b))
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
_words = len(re.sub(r"^---\n.*?\n---\n", "", _paper, flags=re.S).split())
check(".zenodo.json の表題が paper.md と揃い、SUBMIT.md の点検表が済みとした節と語数を paper.md が満たし、"
      "所属は ZEN University, Japan の一つだけで、本文が大学の仕事ではなく大学が認めてもいないと書き、"
      "表題に逆引用符が無く、AI usage disclosure が履歴に出てくるモデルをすべて名指しし、本文の数が README と合い、"
      "SUBMIT.md の関門の数が git と合う（壊した写しでは落ちる）",
      _zenodo["title"].startswith(_paper_title) and not _PP and not _GP
      and _affil_ok(_paper) and all(b != _paper and not _affil_ok(b) for b in _affil_breaks)
      and _paper_break_ok == len(_paper_breaks) and len(_gate_breaks) > 1 and _gate_break_ok == len(_gate_breaks),
      "語数 %d / 食い違い %s / モデル %s / 所属の一文 %s / 壊した写しで落ちる 所属 %d・論文 %d / %d・関門 %d / %d" % (
          _words, " / ".join(_PP + _GP) or "無し", ", ".join(_MODELS or []) or "読めない",
          "有り" if _affil_ok(_paper) else "無し",
          sum(1 for b in _affil_breaks if b != _paper and not _affil_ok(b)),
          _paper_break_ok, len(_paper_breaks), _gate_break_ok, len(_gate_breaks)))

print("\n" + "-" * 58)
if failures:
    print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("%d 件すべて通りました。" % passed)
