#!/usr/bin/env python3
"""凍結された公開物に対して、正誤表のほうを機械で監査する。

    python3 errata_check.py audit.toml

DOI が付いて公開された PDF は、もう直せない。直せるのは**正誤表のほう**である。
だから正誤表は、時間とともに一次資料からずれていく。引用が一字変わる。数え落とす。
「解決しました」と書き換わる。最終更新の日付が古いまま残る。

これは、そのずれを CI で落とすための道具である。

    引用      正誤表が「印字されている」と述べた文が、本当にその PDF にあるか
              逆に「印字されていない」と述べたものが、本当に無いか
    完全性    宣言した件数だけ引用が挙がっているか（数え落としを止める）
    不在      「同梱されている」と謳われたファイルが、本当に無いか
    数値      正誤表が名乗る件数が、実際にコマンドを走らせた結果と一致するか
    未解決    解決しないと決めた項目が、こっそり解決済みに書き換わっていないか
    凍結      一次資料そのものが差し替わっていないか（SHA-256）
    日付      最終更新が、本文に書かれたどの日付よりも古くないか

**判定に推論を使わない。**あるか、無いか、一致するか、しないか。LLM も類似度も
使わない。だから出力を人が確かめ直す必要が無い。

PDF を読むときだけ pypdf が要る。平文（.txt / .md）だけを見るなら依存は無い。

    pip install pypdf

MIT License。© 2026 Takuya Nemoto
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import unicodedata

__version__ = "0.1.0"
__all__ = ["Audit", "Result", "load", "run", "normalize", "extract_text"]

# ------------------------------------------------------------------ 文字の正規化

_ZERO = dict.fromkeys(map(ord, "­​‌‍﻿"), None)


def normalize(text):
    """比較の前に、取り出し方の違いで生じる差を潰す。

    PDF から取り出した文字列は、改行や空白の入り方が処理系で変わる。合字や
    幅の違う空白も混ざる。**意味を変えない差だけ**を潰す。
    文字そのものは変えない（NFKC はかけるが、置換表は持たない）。
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_ZERO)
    return re.sub(r"\s+", " ", text).strip()


def extract_text(path):
    """一次資料から文字を取り出す。PDF なら pypdf、それ以外は素直に読む。"""
    if path.lower().endswith(".pdf"):
        # 暗号化されていない PDF に暗号処理は要らない。環境によっては
        # cryptography の読み込みが壊れるので、先に塞いでから読む。
        sys.modules.setdefault("cryptography", None)
        try:
            from pypdf import PdfReader
        except ImportError:
            raise SystemExit(
                "PDF を読むには pypdf が要ります:  pip install pypdf")
        return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def digest(path):
    """SHA-256。凍結されているはずのものが差し替わっていないかを見るため。"""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------ 宣言の読み込み

def load(path):
    """監査の宣言を読む。.toml（Python 3.11 以降）と .json に対応。"""
    if path.lower().endswith(".json"):
        with io.open(path, encoding="utf-8") as fh:
            return json.load(fh)
    try:
        import tomllib
    except ImportError:
        raise SystemExit("TOML には Python 3.11 以降が要ります。"
                         ".json で書くこともできます。")
    with open(path, "rb") as fh:
        return tomllib.load(fh)


# ------------------------------------------------------------------ 結果

class Result:
    """検査 1 件の結果。通ったかどうかと、外から見て分かる理由を持つ。"""

    def __init__(self, group, label, ok, detail=""):
        self.group = group
        self.label = label
        self.ok = bool(ok)
        self.detail = detail

    def line(self):
        return "  %s  %s%s" % ("PASS" if self.ok else "FAIL", self.label,
                               ("  " + self.detail) if self.detail else "")

    def as_dict(self):
        return {"group": self.group, "label": self.label,
                "ok": self.ok, "detail": self.detail}


# ------------------------------------------------------------------ 監査

class Audit:
    """宣言どおりに検査を走らせる。

    root       宣言ファイルからの相対パスの基準。既定は宣言ファイルの置き場所
    spec       load() が返した辞書
    """

    def __init__(self, spec, root="."):
        self.spec = spec
        self.root = root
        self.results = []
        self._text = {}
        self._document = None

    # -------------------------------------------------------------- 補助
    def _path(self, rel):
        return os.path.join(self.root, rel)

    def _add(self, group, label, ok, detail=""):
        self.results.append(Result(group, label, ok, detail))
        return ok

    def _source(self, sid):
        for s in self.spec.get("source", []):
            if s.get("id") == sid:
                return s
        return None

    def _source_text(self, sid):
        if sid not in self._text:
            s = self._source(sid)
            if s is None:
                return None
            self._text[sid] = normalize(extract_text(self._path(s["path"])))
        return self._text[sid]

    def document_text(self):
        """正誤表そのもの。宣言に document が無ければ None。"""
        if self._document is None:
            doc = self.spec.get("document")
            if not doc:
                return None
            with io.open(self._path(doc["path"]), encoding="utf-8") as fh:
                self._document = fh.read()
        return self._document

    # -------------------------------------------------------- 一次資料
    def check_sources(self):
        srcs = self.spec.get("source", [])
        self._add("凍結", "一次資料が宣言されている", bool(srcs),
                  "%d 件" % len(srcs))
        for s in srcs:
            path = self._path(s["path"])
            if not self._add("凍結", "%s が読める" % s["path"],
                             os.path.isfile(path)):
                continue
            got = digest(path)
            want = s.get("sha256")
            if not want:
                # 宣言が無いことを「通った」と数えない。書き足せるように値は出す。
                self._add("凍結", "%s の sha256 が宣言されている" % s["id"],
                          False, "いまの値: " + got)
            else:
                self._add("凍結", "%s が差し替わっていない" % s["id"],
                          got == want,
                          "宣言 %s… / 実際 %s…" % (want[:16], got[:16]))

    # ------------------------------------------------------------ 引用
    def check_quotes(self):
        quotes = self.spec.get("quote", [])
        doc = self.document_text()
        doc_flat = normalize(doc) if doc is not None else None
        tally = {}
        for q in quotes:
            sid = q["source"]
            if q.get("present", True):
                key = (sid, q.get("group"))
                tally[key] = tally.get(key, 0) + 1
            text = self._source_text(sid)
            where = q.get("where", "")
            head = normalize(q["text"])
            present = q.get("present", True)
            label = "%s%s の記述が一次資料に%s" % (
                sid, ("（%s）" % where) if where else "",
                "ある" if present else "無い")
            if text is None:
                self._add("引用", label, False, "一次資料 %s が宣言に無い" % sid)
                continue
            self._add("引用", label, (head in text) == present, head[:56] + "…")
            if not present:
                # 「印字されていないこと」は正誤表の側にはあってよい。数えない。
                continue
            if q.get("in_document", True) and doc_flat is not None:
                self._add("引用", "同じ引用が正誤表にもある", head in doc_flat,
                          head[:56] + "…")
        # 数え落としを落とす。「三箇所だと思っていたら六箇所だった」を止めるため。
        for c in self.spec.get("count", []):
            sid, group, want = c["source"], c.get("group"), c["expect"]
            got = (tally.get((sid, group), 0) if group is not None
                   else sum(v for (s_, _g), v in tally.items() if s_ == sid))
            name = "%s%s" % (sid, ("・%s" % group) if group else "")
            self._add("引用", "%s の記述が %d 箇所宣言されている" % (name, want),
                      got == want, "宣言 %d / 実際 %d" % (want, got))

    # ------------------------------------------------------------ 不在
    def check_absent(self):
        for a in self.spec.get("absent", []):
            pattern = os.path.join(self.root, a["glob"])
            hits = [os.path.relpath(p, self.root)
                    for p in glob.glob(pattern, recursive=True)]
            self._add("不在", "%s が存在しない" % a["glob"], not hits,
                      (a.get("reason", "") + ("  見つかった: " + ", ".join(hits[:3])
                                              if hits else "")).strip())

    # ------------------------------------------------------------ 数値
    def check_numbers(self):
        doc = self.document_text()
        for nspec in self.spec.get("number", []):
            label = nspec.get("label", nspec.get("pattern", "数値"))
            out = subprocess.run(nspec["command"], shell=True, cwd=self.root,
                                 capture_output=True, text=True)
            m = re.search(nspec["extract"], out.stdout)
            if not m:
                self._add("数値", "%s をコマンドの出力から取れる" % label, False,
                          "出力の末尾: " + out.stdout.strip()[-80:])
                continue
            actual = m.group(1)
            self._add("数値", "%s をコマンドの出力から取れる" % label, True,
                      actual)
            targets = nspec.get("in", [])
            if isinstance(targets, str):
                targets = [targets]
            if not targets and doc is not None:
                targets = [self.spec["document"]["path"]]
            for rel in targets:
                with io.open(self._path(rel), encoding="utf-8") as fh:
                    body = fh.read()
                found = re.findall(nspec["pattern"], body)
                self._add("数値", "%s に書かれた %s が実際と一致する" % (rel, label),
                          bool(found) and all(v == actual for v in found),
                          "文書 %s / 実際 %s" % (", ".join(sorted(set(found))) or "なし",
                                                actual))

    # -------------------------------------------------------- 未解決の項目
    def check_open_items(self):
        doc = self.document_text()
        if doc is None:
            return
        for item in self.spec.get("open_item", []):
            iid = item.get("id", "項目")
            hp = item.get("heading_pattern")
            if hp:
                self._add("未解決", "%s の見出しがある" % iid,
                          re.search(hp, doc, re.M) is not None, hp)
            for phrase in item.get("must_say", []):
                self._add("未解決", "%s が「%s」を保っている" % (iid, phrase[:24]),
                          phrase in doc)
            for phrase in item.get("must_not_say", []):
                self._add("未解決", "%s が「%s」と言っていない" % (iid, phrase[:24]),
                          phrase not in doc)

    # ------------------------------------------------------------ 日付
    def check_dates(self):
        doc = self.document_text()
        spec = self.spec.get("dates")
        if doc is None or not spec:
            return
        stamp_pat = spec["stamp_pattern"]
        any_pat = spec.get("any_pattern", stamp_pat)
        m = re.search(stamp_pat, doc)
        if not self._add("日付", "最終更新の日付が書いてある", m is not None,
                         stamp_pat):
            return
        def key(match):
            return tuple(int(g) for g in match)
        stamp = key(m.groups())
        inner = [key(g) for g in re.findall(any_pat, doc)]
        newest = max(inner) if inner else stamp
        self._add("日付", "最終更新が本文のどの日付よりも古くない", stamp >= newest,
                  "最終更新 %s / 本文の最新 %s" % (stamp, newest))

    # ------------------------------------------------------------ 実行
    def run(self):
        self.check_sources()
        self.check_quotes()
        self.check_absent()
        self.check_numbers()
        self.check_open_items()
        self.check_dates()
        return self.results


def run(spec_path, quiet=False, as_json=False):
    """宣言を読んで走らせ、(通った件数, 落ちた結果) を返す。"""
    spec = load(spec_path)
    root = spec.get("root") or os.path.dirname(os.path.abspath(spec_path)) or "."
    if not os.path.isabs(root):
        root = os.path.join(os.path.dirname(os.path.abspath(spec_path)), root)
    audit = Audit(spec, root=os.path.normpath(root))
    results = audit.run()
    if as_json:
        print(json.dumps({"version": __version__,
                          "passed": sum(r.ok for r in results),
                          "failed": sum(not r.ok for r in results),
                          "results": [r.as_dict() for r in results]},
                         ensure_ascii=False, indent=1))
    elif not quiet:
        group = None
        for r in results:
            if r.group != group:
                group = r.group
                print("\n" + group)
            print(r.line())
    return sum(r.ok for r in results), [r for r in results if not r.ok]


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="errata-check",
        description="凍結された公開物に対して、正誤表のほうを機械で監査する。")
    ap.add_argument("spec", help="監査の宣言（.toml または .json）")
    ap.add_argument("--json", action="store_true", dest="as_json",
                    help="結果を JSON で出す")
    ap.add_argument("--quiet", action="store_true", help="要約だけ出す")
    ap.add_argument("--version", action="version", version=__version__)
    args = ap.parse_args(argv)

    passed, failed = run(args.spec, quiet=args.quiet, as_json=args.as_json)
    if not args.as_json:
        print("\n" + "-" * 58)
        if failed:
            print("%d 件が通り、%d 件が通りませんでした。" % (passed, len(failed)))
            for r in failed:
                print("  - " + r.label + (("  " + r.detail) if r.detail else ""))
        else:
            print("%d 件すべて通りました。" % passed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
