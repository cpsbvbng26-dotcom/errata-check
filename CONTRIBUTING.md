# 手を入れるときに

Issue も pull request も歓迎する。**登録は要らない**（一次資料の閲覧・issue の作成・
変更の提案のいずれにも、承認や支払いを求めない）。

## 不具合を知らせる

<https://github.com/cpsbvbng26-dotcom/errata-check/issues> に立てる。「不具合の報告」の様式
（`.github/ISSUE_TEMPLATE/bug_report.yml`）が、次のものを必ず書く形になっている。

1. 出た出力（そのまま貼る）
2. 期待していた出力
3. 再現の手順。走らせたコマンドと、宣言（`audit.toml`）の問題が出た部分
4. errata-check の版（`--version`）か、写した commit
5. 環境。OS、Python と pypdf の版、GitHub Action で使ったかどうか

偽陽性はとくに知らせてほしい。この道具は継続的インテグレーションの門として
使うことを前提にしており、誤って落ちることは、落ちないことより悪い。

## 変更を出す

```
python3 tests/check_tool.py     # 全部通ってから出す。項目数は README が名乗る
```

検査を足すときは、壊す試験も一緒に足す。

新しい検査を書いたら、`tests/check_tool.py` に「通る状態を壊して、その検査が
ちょうど落ちること」を確かめる場合を足す。壊しても落ちない検査は、何も見ていない。
この決まりのために、試験は検査ごとに壊し方を持っている。その数は README が名乗り、
名乗る数がずれたら落ちる。数をここに書き写さないのは、写しが古くなるからである。

## 判定に推論を入れない

この道具の設計上の約束である。大規模言語モデル、埋め込み、類似度、あいまい照合の
いずれも、判定に入れない。あるか無いか、一致するかしないかだけで決める。

理由は、出力を人が確かめ直さなくてよくするためである。確かめ直しが要るなら、
継続的インテグレーションの門にはならない。この約束を外す提案は受け付けない。

空白と字体の正規化だけは行う。何をどう正規化するかは README の「空白の扱い」にある。
それ以上の寛容さは、推論を持ち込むことになる。

## 支えの範囲と、これからの見込み

- **維持しているのは著者一人である**（根本卓哉）。組織の後ろ盾は無い。
- issue への返答は**数日から一週間**を目安とする。約束ではない。
- 後方互換。宣言の書式は、既にある宣言が落ちる形では変えない。変える必要が出たら
  版の番号を上げ、README に移行の手順を書く。
- 範囲。凍結された一次資料と、それを説明する訂正の記録との突き合わせに限る。
  原稿そのものの校正、書誌の整形、剽窃の検出は範囲の外である。

## ライセンス

MIT。手を入れたぶんも同じ条件で扱われる。

## 突き合わせの受付 / Checked intake

2026-12-01 から、誤りの知らせ（`error-report.yml`）は「突き合わせの受付」で確かめる。
人が嘘をつくこと一般は、仕組みでは止められない。受けるのは、申し立てた人がその場で書けない出どころと突き合わせられる申し立てだけで、通らないものと確かめられないものは自動で退ける。
確かめるのは一つだけである。「書いてあること」の語が、「どこか」の欄に書いた所（このリポジトリのファイル、配っている頁、このリポジトリが写しを持つ DOI の PDF か翻刻）に、そのとおりにあること。空白の違いと文字の幅は見ない。頁や節は確かめず、文書の全体を探す。
あればラベル「quote verified」を付ける。それが誤りかどうかは、人が読んで決める。なければ、ラベル「not verified」と決まった文のコメントを付け、その申し立ては受け付けない。本文を直すか、新しい issue で出し直せば、もう一度確かめる。
突き合わせの受付は、どの issue も閉じず、鍵も掛けない。どの issue も人が読む。言葉の並びでは、法令が受けて扱うことを求める求め（削除・権利・個人の情報・人についての記述・同意の撤回。どの言語でも）を、誤りの知らせと見分けきれないためである（2026-11-15）。
そう読める語を含む issue には、ラベル「needs a person」も付ける。人への目印で、これに頼って何かを決めることはない。
持ち主が開き直したり直したりしたときは、何もしない。
コメントと実行の記録は、決まった語と issue の番号だけを書き、issue に書かれたことを写さない。
道具は `.github/checked-intake/verify.js`、確かめる先は `.github/checked-intake/config.json` にある。

From 2026-12-01, error reports (`error-report.yml`) are checked by the checked intake.
No system can stop a person from lying in general. Only claims that can be checked against a source that the claimant does not write at the moment of claiming are accepted; a claim that fails, or cannot be checked, is turned away automatically.
One thing is checked: that the words under "What it says" occur, as written, at the location under "Where" (a file of this repository, a page that it serves, or the PDF or transcription of a DOI of which it holds a copy). Differences of white space and character width are ignored. The page or section is not checked; the whole document is searched.
If they occur, the label "quote verified" is added, and whether it is an error is decided by a person. If they do not, the label "not verified" and a fixed comment are added, and the claim is not accepted; editing the issue, or opening a new one, runs the check again.
The checked intake never closes or locks an issue; a person reads every one. No list of words can tell every request that the law requires the operator to receive (removal, rights, personal data, statements about a person, the withdrawal of a consent, in any language) from an error report (2026-11-15).
An issue with words that read as such a request also gets the label "needs a person": a signal for the person, never relied on.
When the owner of the repository reopens or edits an issue, nothing is done.
Comments and logs carry only fixed words and the issue number, never what the issue says.
The script is `.github/checked-intake/verify.js`; what it checks against is in `.github/checked-intake/config.json`.
