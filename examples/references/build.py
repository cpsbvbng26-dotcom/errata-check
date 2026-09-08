#!/usr/bin/env python3
"""参考文献の使い方の見本を作り直す。

    python3 examples/references/build.py

原稿を一つ置く。**合成である。**本物の論考を使うと、通ったのが道具のおかげ
なのか原稿のおかげなのかが分からなくなる。

「読んだ」は内面であり、外から確かめられない。**「どの箇所が、どの主張を
支えているか」は公開された主張**であって、本を持っている人なら誰でも
反証できる。だから宣言させるのは読書ではなく、指し示しのほうである。
"""

import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)

from errata_check import digest     # noqa: E402

ESSAY = """# 自己立法についての覚書

自己を統べるという発想を、三つの源から組み立てる。

第一に、自己が自らの法の作り手であると同時に、その法に従う者でもあるという
二重の位置である。定言命法をめぐる議論はこの構造を明示している
(Kant 1785)。ここで用いるのは法の形式の側だけであり、義務の内容論には
立ち入らない。

第二に、価値の再創造である。「力への意志」という語そのものは、著者の公刊した
著作ではなく編纂物に由来する (Nietzsche 1967)。**この語を使う以上、その編纂の
経緯を無視できない。**

第三に、動員という語の来歴である (Junger 1932)。国家の総動員を論じた文脈から
自己の陶冶へ語を移すには、明示的な翻案が要る。

対立する見方も置いておく。自己の統治という比喩そのものを、支配の語彙の再生産
として退ける立場がある (Foucault 1988)。

## 参考文献

- Foucault, M. (1988). Technologies of the Self.
- Junger, E. (1932). Der Arbeiter.
- Kant, I. (1785). Grundlegung zur Metaphysik der Sitten.
- Nietzsche, F. (1967). The Will to Power. Kaufmann & Hollingdale, trans.
"""

path = os.path.join(HERE, "essay.md")
io.open(path, "w", encoding="utf-8", newline="\n").write(ESSAY)
print("書きました: %s" % os.path.relpath(path, ROOT))
print("  sha256 = %s" % digest(path))
