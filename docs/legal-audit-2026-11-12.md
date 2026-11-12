# 法令の点検（2026-11-12）

この頁は、2026-11-12 に Claude が行った法令の点検のうち、errata-check の分の記録です。
対象は、README のライセンスの記載、JOSS に出す原稿（paper.md）、見本（examples/）です。
10 のリポジトリに掛かる免責事項の点検と、条文の取り寄せ方は、cpsbvbng26-dotcom の[点検の記録](https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/docs/legal-audit-2026-11-12.md)にあります。
この頁は運営者の立場を記録するもので、読む人への法的な助言ではありません。

## やり方

法令が出てくる箇所を一つずつ挙げ、挙げた条の文を、取り寄せた条文と照らしました。
条文は記憶から書いていません。
Sophaxis の取り寄せの仕事を走らせて e-Gov から取り寄せ、cpsbvbng26-dotcom の [verification/statutes.json](https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/verification/statutes.json) に写しました。
この頁が挙げる条がどれもその表にあることは、cpsbvbng26-dotcom の `check_ecosystem.js` が確かめます。
判定は、誤り・根拠不足・漏れ・表現・問題なしの五つです。

## 点検の表

| 箇所 | 法令と条 | 要件 | 事実 | 判定 | 対応 |
| --- | --- | --- | --- | --- | --- |
| README「ライセンス」、LICENSE、CITATION.cff、.zenodo.json、免責事項の「再利用」 | 著作権法第21条、著作権法第23条 | 複製と公衆送信は著作者の権利で、他人に許す範囲は許す者の表示で決まる | 全体が MIT で揃っている。paper.md もリポジトリの中では MIT | 問題なし | なし |
| 見本（examples/）の紙面と文献 | 著作権法第32条、著作権法第48条 | 公表された著作物を、公正な慣行に合致し、報道・批評・研究その他の引用の目的上正当な範囲内で引く。出所を明示する | 見本はどれも合成で、本物の論文を置かないと examples/README.md が書く。文献の欄は書誌だけ | 問題なし | なし |
| 道具が読むもの | 個人情報保護法第2条 | 特定の個人を識別できる情報 | 道具は使う人の手元のファイルを読み、外へ送らない | 問題なし | なし |

## 2026-11-12 の続き：リスクを締めた

同じ日に、利用者が「法的リスクをさらにシメて」と求めました。
上の表で根拠不足としたところと、取り寄せた文だけでは読みが決まらないところを、厳しいほうの読みで見直しました。
厳しいほうの読みでも成り立つ形があり、費用が掛からないときは、その形を採りました。
決めたことは、行ごとに理由と一緒に書きます。
取り寄せられなかった文に頼るところは、この節では扱っていません。

| 箇所 | 法令と条 | 要件 | 事実 | 判定 | 対応 |
| --- | --- | --- | --- | --- | --- |
| README の statcheck と GRIM の記述 | 刑法第230条、不正競争防止法第2条 | 名誉の毀損。競争関係にある他人の営業上の信用を害する虚偽の事実を告げ、又は流布すること | 二つの考え方を、文献の DOI を添えて説明する。違いは「目的が違う」と書き、どちらが良いとは書かない | 問題なし | なし |
| 見本（examples/）の紙面と文献 | 著作権法第21条、個人情報保護法第2条 | 他人の著作物の複製。特定の個人を識別できる情報 | 見本はどれも合成で、文献の欄は書誌だけ。実在の人の名を著者として置いていない | 問題なし | なし |
| README の責任の一文 | 民法第709条 | 故意又は過失で他人の権利又は法律上保護される利益を侵害した者は、生じた損害を賠償する | 「責任の範囲は、免責事項に定めています」と書いていた。免責事項は契約ではなく、責任の範囲は法令が決める。今日、免責事項は責任を免除する文をやめた | 表現 | 「責任は、法令の定めるとおりです。説明は免責事項にあります。」に直した。10 のリポジトリで同じ一文にそろえ、cpsbvbng26-dotcom の `check_ecosystem.js` が一字一句を見る。2026-11-12 に Claude が決めました。免責事項が範囲を決めると読める言い方は、どちらの読みでも成り立たないからです |

## 2026-11-12 の続き：取り寄せた周辺の文

上の表で取り寄せられなかった文のうち、同じ日に Sophaxis の取り寄せの仕事が取り寄せたものがあります。
置き場は Sophaxis の main（コミット 6b40d77、PR #218）の `verification/sources-raw.json` です。
取り寄せた文で、上の結論を一つずつ確かめ直しました。
条の文は cpsbvbng26-dotcom の `verification/statutes.json` に写し、`check_ecosystem.js` が Sophaxis の文と一字一句を突き合わせます。
規約は著作物なので、頼った句だけをこの表に引きます。

| 箇所 | 法令と条 | 要件 | 事実 | 判定 | 対応 |
| --- | --- | --- | --- | --- | --- |
| paper.md と JOSS | JOSS の方針 | JOSS の頁は、論文の著者が著作権を持ち続け、論文は CC BY 4.0 で公開されると書く（`papers retain copyright`） | paper.md はリポジトリの中で MIT。著作権は著者にある。著者は同じ文を、別のライセンスでも許すことができる | 問題なし | なし |

## 2026-11-12 の続き：二度目の見落とし

同じ日に、読むだけの点検を、さらに別の手でもう一度行いました。
上の節が見落としていたものが見つかりました。
前の行は、そのとき何を確かめたかの記録なので、消していません。
法令の文は、cpsbvbng26-dotcom の `verification/statutes.json` に写した取り寄せた文から引きます。
10 のリポジトリに同じものを置く文書の点検は、[cpsbvbng26-dotcom の記録](https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/docs/legal-audit-2026-11-12.md)の同じ見出しの節にもあります。

| 箇所 | 法令と条 | 要件 | 事実 | 判定 | 対応 |
| --- | --- | --- | --- | --- | --- |
| SECURITY.md | 民法第709条 | 取り寄せた文は「故意又は過失によって他人の権利又は法律上保護される利益を侵害した者は、これによって生じた損害を賠償する責任を負う」と定める。無い窓口を約して、頼った人に損を生じさせないこと | SECURITY.md は、安全の問題を GitHub の非公開の報告で受けると約していた。GitHub の API は、2026-11-12 に、このリポジトリの非公開の報告を `enabled: false` と返した。これはリポジトリの設定であり、Claude の持つ道具では変えられない | 誤り | 運営者の ORCID の記録にあるメールアドレスで受けると書き直し、GitHub の非公開の報告は有効になっていないと、確かめた日と一緒に書いた。写しは 10 のリポジトリと deposit-check で一字一句同じで、cpsbvbng26-dotcom の `check_ecosystem.js` の 12j が中身を確かめる。2026-11-12 に Claude が決めました。在る窓口は、免責事項がすでに使っている一つだけだからです |

## 2026-11-12 の続き：四度目の見落とし

同じ日に、読むだけの点検を、四度目に別の手で行いました。
上の節が見落としていたものが見つかりました。
前の行は、そのとき何を確かめたかの記録なので、消していません。
誤っていた前の行は、新しい行の中でそう書き、理由を添えます。
法令の文は、cpsbvbng26-dotcom の `verification/statutes.json` に写した取り寄せた文から引きます。
10 のリポジトリと deposit-check に同じ形で置く文の点検は、[cpsbvbng26-dotcom の記録](https://github.com/cpsbvbng26-dotcom/cpsbvbng26-dotcom/blob/main/docs/legal-audit-2026-11-12.md)の同じ見出しの節にもあります。

| 箇所 | 法令と条 | 要件 | 事実 | 判定 | 対応 |
| --- | --- | --- | --- | --- | --- |
| README「ライセンス」（日英） | 著作権法第21条 | 取り寄せた文は「著作者は、その著作物を複製する権利を専有する。」と定める（cpsbvbng26-dotcom の `verification/statutes.json`、SHA-256 `a85d04f2fd20d7867d5579bee40676b13405c58ea7fd7eb27f1e7a5a03bda100`）。許せるのは、許す者が権利を持つものだけである。ライセンスの文が、他人の文まで許すと読めないこと | README のライセンスの節は、リポジトリ全体の MIT だけを書き、引いた他人の文の扱いを書いていなかった。Sophaxis は、最初の見落としの節で同じ一文を足していたが、10 のリポジトリと deposit-check には届いていなかった。上の点検の表の「README「ライセンス」、LICENSE、CITATION.cff、.zenodo.json、免責事項の「再利用」」の行は問題なしとしていたが、他人の文の扱いを見ていなかった | 漏れ | README のライセンスの節に「このリポジトリが引き、または引用を確かめるために置いている他人の文は、CC BY 4.0 でも MIT でも許諾しておらず、それぞれの権利者のものです。」を足した。`check_ecosystem.js` の 12l が、10 のリポジトリと deposit-check の README（英語の README を含む）にこの一文があることを見る。2026-11-12 に Claude が決めました。Sophaxis の README と同じ範囲を、同じ形で書くためです |
| CITATION.cff の message と .zenodo.json の notes | 著作権法第21条 | 同上。引用情報の license の欄は、どの部分に掛かるかを書けないので、その範囲を別の欄で書くこと | CITATION.cff と .zenodo.json の license の欄は MIT で、notes は「The code is MIT.」とだけ書いていた。リポジトリは LICENSE 一つで、文書も MIT である（免責事項の「再利用」）。上の点検の表の「README「ライセンス」、LICENSE、CITATION.cff、.zenodo.json、免責事項の「再利用」」の行は問題なしとしていたが、欄の掛かる範囲と他人の文を見ていなかった | 表現 | message と notes に、コードも文書も含めてリポジトリ全体が MIT で、license の欄が全体に掛かることを書いた。他人の文は許諾していないとも、和英で書いた。`check_ecosystem.js` の 12l が、二つのファイルにこの文があり、置き方が目録の licenceLayout と同じことを見る。2026-11-12 に Claude が決めました。Sophaxis の CITATION.cff が三度目の見落としの節で書いた範囲の文に、10 のリポジトリと deposit-check を揃えるためです |

## 2026-11-12 の続き：八度目の見落とし

読むだけの点検を、八度目に別の手で行いました。
上の節が見落としていたものが見つかりました。
直した日は、日本時間で 2026-11-13 です。
前の行は、そのとき何を確かめたかの記録なので、消していません。
GitHub の利用規約の I 節は「Some Service features may be subject to additional terms specific to that feature or product as set forth in the GitHub Additional Product Terms.」と書きます。
その追加の規約（GitHub Terms for Additional Products and Features）を、これまでの点検は取り寄せていませんでした。
追加の規約は、`github/site-policy` のコミット `166eb97e485b7de3cd5dbaf8c8d16e4310fda46c` の文を、2026-11-13 に raw.githubusercontent.com から直に取り寄せました。
ファイルの SHA-256 は `c39b5a7fc1953ebd37428db18101726acefb55420f766bcd7d912e1b71ee2ffc` です。
Actions の節は「Additionally, regardless of whether an Action is using self-hosted runners, Actions should not be used for:」と書き、次の二つを挙げます。
一つは「Any activity that places a burden on our servers, where that burden is disproportionate to the benefits provided to users (for example, don't use Actions as a content delivery network or as part of a serverless application, but a low benefit Action could be ok if it’s also low burden); or」です。
もう一つは「If using GitHub-hosted runners, any other activity unrelated to the production, testing, deployment, or publication of the software project associated with the repository where GitHub Actions are used.」です。
同じ節は「Misuse of GitHub Actions may result in termination of jobs, restrictions in your ability to use GitHub Actions, disabling of repositories created to run Actions in a way that violates these Terms, or in some cases, suspension or termination of your GitHub account.」とも書きます。
このリポジトリのワークフローは、どれも GitHub の実行環境（`ubuntu-latest` か `ubuntu-24.04`）で動きます。
そこで、ワークフローを一つずつ、四つの目的（制作・検査・配備・公開）のどれに当たるか、負荷が益に見合うかで読みました。
ワークフローの行は、箇所の欄を `.github/workflows/` のファイルの名で始めます。
実行の時間は、GitHub の API で 2026-11-13 に読んだ直近の実行（多くて 300 件）の中央値です。
GitHub Pages が枝から頁を配るときに GitHub が動かす仕事と、Dependabot の版の更新は、このリポジトリのファイルではないので、表に挙げていません。
引いた文は、cpsbvbng26-dotcom の `verification/statutes.json` の「GitHub の利用規約 I」と「GitHub の追加製品の規約 Actions」に写しました。
同じ点検は、13 のリポジトリの記録の同じ見出しの節にあります。

| 箇所 | 法令と条 | 要件 | 事実 | 判定 | 対応 |
| --- | --- | --- | --- | --- | --- |
| GitHub の追加製品の規約（Actions の節） | GitHub の利用規約 I、GitHub の追加製品の規約 Actions | 使っているサービスの規約を取り寄せて読むこと | 利用規約の I 節は追加の規約を取り込みますが、これまでの点検は追加の規約を読んでいませんでした | 漏れ | 取り寄せ、Actions の節の文を cpsbvbng26-dotcom の `verification/statutes.json` に写しました。Sophaxis と Nusquama の見張りにも足しました。2026-11-13 に Claude が決めました。ワークフローの使い方を決める文なので、ほかの規約と同じに読むためです |
| `.github/workflows/hygiene.yml`（main への push・PR、毎週水曜の 13:53、手で起こすとき） | GitHub の追加製品の規約 Actions | GitHub の実行環境で、リポジトリのソフトウェアのプロジェクトの制作・検査・配備・公開のどれかに当たること。負荷が利用者への益に見合うこと | 依存・権限・固定・秘密の走査（`tests/check_hygiene.py`）を回します。週に一度の実行は、変更の無い日にも混入を見るためです。実行の中央値は 9 秒です | 問題なし | 変えていません。検査に当たり、負荷は週に一度の数秒です |
| `.github/workflows/pypi.yml`（Release を公開したとき、手で起こすとき） | GitHub の追加製品の規約 Actions | GitHub の実行環境で、リポジトリのソフトウェアのプロジェクトの制作・検査・配備・公開のどれかに当たること。負荷が利用者への益に見合うこと | タグから組んで PyPI に出します。直近の実行の記録はありません | 問題なし | 変えていません。道具の公開に当たります |
| `.github/workflows/swh-save.yml`（手で起こすとき） | GitHub の追加製品の規約 Actions | GitHub の実行環境で、リポジトリのソフトウェアのプロジェクトの制作・検査・配備・公開のどれかに当たること。負荷が利用者への益に見合うこと | Software Heritage に保存を頼み、版の中身が入ったことを確かめます。`repo` を渡すと、同じ持ち主の別のリポジトリも頼めました。実行は 2026-09-29 の 2 回で、どちらも 11〜13 秒でした。researcher-profile の README は、その日にこの仕事で researcher-profile の保存を確かめたと書いています。errata-check の外のプロジェクトのための使い方でした | 漏れ | `repo` の入力を外し、このリポジトリだけを頼むようにしました。cpsbvbng26-dotcom の続けられなくなったときの頁も直しました。2026-09-29 の保存の記録は、そのまま残します。2026-11-13 に Claude が決めました。このリポジトリの道具を保存することは公開に当たりますが、ほかのリポジトリを頼むことは、このリポジトリのプロジェクトに関わらないためです |
| `.github/workflows/verify.yml`（main への push・PR、手で起こすとき） | GitHub の追加製品の規約 Actions | GitHub の実行環境で、リポジトリのソフトウェアのプロジェクトの制作・検査・配備・公開のどれかに当たること。負荷が利用者への益に見合うこと | このリポジトリの検査を回します（道具自身の検査、見本の監査）。実行の中央値は 17 秒です | 問題なし | 変えていません。検査に当たります |
| 検査（`tests/check_hygiene.py`） | なし | ワークフローごとの判断を、機械で固めること | ありませんでした | 漏れ | `tests/check_hygiene.py` に 7 番を足し、`.github/workflows/` のどのファイルもこの節の表に行を持ち、無いファイルの行が無いことを確かめます。cpsbvbng26-dotcom の `check_ecosystem.js` の 12o も、13 のリポジトリについて同じことを確かめます。2026-11-13 に Claude が決めました。新しいワークフローを、規約に照らさずに足せないようにするためです |

この表の判定は、漏れ 3、問題なし 3 です。

弁護士は、この節を見ていません。

## 調べた法令

- GitHub の利用規約（I 節）と GitHub の追加製品の規約（Actions の節。2026-11-13 に `github/site-policy` から直に取り寄せた）
- 著作権法（第21条、第23条、第32条、第48条）
- 個人情報保護法（第2条）
- 刑法（第230条）、不正競争防止法（第2条）
- 民法（第709条）
- JOSS の方針と論文の頁

## 取り寄せられなかった文

- この記録が頼る文で、取り寄せられなかったものは残っていません。

## 弁護士について

この点検は Claude が行いました。
弁護士は、この点検を見ていません。
