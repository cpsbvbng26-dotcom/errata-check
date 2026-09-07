#!/usr/bin/env python3
"""検査用の PDF を、依存なしで書き出す。

    python3 tests/make_pdf.py out.pdf "一行目" "二行目" ...

本物の論文を使うと、検査が通ったのが道具のおかげなのか、その PDF のおかげなのかが
分からない。**中身が既知の PDF を自分で作る。**

最小限の構造だけ書く。1 ページ、Helvetica、圧縮なし、暗号化なし。
"""

import sys


def escape(s):
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def make(lines, width=612, height=792, size=11, leading=16):
    """行の並びから PDF のバイト列を作る。ASCII のみ。"""
    y = height - 72
    parts = ["BT", "/F1 %d Tf" % size, "%d %d Td" % (72, y), "%d TL" % leading]
    for i, line in enumerate(lines):
        parts.append("(%s) Tj" % escape(line))
        if i != len(lines) - 1:
            parts.append("T*")
    parts.append("ET")
    stream = "\n".join(parts).encode("ascii")

    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        ("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d] "
         "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
         % (width, height)).encode("ascii"),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body + b"\nendobj\n"
    start = len(out)
    out += b"xref\n0 %d\n" % (len(objs) + 1)
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += (b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
            % (len(objs) + 1, start))
    return bytes(out)


if __name__ == "__main__":
    path, lines = sys.argv[1], sys.argv[2:]
    with open(path, "wb") as fh:
        fh.write(make(lines))
    print("書き出しました: %s（%d 行）" % (path, len(lines)))
