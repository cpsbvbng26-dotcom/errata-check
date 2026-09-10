# errata-check

[![検査](https://github.com/cpsbvbng26-dotcom/errata-check/actions/workflows/verify.yml/badge.svg)](https://github.com/cpsbvbng26-dotcom/errata-check/actions/workflows/verify.yml)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22685687.svg)](https://doi.org/10.5281/zenodo.22685687)

**凍結された公開物に対して、正誤表のほうを機械で監査する。**

DOI が付いて公開された PDF は、もう直せない。直せるのは正誤表のほうである。
だから正誤表は、時間とともに一次資料からずれていく。

- 引用が一字変わる
- 箇所を数え落とす
- 「解決した」に書き換わる
- 最終更新の日付が古いまま残る

そのずれを CI で落とすための道具である。

```
pip install pypdf
python3 errata_check.py audit.toml
```

判定に推論を使わない。あるか、無いか、一致するか、しないか。LLM も類似度も
使わない。だから出力を人が確かめ直す必要が無い。

---

## 何を見るか

| | 内容 |
| --- | --- |
| **引用** | 正誤表が「印字されている」と述べた文が、本当にその PDF にあるか。逆に「印字されていない」と述べたものが、本当に無いか |
| **完全性** | 宣言した件数だけ記述が挙がっているか（**数え落としを止める**） |
| **不在** | 「同梱されている」と謳われたファイルが、本当に無いか |
| **数値** | 正誤表が名乗る件数が、実際にコマンドを走らせた結果と一致するか |
| **未解決** | 解決しないと決めた項目が、こっそり解決済みに書き換わっていないか |
| **凍結** | 一次資料そのものが差し替わっていないか（SHA-256） |
| **日付** | 最終更新が、本文に書かれたどの日付よりも古くないか |

いちばん効くのは 完全性 と 未解決 である。ほかは書き間違いを捕まえる。この二つは、
書き手が自分に都合よく直すことを捕まえる。

### 分野ごとに、紙面から決定的に確かめられるもの

引用の一致だけが検査ではない。分野が違えば、紙面から機械で確かめられるものも違う。

| | 内容 | 効く分野 |
| --- | --- | --- |
| **検定** | 印字された検定統計量と自由度から `p` を計算し直し、印字された `p` と合うか（`t` / `F` / `χ²` / `r`） | 心理学・医学・経済学など実証系 |
| **GRIM** | 整数を平均した値が、その標本数で本当に到達できる値か | 同上 |
| **識別子** | ORCID・ISBN・ISSN の検査数字（チェックディジット） | 全分野 |
| **算術** | 印字されている数どうしの関係（無作為化 = 解析 + 脱落 など） | 臨床試験・実験 |
| **元号** | 和暦と西暦が対応しているか | 史学・文書研究 |
| **参考文献** | 引用した典拠の**どの箇所が、どの主張を支えているか**。宣言し忘れた引用と、使っていない参考文献も落ちる | 人文系・全分野 |

```toml
[[statistic]]
source = "paper"
text = "t(28) = 2.14, p = .04"
test = "t"
df = [28]
value = 2.14
reported = "p = .04"        # 印字どおり。精度と不等号をここから読む

[[grim]]
source = "paper"
text = "Mean score 3.44 (n = 25)"
mean = 3.44
n = 25

[[identifier]]
source = "paper"
kind = "orcid"               # orcid / isbn13 / isbn10 / issn
value = "0009-0000-1406-0547"

[[arithmetic]]
label = "無作為化 120 = 解析 112 + 脱落 8"
source = "paper"
texts = ["120 participants randomised", "112 were analysed", "8 were lost"]
op = "sum"
values = [112, 8]
equals = 120

[[era]]
source = "record"
text = "昭和十八年"
gregorian = 1943
```

**「誤っていること」も宣言できる。**`consistent = false` と書くと、
計算し直した `p` が印字と**合わないこと**のほうを検査する。正誤表が
「この箇所は誤っている」と述べたとき、**その指摘自体が正しいかどうか**を
機械で押さえるための欄である。

```
python3 errata_check.py examples/disciplines/audit.toml    # 31 項目
```

### 参考文献 —— 「読んだ」とは書かせない

内面は外から確かめられない。「読んだ」と宣言させても、それは証言であって検査では
ない。

「どの箇所が、どの主張を支えているか」は違う。公開された主張であり、その本を持つ者
なら誰でも反証できる。だから宣言させるのは読書ではない。指し示しのほうである。

```toml
[[reference]]
key      = "Nietzsche 1967"
edition  = "The Will to Power, Kaufmann & Hollingdale trans., Vintage, 1967"
locus    = "§1067"
role     = "用語の出所"
supports = "「力への意志」という語の出どころ。主張そのものは支えていない"
caveat   = "遺稿の編纂物であり、著者自身が公刊した順序ではない"
```

`role` は五つだけとする。曖昧な「参考」を認めない。

| | |
| --- | --- |
| `直接支持` | その主張を、その典拠が述べている |
| `用語の出所` | 語や概念の由来。主張の支えではない |
| `対立見解` | 反対の立場として引く |
| `背景` | 位置づけのため。主張は支えていない |
| `反例` | 自説に不利なものとして挙げる |

本文の側からも見る。

```toml
[reference_policy]
pattern      = "\\(([^()]{2,60}?\\s\\d{4}[a-z]?)\\)"
require_all  = true      # 本文の引用がすべて宣言されているか
require_used = true      # 宣言した参考文献がすべて使われているか
```

`require_used` が効く。本文で使っていない文献を並べて厚く見せることが、構造的に
できなくなる。

この検査は、その本が本当にそう述べているかを見ない。見られないからである。
見られないことを、見たふりにしない。確かめられるのは、宣言と紙面の整合だけである。

見本は [`examples/references/`](examples/references/)（21 項目）にある。

### 検定と GRIM の出どころ

どちらも既存の考え方である。**新しい統計手法ではない。**

- **検定の再計算** —— [statcheck](https://doi.org/10.3758/s13428-015-0664-2)（Nuijten ら 2016）と同じ考え方
- **GRIM** —— [Brown–Heathers](https://doi.org/10.1177/1948550616673876)（2017）の GRIM テストと同じ考え方

**実装は独立で、それぞれのコードは見ていない。**違いが一つある。statcheck は
論文から統計量を**自動で抜き出す**。この道具は**宣言されたものだけ**を見る。
抜き出しの誤りによる偽陽性が出ない代わりに、**宣言し忘れた箇所は見ない。**
どちらが良いという話ではなく、目的が違う。ここは網羅ではなく、
**正誤表に書いたことが本当かどうか**を押さえる道具である。

### 分布は自分で実装している

`p` を出すのに scipy は使わない。単一ファイルで配れなくなるためである。
正則化不完全ベータ・ガンマを Lentz の連分数と級数で書いてある。

**実装が正しいかどうかは、実装だけでは分からない。**公表されている統計数値表の
5% 点・1% 点と **11 点で突き合わせて**確かめている（`tests/check_tool.py` の 3 節）。

## 宣言の書き方

```toml
[document]
path = "ERRATA.md"

[[source]]
id = "paper"
path = "paper.pdf"
sha256 = "9e0f27cb…"       # 無いと「宣言されていない」で落ちる

[[count]]
source = "paper"
group = "promise"
expect = 2                  # この種類の記述が 2 箇所あると宣言する

[[quote]]
source = "paper"
group = "promise"
where = "謝辞"
text = "the verification script is distributed together with this PDF"

[[quote]]                   # 「印字されていない」ことの宣言
source = "paper"
where = "改訂版の DOI"
text = "10.5281/zenodo.00000002"
present = false

[[absent]]
glob = "**/demo_verification.py"
reason = "同梱を謳っているが存在しない"

[[number]]
label = "検査の件数"
command = "python3 count.py"
extract = "(\\d+) checks"    # コマンドの出力からの取り出し方
pattern = "(\\d+) 項目の検査" # 文書の中の書き方

[[open_item]]
id = "E1"
heading_pattern = "^## E1 —"
must_say = ["この項目は解決しません"]
must_not_say = ["解決済み", "修正しました"]

[dates]
stamp_pattern = "最終更新: (\\d{4})年(\\d{1,2})月(\\d{1,2})日"
any_pattern = "(\\d{4})年(\\d{1,2})月(\\d{1,2})日"
```

`.json` でも書ける。TOML には Python 3.11 以降（`tomllib`）が要る。

動く見本が [`examples/minimal/`](examples/minimal/) にある。

```
python3 errata_check.py examples/minimal/audit.toml     # 19 項目
```

## 空白の扱い

PDF から取り出した文字列は、改行や空白の入り方が処理系で変わる。
比較の前に `NFKC` をかけ、幅ゼロの文字を落とし、**空白の連なりを一つに潰す。**
文字そのものは置き換えない。だから「引用が一字違う」は落ちるが、
「行が折り返された」では落ちない。

## この道具自身の検査

```
python3 tests/check_tool.py     # 68 項目
```

**検査の道具は、通ることでは信用できない。**何も見ていなくても全部通るからである。
そこで、通る状態を作ってから**一つずつ壊し、壊したところがちょうど落ちること**を
確かめている。落ちなければ、その検査は何も見ていない。

壊す先は 26 通りある。引用を一字変える、無い引用を「ある」と宣言する、
無いはずの記述を一次資料に置く、件数を偽る、PDF を差し替える、`sha256` の宣言を消す、
無いはずのファイルを置く、名乗る件数をずらす、コマンドの側の結果をずらす、
「解決しない」を消す、「解決済み」に書き換える、見出しを消す、日付を古くする、
印字された `p` を偽る、自由度を偽る、到達できない平均を到達できると宣言する、
ORCID を一桁変える、ISBN を一桁変える、内訳の和を崩す、和暦の対応を変える、
平文の一次資料を書き換える、参考文献の箇所を消す、何を支えているか書かない、
決めていない使い方を書く、引用の宣言を忘れる、使っていない参考文献を宣言する。
最後に**偽陽性を出さないこと**（行が折り返されても落ちないこと）も見る。

検査に使う PDF は [`tests/make_pdf.py`](tests/make_pdf.py) が依存なしで書き出す。
本物の論文を使うと、通ったのが道具のおかげなのかその PDF のおかげなのかが
分からなくなるためである。

---

## これは何ではないか

既にあるものと混同しないために書いておく。

| 既存 | 何をするか | この道具との違い |
| --- | --- | --- |
| [showyourwork](https://github.com/showyourwork/showyourwork) | CI で論文 PDF を作り直し、図と数値をコードと同期させる | **原稿を作り直せることが前提。**凍結された PDF には使えない |
| [continuous analysis](https://www.nature.com/articles/nbt.3780) | 解析パイプラインを CI で再実行 | 同上。出版後の監査ではない |
| [citecheck](https://arxiv.org/html/2603.17339) | 参考文献を Crossref 等に照会して自動修復 | 参考文献だけ。本文の引用は見ない |
| [ATIBA](https://arxiv.org/html/2609.04123) | 引用文脈と参照先の整合を LLM で判定 | 確率的。「uncertain」を返す |
| 学術誌の corrigendum | 訂正を別記事として出す | 散文。機械検査は無い |

**この道具は、正誤表が正しいかどうかを判定しない。**正誤表が一次資料と
食い違っていないかだけを見る。何を訂正とみなすかは人が決めることである。

## 限界

- PDF から取り出した文字列に依存する。取り出し方（pypdf）が変われば結果も変わる。
  合字や特殊な字形を使った箇所では、一致しないことがある
- 一次資料が画像だけの PDF なら、何も取り出せない。OCR は持たない
- 意味は見ない。引用が原文にあることは見る。その引用が文脈を歪めて切り取られて
  いないかは見ない
- 網羅しない。宣言された箇所だけを見る。書き落とした箇所は見ない
- 検定の再計算は、印字された値が内部で整合するかだけを見る。その検定を使うべき
  だったか、前提が満たされているかは見ない
- `[[number]]` は任意のコマンドを実行する。信用できる宣言だけを走らせること

## 引用

Zenodo にアーカイブされ、DOI が付与されている。**版ごとに DOI が違う。**
使った版の番号を書くこと。

| 版 | DOI |
| --- | --- |
| v0.2.0（いまの版） | [10.5281/zenodo.22649899](https://doi.org/10.5281/zenodo.22649899) |
| v0.1.0 | [10.5281/zenodo.22649054](https://doi.org/10.5281/zenodo.22649054) |

> 根本卓哉 (2026). *errata-check: Deterministic auditing of errata against frozen
> published artifacts / 凍結された公開物に対する、決定的な正誤表の監査* (v0.2.0).
> Zenodo. https://doi.org/10.5281/zenodo.22649899

```bibtex
@software{nemoto_errata_check_2026,
  author       = {Nemoto, Takuya},
  title        = {{errata-check: Deterministic auditing of errata
                   against frozen published artifacts}},
  year         = {2026},
  version      = {v0.2.0},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.22649899},
  url          = {https://doi.org/10.5281/zenodo.22649899}
}
```

引用のための情報は [`CITATION.cff`](CITATION.cff) にもある。

## AI の利用

[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-D97757?style=for-the-badge)](https://claude.com/claude-code)

この道具の実装は、Claude Code（Anthropic）を用いて書いた。`errata_check.py`、
`tests/check_tool.py`、`examples/`、README、`CITATION.cff` のいずれもそうである。

何を検査するかを決めたのは著者である。「凍結された公開物に対して、正誤表のほうを
決定的に監査する」という切り口、判定に推論を使わないという方針、宣言の書式、
通る状態を壊して落ちることまで確かめる試験の作り方 ―― これらは著者の判断である。

検査が報告する数値は、すべて実行して得たものである。AI は著作者ではない。いずれの
主張についても、責任は著者（根本卓哉）にある。

このリポジトリのコミットは `Claude` 名義であり、末尾に作業セッションを示す
`Claude-Session:` トレーラが付く。`git log --author=Claude` で辿れる。

Zenodo に登録した v0.1.0 と v0.2.0 のレコードには、この記載が無い。公開後に
ファイルは差し替えられないため、直せるのはこちら側だけである
（[self-correction](https://github.com/cpsbvbng26-dotcom/self-correction) の `TL-001`）。

## 出す先

**JOSS（Journal of Open Source Software）に出す。**論文は [`paper.md`](paper.md)、
手順と、通らない見込みは [`SUBMIT.md`](SUBMIT.md) にある。**結果はまだ出ていない。**

---

## ライセンス

[MIT](LICENSE)。© 2026 根本卓哉（Takuya Nemoto）

## 使われている場所

- [trinity-infinity](https://github.com/cpsbvbng26-dotcom/trinity-infinity) —— 著者本人による、自分の三篇の正誤表の監査
