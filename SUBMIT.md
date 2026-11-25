# JOSS へ出す手順

手順書です。まだ出していません。

2026年9月10日、いまは出さないと決めました。受け付け前の四つの関門のうち二つが
欠けており、埋まるのは時間が経ってからです（下の「四つの関門」）。
足りないと分かっているものを出して門前払いを受けるより、埋めてから出します。
出すこと自体をやめたのではありません。

2026年11月11日に、出す時期を決めました。Sophaxis のコードと一緒に、2027年5月以降に出します。
関門 1 が満ちるのは 2027年3月7日より後で、その前に来ます。下の「いつ出すか」は、その日付を必要条件として残しています。

2026年11月23日に、規程を読み直しました（下の「2026年11月23日に読み直したもの」）。出す時期の決めは変えていません。
読み直して分かった障害は、その節の「規程に照らした障害」に書きました。

2026年11月25日に、2026年11月24日の規程でもう一度読み直しました（下の「2026年11月25日に読み直したもの」）。
点検表の一行ずつに、規程の文と、いまの状態と、直したものを当てています。出す時期の決めは変えていません。

## 出すもの

| | |
| --- | --- |
| リポジトリ | <https://github.com/cpsbvbng26-dotcom/errata-check> |
| 論文 | [`paper.md`](paper.md) と [`paper.bib`](paper.bib)。語数の決まりは下の「原文を読んで直したもの」 |
| ライセンス | MIT（OSI 承認） |
| 言語 | Python 3。依存は PDF を読むときの `pypdf` だけ |
| 試験 | `python3 tests/check_tool.py`。項目数と壊す先の数は README が名乗り、検査が突き合わせる |

## 出す前に要るもの

| | いまの状態 |
| --- | --- |
| **リリースを切る** | 済んだ。`v0.3.0`、2026年9月10日 08:46 UTC 公開 |
| **保管先の DOI** | 取れた。`10.5281/zenodo.22685687`（利用者から受け取った番号である。こちらから Zenodo は開けない） |
| **版の番号** | `v0.3.0`。ただしタグの中の `CITATION.cff` は `0.2.0` のまま、`pyproject.toml` はタグに無い（self-correction の `TL-002`）。次の版（0.4.0 の予定）は、下の「版を切るコミットの形」で揃える |

旧版の DOI は残します。`10.5281/zenodo.22649899` は `v0.2.0` の記録であり、
写して使っている `autonomy-and-self-cultivation` と `naval-gazette-notes` は
その版を指しています。版と番号が対応しているので、書き換えません。

## 出す前の点検表

この文書が引いている JOSS の規程（「受け付け前の四つの関門」と「原文を読んで直したもの」）を、
一行ずつの点検に直したもの。`[x]` は済み、`[ ]` はまだ。出すのは早くても 2027年3月7日より後。
関門の行の頭の札は、2026年11月25日に足しました。「いま満たす」「日付で満ちる」「満たさない」のどれかです。

関門（`docs/submitting.md` の「Pre-review screening criteria」）

- [ ] 関門 1（日付で満ちる）：公開の開発履歴が六か月を超えている。2027年3月7日までは満たさない。コミットが数日に集中していないこと。数は下の「関門の数（git から数えた）」、日付の出し方は下の「関門 1 の日付」
- [x] 関門 2 の最低限（いま満たす）：研究に使われている証拠のうち、規程が最低限とする開発者自身の利用。三つのリポジトリで、凍結された成果物の正誤表を CI で監査している
- [ ] 関門 2 の望ましい形（満たさない）：著者のほかの利用（"ideally by others"）。著者のほかに使った記録は無い。開発者自身の利用で足りるかは、編集者が決める
- [x] 関門 3（いま満たす）：開かれた開発の実践。単独の著者に求める複数の目印（タグ付きのリリース・変更履歴・試験と CI・文書・`CONTRIBUTING.md`・支えの範囲）がそろう。公開のコミットの履歴は短い
- [ ] 関門 4（満たさない）：時間をかけた反復。2026年9月18日より後は、変更をすべて pull request で残している。コミットは 2026年9月と 2026年11月に集まり、使いながら直した跡として読める長さにはまだ足りない

規程が「受け付けられない」と書く形（2026年11月23日に読み直して足した。原文は下の「規程に照らした障害」）

- [ ] 単独の著者で、著者のほかの関与の証拠が無い。`review_criteria.md` の「Collaborative effort」は、これを「Not acceptable」とする
- [ ] 出す著者が、コミットの履歴から見て大きく寄与している。いまの履歴では、マージを除くコミットのほとんどに Claude が共著者として載る
- [ ] 新しいソフトウェアなら、同僚が試している。試したという記録は無い
- [ ] 小さな道具や一つの機能だけの梱包ではない（"Minor utility"）。本体は一つのファイルで、そう読まれうる。読むのは編集者である（下の「規程に照らした障害」）

論文（`paper.md` と `paper.bib`）

- [x] `paper.md` に、JOSS が求める節がある：`Summary`・`Statement of need`・`State of the field`・`Software design`・`Research impact statement`・`AI usage disclosure`・`Acknowledgements`・`References`
- [x] `paper.md` の本文が 750〜1750 語に収まる
- [x] `paper.md` の表題に逆引用符を使っていない（2026年10月7日に論文の手引きに足された決まり）
- [x] 外部の採用が無いことを、`Research impact statement` に書いてある
- [x] 言語モデルの利用を、`AI usage disclosure` に規程が求める三点と確かめ方で書いてある。使ったモデルを版まで名指ししている。言語モデルを著者にしていない
- [x] `paper.md` の節が、上の並びの順にある（2026年11月25日に検査に足した）
- [x] `paper.bib` の DOI を、登録機関の記録と突き合わせた（2026年11月23日と 2026年11月25日、Crossref。下の「2026年11月23日に読み直したもの」と「2026年11月25日に読み直したもの」）
- [x] 引いた鍵と `paper.bib` の項目が一つずつ対応し、DOI の欄が DOI の形をしている（検査が見る）
- [x] `State of the field` が、訂正と撤回の登録（Crossref の更新の記録と Retraction Watch のデータ）と比べている（2026年11月25日）
- [x] JOSS の組版（inara）で PDF の下書きを作る仕事がある（`.github/workflows/paper.yml`、2026年11月25日）
- [ ] `Confirmation of review` の言明に、著者が署名している。この段の文は Claude が書いたもので、Claude は代わって署名できない。`paper.md` を変えたコミットはどれも Claude を共著者に持ち、署名の記録は無い（検査が見る）
- [ ] `paper.md` の `date` が出す日である。いまの `23 November 2026` は下書きの日付で、出す日にその日の日付にする

リポジトリ

- [x] OSI 承認のライセンス（MIT、`LICENSE`）
- [x] その言語の慣行に沿った梱包（`pyproject.toml`）
- [x] タグ付きのリリースと保管先の DOI（`v0.3.0`、`10.5281/zenodo.22685687`）
- [ ] 版の番号が、タグの中でも揃っている。`v0.3.0` のタグの中の `CITATION.cff` は `0.2.0` のまま（self-correction の `TL-002`）。次の版で揃える。リリースは作業環境から切れない（タグの push は 403）
- [x] 試験と CI（`tests/check_tool.py`、`.github/workflows/verify.yml`）
- [x] 変更履歴（`CHANGELOG.md`）と、手を入れるときの文書（`CONTRIBUTING.md`）
- [x] 入れ方と依存の一覧（README の「入れる」、`pyproject.toml`）。複製から `pip install ".[pdf]"` で入り、`errata-check` のコマンドが動く（2026年11月25日に確かめた）
- [x] 手を入れる・不具合を知らせる・助けを求める道筋が、英語でも読める（`CONTRIBUTING.md` の「In English」、2026年11月25日）
- [x] 保管先の DOI が版ごとの DOI である（2026年11月24日に規程が求めた。README の版の表の DOI は、DataCite の記録でどれも `IsVersionOf` を持つ）

出す日

- [ ] 2027年3月7日より後であること。日付は必要条件であって十分条件ではない（下の「いつ出すか」）
- [ ] 2027年5月以降に、Sophaxis のコードと一緒に出すこと（2026年11月11日の決め）

`paper.md` の節・語数・表題・開示の行と、下の「関門の数（git から数えた）」は、`tests/check_tool.py` が
`paper.md` と git を読んで確かめている。節の名前と語数の範囲は、この表から読む。

## 版の番号について

`v0.2.0` のタグから 87 行離れたまま、`__version__` は `0.2.0` を名乗っていました。
参考文献の使い方を宣言させる検査が丸ごと入っているのに、番号が動いていません。
**同じ番号が別の中身を指す**という、この道具が捕まえるために書かれたもの
そのものです（`trinity-infinity` の `E1` と同じ形）。

`__version__` を `0.3.0` にしました。リリースはこの番号で切ります。

写して使っている側は影響を受けません。三つの複製は、それぞれが名乗っている
タグ（`v0.2.0` / `v0.1.0`）の中身に MIT の権利表示 25 行を足したもので、
中身と番号は対応しています。

### リリースのあとに直したもの

`CITATION.cff` の三行を、受け取った番号で埋めました。

```
doi: 10.5281/zenodo.22685687
version: 0.3.0
date-released: "2026-09-10"
```

README の DOI の記章も同じ番号にしました。`10.5281/zenodo.22649899` は
`v0.2.0` の記録として残ります。

### 版を切るコミットの形（2026年11月23日に決めた）

`TL-002` は、タグが指したコミットの中で、版を書いた四か所が揃っていなかったことから起きました。
タグを切るのは作業環境の外です。だから、タグが指すコミットそのものが揃う形を先に決め、検査で留めます。

版と版のあいだは、四か所（`errata_check.py` の `__version__`、`pyproject.toml`、`CITATION.cff`、`CHANGELOG.md`）が、
最後に出した版を名乗ります。いまは `0.3.0` です。
`CITATION.cff` の `date-released` と `doi`、`pyproject.toml` の `Archive` は、変更履歴のその版の欄の日付と DOI に合わせます。
変更は変更履歴の `## 未リリース` に溜めます。

出していない版の番号は、四か所に書きません。`0.4.0.dev0` のような開発版の番号も使いません。
四か所は、GitHub の引用の欄、Zenodo、PyPI、`--version` が読みます。出す前に新しい番号を書けば、出していない版を出したと書くことになります。
`CITATION.cff` は版と日付と DOI を組で持ちます。開発版の番号には、組になる日付も DOI もありません。
これまでの変更履歴と検査も、この形でした。書いて決めたのは 2026年11月23日です。

版を切るコミット（タグが指すコミット）では、四か所が新しい版を名乗ります。
変更履歴の `## 未リリース` は `## [版] — 日付` になり、その下の DOI の行は、決めた次の一文になります。

```
DOI: 未付与（Release と Zenodo の版ができたあとに、受け取った番号をここに書きます）
```

そのコミットの `CITATION.cff` には `doi` を置かず、`pyproject.toml` には `Archive` を置きません。
新しい版の DOI はまだ無く、前の版の DOI を置けば、別の中身を指すからです。
`CITATION.cff` の `date-released` は、変更履歴の見出しの日付と同じにします。
README の版の表は、DOI のある版だけを並べたままにします。

版を切ったあとのコミットで、受け取った DOI を変更履歴・`CITATION.cff`・`pyproject.toml`・README に書きます。
`v0.3.0` のときの「リリースのあとに直したもの」と同じ順です。

`tests/check_tool.py` は、四か所がこの二つの形のどちらにも当たらなければ落とします。
いまの中身から版を切るコミットの形を作って通ることと、どちらの形にも当たらない写しが落ちることも見ます。
PyPI へ出す仕事（`.github/workflows/pypi.yml`）は、タグの中でこの検査を走らせます。

タグ・GitHub の Release・Zenodo の版は、運営者のアカウントから作られます。作業環境からは作れません。
タグの push は 403 を返し、Zenodo の操作は運営者のアカウントでしかできません。

## 受け付け前の四つの関門（規程の原文に当たった）

`openjournals/joss` の `docs/submitting.md`（2026年8月26日の版）を読みました。
「Pre-review screening criteria」に四つあり、一つでも欠けると門前で却下されます。

| | 関門 | いまの状態 |
| --- | --- | --- |
| 1 | 公開の開発履歴が六か月を超えていること。数日や数週に集中したものは受け付けない。コミットの分布を自動で検査する | 欠けている。公開は 2026年9月7日、17 コミットが 2 日に集中 |
| 2 | 研究に使われている証拠。最低でも開発者自身が使っていること。将来の見込みでは足りない | 満たしている。三つのリポジトリで、凍結された成果物の正誤表を継続的インテグレーションで監査している |
| 3 | 開かれた開発の実践。一人で書いているものは、複数の目印が要る —— 続いたコミット、タグ付きのリリースか変更履歴、試験と CI、明確な文書、`CONTRIBUTING`、支えの範囲の表明 | 半分。リリース・試験・CI・文書はある。`CONTRIBUTING` と支えの範囲を足した。続いたコミットが無い |
| 4 | 時間をかけた反復。一度にまとめて書かれたものは、反復して育っていない証拠と見なされる | **欠けている** |

四つのうち二つが欠けています。却下される見込みは、この二つによる。

規程は続けてこう書いています。

> A desk rejection on these grounds may be a "not yet," rather than a "never."
> ... Fix the gaps, continue developing openly, and resubmit in six months or more.

「まだ」であって「決して」ではありません、と規程自身が書いています。却下されれば、何が
足りないかを具体的に書いた通知が来ます。それは六か月後に埋めるべきものの一覧になります。

## 関門の数（git から数えた）

2026年11月23日に数えました。関門 1・3・4 に掛かる事実です。数を増やすための活動は足していません。

数えた先は `main` の `70523c293d62b0e6c2dba33e32dd531e1962623d` です。
2026年11月23日にこの節を書き始めた時点の `main` の先端で、#57 のマージです。
数えた先を固定しているので、あとのコミットでこの数は動きません。`tests/check_tool.py` が git から数え直し、一行でも違えば落とします。

- 最初のコミットの日：2026-09-07
- 最後のコミットの日：2026-11-19
- コミット：184 件（マージを除くと 132 件、マージは 52 件）
- 月ごとのコミット：2026-09 が 60 件、2026-10 が 15 件、2026-11 が 109 件
- コミットのある日：28 日（2026-09 が 13 日、2026-10 が 6 日、2026-11 が 9 日）
- 2026-09-18 以降にマージした pull request：48 件
- マージを除くコミットのうち、`Co-Authored-By` に Claude があるもの：131 件。無い 1 件は dependabot のコミット
- マージを除くコミットの作者の名：Claude が 110 件、根本卓哉 が 19 件、Takuya Nemoto が 1 件、cpsbvbng26-dotcom が 1 件、dependabot[bot] が 1 件

日付は、書いた人の時刻での日付です（`git log --format=%as`）。
pull request は、`main` の第一の親の並びにあるマージと squash のコミットから、番号を拾って数えました（日付は `%cs`）。
GitHub の API の pull request の一覧とも、2026年11月23日に突き合わせて合いました。

GitHub の API が返すリポジトリの作成日は 2026年9月7日です。公開に切り替えた日は API から読めません（下の「関門 1 の日付」。2026年11月25日に直しました）。
2026年10月のコミットは少なく、2026年11月に多く集まっています。関門 4 が見る「反復」は、この分布で読まれます。

## 原文を読んで直したもの

規程を実際に読んで、`paper.md` に足りない節が三つあることが分かりました。

| 求められている節 | 前 | いま |
| --- | --- | --- |
| Summary | あった | ある |
| Statement of need | あった | ある |
| **State of the field** | **無かった** | 足した。`statcheck` との「作るか寄与するか」の判断も書いた |
| **Software design** | **無かった** | 足した。四つの取捨（推論を入れない／宣言を明示させる／単一ファイル／壊す試験） |
| **Research impact statement** | **無かった** | 足した。三つのリポジトリでの使用と、実際に見つかった不備。**外部の採用は無いと明記した** |
| AI usage disclosure | あった | 規程が求める三点（道具と場所／助力の中身／確認したという言明）に組み直した |

語数は 750〜1750 語と決まっています。前の版は 764 語で下限すれすれでした。
2026年9月10日に組み直した版は 1424 語でした。

あわせて `pyproject.toml`（規程は「その言語の慣行に沿った梱包」を求める）と
`CONTRIBUTING.md`（関門 3）を置きました。

## 2026年11月23日に読み直したもの

`openjournals/joss` の `docs/` を、コミット `9ab7c7c0494b17caca7e0cf98094d6585ae23abe`（2026-11-23）で読みました。
読んだのは `submitting.md`・`review_criteria.md`・`review_checklist.md`・`policies.md`・`paper.md`・`example_paper.md`・
`reviewer_guidelines.md`・`sample_messages.md`・`editing.md` です。

上の「2026年8月26日の版」は、その日までの最後の `docs/` のコミット `53aadb69db6060d83560d92a3cc7051e9dda7e84`（2026-08-25）に当たります。
この二つの差分を、ファイルごとに読みました。上の節は、8月の読みの記録としてそのまま残します。

### 変わったもの

| ファイル | 変わったこと | ここへの効き |
| --- | --- | --- |
| `submitting.md` | 提出の要件の末尾に、審査の基準と点検表を満たすことを求める一文が足された（2026-10-16） | 審査の基準（`review_criteria.md`）が、出す側の要件として明記された。基準の「Collaborative effort」が効く（下の「規程に照らした障害」） |
| `paper.md`・`example_paper.md` | 表題に逆引用符を使わない決まりが足された（2026-10-07） | `paper.md` の表題は使っていない。検査に足した |
| `sample_messages.md` | 却下のあとも pre-review と review の issue を消さない方針が書かれた（2026-11-19） | 下の「審査は公開の場で行われる」に書いたことと合う |
| `reviewer_guidelines.md`・`editing.md`・`sample_messages.md` | 審査の issue で、頼まれていない人が査読を申し出ても、原則として受けない（2026-08-31・2026-10-16） | 査読者は編集者が選ぶ |
| `editing.md` | rOpenSci と pyOpenSci の審査を経たものも、範囲と意義の確認を受ける | 関係しない |
| `policies.md`・`review_criteria.md`・`review_checklist.md` | 変わっていない | 言語モデルの方針、語数、求める節は、8月の版と同じ |

決めたことに効く原文は、次のとおりです。

> Finally, please review the [JOSS review criteria](https://joss.readthedocs.io/en/latest/review_criteria.html) and the [JOSS review checklist](https://joss.readthedocs.io/en/latest/review_checklist.html), and ensure that your submission meets them.

> Use software names as plain text in the YAML `title` field. Do not surround them
> with backticks to apply inline-code formatting.

> JOSS’s policy is that reviews (and pre-reviews) are part of the record of JOSS’s interaction with projects and people, and these records can be important to preserve for future interactions, as well as for understanding the scholarly literature and its processes.

### 前の読みで書き落としていたもの

8月の版にもあり、この文書が書いていなかった決まりです。

| 決まり | 原文 | 直したもの |
| --- | --- | --- |
| 開示はモデルの版まで | "The tools/models used (and versions) and where they were used (code, paper text, docs)." | `paper.md` に Claude Opus 5 と Claude Opus 5.5 を名指しした。履歴の `Co-Authored-By` に出てくるモデルを開示が全部名指ししているかを、検査が見る |
| 確かめ方を書く | "If AI tools were used, describe how they were used and how the quality and correctness of AI-generated content was verified." | `How correctness was verified` の段を足した |
| 謝辞の節 | "sections for Summary, Statement of need, State of the field, Software design, Research impact statement, AI usage disclosure, Acknowledgements, and References" | 節はあった。点検表と検査の並びに足した |
| 審査のやり取りに言語モデルを使わない | "AI is not allowed for conversational interactions between authors and editors or reviewers unless it is being used for translation purposes." | 下の「言語モデルの関与」に書いた |
| 既存の生態系の上に作る | "We particularly value work that builds upon or extends existing software ecosystems rather than reinventing solutions where quality alternatives already exist." | `paper.md` の `State of the field` が、分布を一から実装してはいないと読める文を持っていた。実際は自前の実装である。正しく書き直した |
| 人の寄与を示す | "Whether or not you use AI assistance in your development, submissions should demonstrate the irreplaceable human contributions: problem framing, key design decisions, thoughtful architectural choices, and practices that make software usable and sustainable for others." | 下の「規程に照らした障害」に書いた |
| 単独の著者 | 下の「規程に照らした障害」に引いた | 同上 |
| 著者の寄与はコミットの履歴で見る | 同上 | 同上 |
| 公開の issue と pull request | 同上 | 同上 |
| 同僚が試す | 同上 | 同上 |
| 小さな道具は受けない | 同上 | 同上 |

### `paper.md` で直したもの

| 箇所 | 前 | いま |
| --- | --- | --- |
| 分布の実装 | 公表の数値表と突き合わせ、一から実装してはいないと読める文 | モジュールの中に実装し、公表の数値表と突き合わせている。README の「分布は自分で実装している」と合わせた |
| 偽陽性の試験 | 頁の境で折り返した行でも落ちない | 空白と改行の違う引用でも落ちない。試験の 8 節がしていることに合わせた |
| `State of the field` | showyourwork と continuous analysis を挙げていなかった | README の「これは何ではないか」が挙げる二つを、引用つきで足した |
| `AI usage disclosure` | モデルは各コミットに残っている、とだけ書いていた | モデルを版まで名指しした。確かめ方の段を足した。Claude Code 本体の版は記録していないと書いた |
| 日付 | 10 September 2026 | 23 November 2026 |

語数は、検査が `paper.md` を数えて、点検表の範囲に収まることを確かめています。

### `paper.bib` で確かめたもの

2026年11月23日に、`api.crossref.org` の記録と突き合わせました。

| 鍵 | DOI | Crossref の記録 | 結果 |
| --- | --- | --- | --- |
| `nuijten2016` | `10.3758/s13428-015-0664-2` | Behavior Research Methods 48(4)、1205–1226。著者と題が合う。印刷版は 2016年12月 | 合う。DOI を書き足した |
| `brown2017` | `10.1177/1948550616673876` | Social Psychological and Personality Science 8(4)、363–369。題と副題が合う。印刷版は 2017年5月 | 合う。DOI を書き足した |
| `beaulieujones2017` | 書いていない | Nature Biotechnology 35(4)、342–346。2017年4月 | 新しく足した。著者・題・巻・号・頁は Crossref の記録から写した |
| `luger2022` | 無い | ソフトウェア。著者と年は showyourwork のリポジトリの `CITATION.cff` から写した | 新しく足した |

前の `paper.bib` には、DOI が一つもありませんでした。
書き足した二つの DOI は、README がすでに載せていた番号です。新しい番号は持ち込んでいません（決めごと 1）。
`beaulieujones2017` には、README が載せている頁の URL を書きました。

`CITATION.cff` と README の三つの版の DOI も、`api.datacite.org` の記録と突き合わせました。
版の名、公開日、種類が Software であることが、変更履歴の版の欄と合います。

### 規程に照らした障害

出す時期の決め（2027年5月以降、Sophaxis のコードと一緒に）は変えていません。
次のものは、時期が来ても、それだけでは埋まりません。原文は 2026年11月23日の版です。

単独の著者で、著者のほかの関与がありません。`review_criteria.md` の「Collaborative effort」は、この形をはっきり退けています。

> **Not acceptable:** Single author with no evidence of community engagement, external use, or collaborative input

同じ節は、単独の著者なら論文の中の証拠でもよいと書きます。`paper.md` は、著者のほかの利用は無いと書いています。

> For single-author projects, community engagement evidence in the paper is acceptable and may be the primary signal.

出す著者の寄与は、コミットの履歴で見られます。

> As part of the review process, you are asked to check whether the submitting author has made a 'substantial contribution' to the submitted software (as determined by the commit history)

> You must be a major contributor to the software you are submitting, and have a GitHub account to participate in the review process.

この履歴では、マージを除くコミットのほとんどに Claude が共著者として載り、作者の名も多くが Claude です（上の「関門の数」）。
規程は、言語モデルを使ったかどうかによらず、人の寄与を示すことを求めます。点検表には、最近の生成でないかを問う項目もあります。

> Whether or not you use AI assistance in your development, submissions should demonstrate the irreplaceable human contributions: problem framing, key design decisions, thoughtful architectural choices, and practices that make software usable and sustainable for others.

> **Development timeline:** Does the project show evidence of sustained development over time (preferably months or years) rather than rapid, recent code generation?

公開の issue と pull request が、六か月の公開の履歴の証拠として求められています。pull request はあります。issue は少数です。

> Projects developed privately are not eligible until there is a public record of open development: at least six months of public history prior to submission, with evidence of releases, public issues and pull requests.

新しいソフトウェアなら、同僚が試していることが求められています。その記録はありません。

> Whether a potential user can easily install, understand, and test the software. (If your software is new, please be sure a colleague has tried it.)

小さな道具と、一つの機能だけの梱包は受け付けません。errata-check は一つのファイルです。機能は一つではありませんが、一つのファイルであることをどう読むかは、編集者が決めます。

> "Minor utility" packages, including "thin" API clients, and single-function packages are not acceptable.

審査のやり取りでは、言語モデルを使えません。翻訳だけが例外です（下の「言語モデルの関与」）。

## 2026年11月25日に読み直したもの

`openjournals/joss` の `docs/` を、コミット `50d7440b4016aea5bfaa014c8e4d9b342a8dc62e`（2026-11-24）で読みました。
読んだのは `submitting.md`・`review_criteria.md`・`review_checklist.md`・`policies.md`・`paper.md`・`example_paper.md` です。
引いた文は、リンクの記法だけを外して写しています。

### 変わったもの

前の読み（`9ab7c7c0494b17caca7e0cf98094d6585ae23abe`）からの差分は、`editing.md`・`editorial_bot.md`・`submitting.md` にあります。
どれも、保管先の DOI を、査読した版の DOI にするという一文です。`submitting.md` は次のとおりです。

> Upon successful completion of the review, authors will make a tagged release of the software, and deposit a copy of the repository with a data-archiving service such as Zenodo or figshare, get a DOI for the archive of the software associated with that specific tag, and update the review issue thread with the version number and DOI.

README の版の表の DOI は、DataCite の記録でどれも `IsVersionOf` を持ちます。版ごとの DOI であり、全版をまとめる DOI ではありません。
査読のあとに出す版の DOI は、そのとき新しく作られます。タグと Zenodo の版は運営者のアカウントから作られ、作業環境からは作れません。

### 点検表の一行ずつ

`review_checklist.md` の項目を、上から順に当てました。「直したもの」が「なし」の行は、直すものが無かったか、いまは直せない行です。

| 項目 | JOSS の文 | いまの状態と根拠 | いま直せるか | 直したもの |
| --- | --- | --- | --- | --- |
| Repository | "Is the source code for this software available at the repository url?" | 公開。GitHub の API は `visibility` に `public` を返す | 直すものが無い | なし |
| License | "Does the repository contain a plain-text LICENSE file with the contents of an OSI approved software license?" | `LICENSE` は MIT の全文。GitHub の API は `spdx_id` に `MIT` を返す | 直すものが無い | なし |
| Contribution and authorship | "Has the submitting author made major contributions to the software? Does the full list of paper authors seem appropriate and complete?" | 著者は一人。マージを除くコミットのほとんどに Claude が共著者として載る（上の「関門の数」） | 直せない。公開した履歴は書き換えない | なし |
| Scope and significance | "Does this submission demonstrate clear research impact or credible scholarly significance as described in the JOSS guidelines?" | 使っているのは著者自身のリポジトリ（README の「使われている場所」）だけ | 直せない。外の利用は作れない | なし |
| Development timeline | "Does the project show evidence of sustained development over time (preferably months or years) rather than rapid, recent code generation?" | 最初のコミットは 2026-09-07。コミットは 2026年9月と 2026年11月に集まる | 直せない。時間が要る | なし |
| Open development | "For projects with recent public repositories, is there at least six months of public development history with evidence of releases, public issues/pull requests, and ideally external engagement?" | タグは `v0.1.0`・`v0.2.0`・`v0.3.0`。pull request はある。issue は少ない。外の関与は無い | 期間は日付で満ちる（下の「関門 1 の日付」）。外の関与は直せない | なし |
| Collaborative effort | "Does the project show evidence of community engagement such as contributions from multiple developers, issues/discussions from external users, or community influence on the development described in the paper?" | 無い | 直せない | なし |
| Good practices | "Does the project follow good open-source practices (license, documentation, tests and/or verification processes, releases, and clear contribution/support pathways)?" | そろう。ただし助けを求める道筋が書かれておらず、手を入れる文書は日本語だけだった | 直せる | `CONTRIBUTING.md` に「In English」を足した |
| Installation | "Does installation proceed as outlined in the documentation?" | README に入れ方が無かった。新しい仮想環境で `pip install ".[pdf]"` が通り、`errata-check --version` が `0.3.0` を返した | 直せる | README（日英）に「入れる」を足した |
| Functionality | "Have the functional claims of the software been confirmed?" | 道具自身の検査と見本が通る。JSON に直した見本の宣言は、Python 3.9 と 3.10 でも通った（手で確かめた。CI が回すのは 3.11・3.12・3.13） | 直すものが無い | なし |
| Performance | "If there are any performance claims of the software, have they been confirmed? (If there are no claims, please check off this item.)" | 速さを名乗る文は無い | 直すものが無い | なし |
| A statement of need | "Do the authors clearly state what problems the software is designed to solve and who the target audience is?" | README と `paper.md` にある | 直すものが無い | なし |
| Installation instructions | "Is there a clearly-stated list of dependencies? Ideally these should be handled with an automated package management solution." | `pyproject.toml` が依存を持つ。README は `pip install pypdf` だけを書いていた | 直せる | 「入れる」に依存と Python の版を書いた |
| Example usage | "Do the authors include examples of how to use the software (ideally to solve real-world analysis problems)." | `examples/` に見本がある。実際の使用は README の「使われている場所」 | 直すものが無い | なし |
| Functionality documentation | "Is the core functionality of the software documented to a satisfactory level (e.g., API method documentation)?" | README の「宣言の書き方」。並べた宣言の名を、検査が道具の `KNOWN_TABLES` と突き合わせる | 直すものが無い | なし |
| Automated tests | "Are there automated tests or manual steps described so that the functionality of the software can be verified?" | `tests/check_tool.py` を CI が回す | 直すものが無い | なし |
| Community guidelines | "Are there clear guidelines for third parties wishing to 1) Contribute to the software 2) Report issues or problems with the software 3) Seek support" | 1 と 2 は日本語であった。3 の場が書かれていなかった | 直せる | 使い方の質問も issue で受けると書いた。英語の節を足した |
| Summary | "Has a clear description of the high-level functionality and purpose of the software for a diverse, non-specialist audience been provided?" | ある | 直すものが無い | なし |
| Statement of need | "Does the paper have a section titled 'Statement of need' that clearly states what problems the software is designed to solve, who the target audience is, and its relation to other work?" | ある | 直すものが無い | なし |
| State of the field | "If related tools exist, do they provide a clear "build vs. contribute" justification explaining their unique scholarly contribution and why alternatives are insufficient?" | statcheck・GRIM・showyourwork・continuous analysis と比べていた。訂正と撤回の登録とは比べていなかった | 直せる | Crossref の更新の記録と Retraction Watch のデータとの比較を足した |
| Software design | "Is the content compelling and does it demonstrate meaningful design thinking?" | 取捨の段がある。名乗る数は、検査が見出しの段落と突き合わせる | 直すものが無い | なし |
| Research impact statement | "Is the evidence presented compelling?" | 著者自身のリポジトリでの使用と、そこで見つかった不備。外の利用は無いと書いてある | 直せない。外の利用は作れない | なし |
| AI usage disclosure | "Does the paper include an "AI usage disclosure" section that transparently discloses any use of generative AI in the software creation, documentation, or paper authoring?" | ある。人が確かめたという言明は、著者自身が署名するもの | 署名は Claude にはできない | 段の前に、著者自身の言明だと書いた注釈を置いた。検査が見る |
| Quality of writing | "Is the paper well written (i.e., it does not require editing for structure, language, or writing quality)?" | 決めるのは査読者 | 決めるのはこちらではない | なし |
| References | "Is the list of references complete, and is everything cited appropriately that should be cited (e.g., papers, datasets, software)? Do references in the text use the proper citation syntax?" | 引用は `[@鍵]` の形。pandoc の citeproc で全部解けた。訂正と撤回の登録を引いていなかった | 直せる | 項目を足した（下の「paper.bib で確かめたもの（2026年11月25日）」） |

論文の手引き（`docs/paper.md`）の決まりも当てました。

| 決まり | JOSS の文 | いまの状態 | 直したもの |
| --- | --- | --- | --- |
| 節と順 | "sections for Summary, Statement of need, State of the field, Software design, Research impact statement, AI usage disclosure, Acknowledgements, and References" | 求める節がこの順にある | 順も検査に足した |
| 語数 | "The paper should be between 750-1750 words." | 検査が数え、範囲に収まる | なし |
| 組めること | "JOSS uses Pandoc to compile papers from their Markdown form into a PDF." | 組む仕事が無かった | `.github/workflows/paper.yml` を足した（下の「論文の下書きを組む仕事」） |
| 日付 | "The date must be specified using the following format: `%e %B %Y`" | `23 November 2026`。下書きの日付 | なし。出す日にその日の日付にする |

### 関門 1 の日付

規程の文は次のとおりです。

> The repository must have been public for more than six months prior to submission, with active development spanning that period.

GitHub の API が返すリポジトリの作成の時刻は、2026-09-07T18:34:51Z です。最初のコミットの日も 2026-09-07 です。
作ったときから公開されていたなら、六か月を超えるのは 2027-03-07T18:34:51Z より後です。日付で数えて最初の日は 2027年3月8日です。
cpsbvbng26-dotcom の `docs/joss.md` の「門 1 に届く最短」の 2027-03-08 と合います。

公開に切り替えた日は、API からは読めません。リポジトリの出来事の一覧（Events API）が返すのは、2026-10-31 より後の出来事だけです。
上の「関門の数」は「公開は 2026年9月7日」と書いていました。作成日を公開日と読んでいたので、その文を直しました。
間接の目印はあります。Zenodo の `v0.1.0` の記録は、DataCite で 2026-09-07T18:56Z に作られ、`IsSupplementTo` に GitHub の `v0.1.0` の頁を持ちます。

出す時期の決めは、Sophaxis のコードと一緒に 2027年5月以降です（2026年11月11日の決め）。日付の点では、関門 1 はその前に満ちます。
関門 1 の「active development spanning that period」と関門 4 は、日付だけでは満ちません。

### 論文の下書きを組む仕事

論文の手引きは、組めることを確かめるやり方に、GitHub Action と Docker と手元を挙げます。
GitHub Action（`openjournals/openjournals-draft-action`）の中身は、`docker://openjournals/inara:latest` を走らせるだけです。
そのリポジトリの `master` は `af22ceb4b8f9eff6b3a13c05747ccc2f573cf2e6` でした（2026年11月25日、`git ls-remote`）。
アクションをこの値で留めても、`latest` が指す像は動きます。このリポジトリは外のものを動かない値で留めると決めています（`tests/check_hygiene.py` の「固定」）。
そこでアクションは使わず、同じ像を直に走らせる仕事を `.github/workflows/paper.yml` に置きました。
像は、Docker Hub の registry が `latest` と `1.3.1` の両方に返した digest（`sha256:a0414b8b72fd8923917ede614d340d98dc7aa3102aabc2e955e9c02a6100fd62`）で留めています。
`inara` の `v1.3.1` のタグの `Dockerfile` は、`paper.md` を読んで `paper.pdf` を書くと書いています。
`paper.md`・`paper.bib`・その仕事のファイルが変わるときだけ動き、できた PDF を実行の成果物に置きます。
この作業環境には Docker の常駐の仕組みが無く、手元では組めませんでした。手元では pandoc（citeproc）で本文を平文に組み、引いた鍵が全部解けることを確かめました。
法令の点検の記録の八度目の表にも、この仕事の行を足しました。
2026年11月25日に Claude が決めました。投稿先の組版で組めないことを、出す前に知るためです。

### paper.bib で確かめたもの（2026年11月25日）

| 鍵 | 確かめた先 | 結果 |
| --- | --- | --- |
| `nuijten2016` | `api.crossref.org` | 題・誌・巻・号・頁・著者が合う |
| `brown2017` | `api.crossref.org` | 題・誌・巻・号・頁・著者が合う |
| `beaulieujones2017` | `api.crossref.org` | 題・誌・巻・号・頁・著者が合う DOI の記録がある。外からの点検がその番号を挙げた。決めごと 1 は利用者から受け取った番号だけを書くと決めているので、DOI の欄には書かず、README と同じ頁の URL のままにした |
| `luger2022` | `api.crossref.org` の書誌の照会 | showyourwork そのものの DOI は見つからなかった。リポジトリの URL のまま |
| `crossrefapi` | `api.crossref.org` の撤回の記録 | 更新の記録が、更新された側の `update-to` の欄に入り、その出どころに `publisher` と `retraction-watch` がある |
| `rwdata` | `gitlab.com/crossref/retraction-watch-data` の README | 次の文がある。データは 2026-11-24 に作られたもの |

> In September 2023, Crossref acquired the Retraction Watch database from the Center of Scientific Integrity and have made it publicly available.

足した項目には DOI がありません。DOI の欄が DOI の形をしていることと、DOI が README にあることは、`tests/check_tool.py` が見ます。

### 確かめなかったもの

- 同僚が試したかどうか。記録が無く、こちらでは作れません。
- `Confirmation of review` の言明への署名。著者自身の言明で、Claude は代わって署名できません。
- 論文の PDF が JOSS の組版で組めるかどうか。手元では組めず、`.github/workflows/paper.yml` の実行が見ます。

## 審査は公開の場で行われる

JOSS の査読は `openjournals/joss-reviews` の issue として公開されます。
却下された場合も、そのやり取りは残ります。消せません。

2026年11月19日に、規程の側にもこの方針が書かれました（上の「2026年11月23日に読み直したもの」）。

それはこの記録の作法と食い違いません。通らなかったことも記録します。

## いつ出すか

2027年5月以降、Sophaxis のコードと一緒に出します（2026年11月11日の決め）。

2027年3月7日より後であることは、そのまま要ります。公開から六か月を数えた日です。ただし日付は必要条件であって
十分条件ではありません。期間だけ空けても、関門 4（時間をかけた反復）は埋まりません。

埋めるために、これからのやり方を変えます。

| | 2026年9月10日のやり方 | これから |
| --- | --- | --- |
| 直しかた | `main` へ直接 push | issue を立ててから pull request で閉じる。公開の記録が残る |
| 版 | 溜めてから上げる | 区切りごとにリリースを切る |
| 変更履歴 | 無い | `CHANGELOG` を置くか、リリースの本文で代える |

直接 push を続けていれば、半年後も「まとめて流し込んだ記録」にしかなりません。
規程が見ているのはコミットの分布であって、経過した日数ではありません。

この表を書いた日のうちに、pull request を使い始めました（#2）。
変更履歴は、その #2 で [`CHANGELOG.md`](CHANGELOG.md) として置きました。
2026年9月18日より後は、`main` へ直接 push した変更はありません。

## 結果をどこに書くか

- 受理されれば、識別子と日付をこの節に書きます。
- 却下されれば、却下されたことと、示された理由を書きます。
- 保留や差し戻しになれば、何を求められたかを書きます。

どの結果でも消しません。

## 言語モデルの関与

規程は、言語モデルの利用と**その検証方法**の、明確で具体的な開示を求めています。
曖昧な書き方は不可とされています。

- `paper.md` に `AI usage disclosure` の節があります。JOSS の規程が求める節の名前です。
- README の「言語モデルの利用」に、何を著者が決めたかを書いてあります。
- 検証方法そのものが、この道具の中身である —— 通る状態を壊して、落ちることまで確かめる試験。項目数と壊す先の数は README が名乗る。
- `paper.md` の開示は、使ったモデルを版まで名指しします。履歴の `Co-Authored-By` に出てくるモデルを全部名指ししているかを、`tests/check_tool.py` が見ます（2026年11月23日）。
- 審査の場（`openjournals/joss-reviews` の issue）のやり取りに、言語モデルは使えません。規程が例外にしているのは翻訳だけです（2026年11月23日に読み直して書き足した）。

> AI is not allowed for conversational interactions between authors and editors or reviewers unless it is being used for translation purposes.

開示は消しません。言語モデルを著作者にしません。
