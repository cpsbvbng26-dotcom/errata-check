# errata-check

[![Checks](https://github.com/cpsbvbng26-dotcom/errata-check/actions/workflows/verify.yml/badge.svg)](https://github.com/cpsbvbng26-dotcom/errata-check/actions/workflows/verify.yml)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22685687.svg)](https://doi.org/10.5281/zenodo.22685687)

**English** ｜ [日本語](README.md)

Machine auditing of an errata document against a frozen, already-published artifact.

Once a PDF has been published with a DOI, it can no longer be revised. Only the errata can. That is why the errata drifts away from the primary source over time:

- a quotation changes by one character
- occurrences are undercounted
- an item quietly becomes "resolved"
- the "last updated" date stays stale

errata-check is a tool for failing that drift in CI.

```
pip install pypdf
python3 errata_check.py audit.toml
```

No inference is used in the judgement. Something is there or it is not; it matches or it does not. No language model and no similarity score is involved, so nobody has to re-check the output by hand.

---

## What it checks

| | What it checks |
| --- | --- |
| **Quotation** | Whether a sentence the errata says is printed really appears in the PDF, and whether one it says is not printed really does not |
| **Completeness** | Whether as many occurrences are listed as were declared (**it stops undercounting**) |
| **Absence** | Whether a file claimed to be "distributed with" the artifact is really missing |
| **Number** | Whether a count the errata states matches the result of actually running a command |
| **Open item** | Whether an item declared unresolvable has been quietly rewritten as resolved |
| **Freeze** | Whether the primary source itself has been swapped (SHA-256) |
| **Dates** | Whether the "last updated" date is not older than any date written in the body |

The most effective are completeness and open items. The others catch slips of the pen. These two catch an author revising things in their own favour.

### What can be checked deterministically from the printed page, by discipline

Matching quotations is not the only check. Different disciplines have different things that can be verified mechanically from the printed page.

| | What it checks | Where it applies |
| --- | --- | --- |
| **Statistic** | Recompute `p` from the printed test statistic and degrees of freedom, and compare with the printed `p` (`t` / `F` / `χ²` / `r`) | Empirical fields: psychology, medicine, economics |
| **GRIM** | Whether a mean of integers is actually reachable with that sample size | Same |
| **Identifier** | Check digits of ORCID, ISBN and ISSN | All fields |
| **Arithmetic** | Relations between printed numbers (randomised = analysed + lost, and so on) | Clinical trials, experiments |
| **Era** | Whether a Japanese era year corresponds to the Gregorian year | History, document studies |
| **Reference** | **Which locus of a cited source supports which claim.** Undeclared citations and unused references also fail | Humanities, all fields |
| **Body-only name** | A name mentioned in the body but **missing from the reference list**. Mentions that do not take the form of a dated citation slip through the net above | Same |

```toml
[[statistic]]
source = "paper"
text = "t(28) = 2.14, p = .04"
test = "t"
df = [28]
value = 2.14
reported = "p = .04"        # as printed; precision and inequality are read from here

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
label = "randomised 120 = analysed 112 + lost 8"
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

You can also declare that something is wrong. With `consistent = false`, the check asserts that the recomputed `p` **does not** match the printed one. This field exists so that, when the errata says "this passage is wrong", the claim itself can be pinned down mechanically.

```
python3 errata_check.py examples/disciplines/audit.toml    # 32 checks
```

### References: no declaration of "having read"

An inner state cannot be verified from outside. A declaration that something was "read" is testimony, not a check.

"Which locus supports which claim" is different. It is a public claim, and anyone who owns the book can refute it. So what is declared is not reading but pointing.

```toml
[[reference]]
key      = "Nietzsche 1967"
edition  = "The Will to Power, Kaufmann & Hollingdale trans., Vintage, 1967"
locus    = "§1067"
role     = "用語の出所"
supports = "Origin of the term 'will to power'. It does not support the claim itself"
caveat   = "A posthumous compilation; not the order the author published"
```

`role` is limited to five values. A vague "for reference" is not allowed.

| | |
| --- | --- |
| `直接支持` (direct support) | The source states the claim |
| `用語の出所` (origin of the term) | The origin of a word or concept, not support for a claim |
| `対立見解` (opposing view) | Cited as an opposing position |
| `背景` (background) | For context; it does not support the claim |
| `反例` (counterexample) | Cited as evidence against one's own position |

The body text is checked as well.

```toml
[reference_policy]
pattern      = "\\(([^()]{2,60}?\\s\\d{4}[a-z]?)\\)"
require_all  = true      # every citation in the body is declared
require_used = true      # every declared reference is used
```

`require_used` is the one that bites. Padding a reference list with works that the text never uses becomes structurally impossible.

This check does not see whether the book really says what is claimed. It cannot see that, and it does not pretend to. All it can verify is the consistency between the declaration and the printed page.

An example is in [`examples/references/`](examples/references/) (24 checks).

### Where the statistic and GRIM checks come from

Both are existing ideas, not new statistical methods.

- **Recomputing tests**: the same idea as [statcheck](https://doi.org/10.3758/s13428-015-0664-2) (Nuijten et al. 2016)
- **GRIM**: the same idea as the GRIM test of [Brown and Heathers](https://doi.org/10.1177/1948550616673876) (2017)

The implementation is independent; neither codebase was consulted. There is one difference. statcheck **extracts** statistics from papers automatically. This tool looks **only at what is declared**. It produces no false positives from extraction errors, and in exchange it does not look at passages nobody declared. Neither is better; the purposes differ. This tool is not about coverage but about pinning down **whether what the errata says is true**.

### The distributions are implemented in-house

`p` is computed without scipy, so that the tool can be distributed as a single file. The regularised incomplete beta and gamma functions are written with Lentz's continued fraction and series.

An implementation cannot vouch for itself. It is checked against **11 points** of the 5% and 1% critical values in published statistical tables (Section 3 of `tests/check_tool.py`).

## Writing a declaration

```toml
[document]
path = "ERRATA.md"

[[source]]
id = "paper"
path = "paper.pdf"
sha256 = "9e0f27cb…"       # without it, the check fails as "not declared"

[[count]]
source = "paper"
group = "promise"
expect = 2                  # declares that this kind of statement occurs twice

[[quote]]
source = "paper"
group = "promise"
where = "acknowledgements"
text = "the verification script is distributed together with this PDF"

[[quote]]                   # declares that something is NOT printed
source = "paper"
where = "DOI of the revised version"
text = "10.5281/zenodo.00000002"
present = false

[[absent]]
glob = "**/demo_verification.py"
reason = "claimed to be distributed with the paper, but does not exist"

[[number]]
label = "number of checks"
command = "python3 count.py"
extract = "(\\d+) checks"    # how to read the number from the command output
pattern = "(\\d+) 項目の検査" # how it is written in the document

[[open_item]]
id = "E1"
heading_pattern = "^## E1 —"
must_say = ["この項目は解決しません"]
must_not_say = ["解決済み", "修正しました"]

[dates]
stamp_pattern = "最終更新: (\\d{4})年(\\d{1,2})月(\\d{1,2})日"
any_pattern = "(\\d{4})年(\\d{1,2})月(\\d{1,2})日"
```

Declarations can also be written in `.json`. TOML requires Python 3.11 or later (`tomllib`).

### The declaration format is fixed

From 0.4.0, the names of the tables and keys allowed at the top level of a declaration are fixed. These are the following 17 names:

```
root  source  document  quote  count  absent  number  statistic  grim
identifier  arithmetic  era  reference  reference_policy  body_only
open_item  dates
```

Any other name fails the "declaration" group of checks. Previously, unknown names were silently ignored: misspell `[[quote]]` as `[[qoute]]`, and everything passed without a single quotation being checked. The tool was producing, at its own entrance, exactly the silent drift it exists to catch.

The keys allowed inside each table are fixed in the same way, and unknown keys fail. The list is `KNOWN_FIELDS` in `errata_check.py`. Misspelling `present = false` as `presnt = false` would otherwise turn a declaration of absence into a declaration of presence.

If a name ever has to change, the old name will remain accepted while the version is bumped, and the migration steps will be written here (the backward-compatibility policy in `CONTRIBUTING.md`).

A working example is in [`examples/minimal/`](examples/minimal/).

```
python3 errata_check.py examples/minimal/audit.toml     # 20 checks
```

## Whitespace

Text extracted from a PDF varies in its line breaks and spacing from one extractor to another. Before comparison, `NFKC` is applied, zero-width characters are dropped, and runs of whitespace are collapsed to one. Characters themselves are never replaced. So "a quotation differs by one character" fails, while "a line was wrapped" does not.

## The tool's own checks

```
python3 tests/check_tool.py     # 82 checks
```

A checking tool cannot be trusted because it passes. It would pass everything even if it looked at nothing. So the tests first build a passing state and then **break it one thing at a time, confirming that exactly the broken thing fails**. If it does not fail, that check is looking at nothing.

The tests break it in 30 distinct ways: changing one character of a quotation, declaring a missing quotation as present, placing a supposedly absent statement in the primary source, misstating a count, swapping the PDF, deleting the `sha256` declaration, misspelling a declaration table name, misspelling an item key, placing a supposedly absent file, shifting a stated count, shifting the command's result, deleting "will not be resolved", rewriting it as "resolved", deleting a heading, making a date stale, misstating a printed `p`, misstating degrees of freedom, declaring an unreachable mean as reachable, changing one digit of an ORCID, changing one digit of an ISBN, breaking the sum of a breakdown, changing an era correspondence, rewriting a plain-text primary source, deleting a reference locus, omitting what a reference supports, using an undefined role, forgetting to declare a citation, declaring an unused reference, removing a body-only name from the body, and placing that name in the reference list. Finally, it checks that **no false positives occur** (a wrapped line does not fail).

The PDFs used in the tests are written without dependencies by [`tests/make_pdf.py`](tests/make_pdf.py). With a real paper, one could not tell whether a pass was due to the tool or to that PDF.

---

## What this is not

To avoid confusion with existing tools:

| Existing | What it does | How this tool differs |
| --- | --- | --- |
| [showyourwork](https://github.com/showyourwork/showyourwork) | Rebuilds the paper PDF in CI and keeps figures and numbers in sync with code | Assumes the manuscript can be rebuilt. Not usable on a frozen PDF |
| [continuous analysis](https://www.nature.com/articles/nbt.3780) | Re-runs the analysis pipeline in CI | Same. Not a post-publication audit |
| [citecheck](https://arxiv.org/html/2603.17339) | Queries Crossref and others to repair references automatically | References only. Does not look at quotations in the body |
| [ATIBA](https://arxiv.org/html/2609.04123) | Judges the consistency between citation context and cited source with a language model | Probabilistic. Returns "uncertain" |
| A journal corrigendum | Publishes the correction as a separate article | Prose. No machine check |

This tool does not judge whether the errata is right. It only checks whether the errata contradicts the primary source. What counts as a correction is for people to decide.

## Limitations

- It depends on the text extracted from the PDF. If the extractor (pypdf) changes, results can change. Passages using ligatures or unusual glyphs may fail to match
- If the primary source is an image-only PDF, nothing can be extracted. There is no OCR
- It does not look at meaning. It checks that a quotation is in the original. It does not check whether the quotation was cut in a way that distorts its context
- It is not exhaustive. It looks only at declared passages, not at passages left undeclared
- Recomputing tests only checks that the printed values are internally consistent. It does not check whether the test was appropriate or its assumptions were met
- `[[number]]` runs arbitrary commands. Run only declarations you trust

## Citation

The tool is archived on Zenodo with a DOI. Each version has its own DOI; cite the version you used.

| Version | DOI |
| --- | --- |
| v0.3.0 (current) | [10.5281/zenodo.22685687](https://doi.org/10.5281/zenodo.22685687) |
| v0.2.0 | [10.5281/zenodo.22649899](https://doi.org/10.5281/zenodo.22649899) |
| v0.1.0 | [10.5281/zenodo.22649054](https://doi.org/10.5281/zenodo.22649054) |

> Nemoto, T. (2026). *errata-check: Deterministic auditing of errata against frozen
> published artifacts* (v0.3.0). Zenodo. https://doi.org/10.5281/zenodo.22685687

```bibtex
@software{nemoto_errata_check_2026,
  author       = {Nemoto, Takuya},
  title        = {{errata-check: Deterministic auditing of errata
                   against frozen published artifacts}},
  year         = {2026},
  version      = {v0.3.0},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.22685687},
  url          = {https://doi.org/10.5281/zenodo.22685687}
}
```

The v0.3.0 source is also preserved at [Software Heritage](https://archive.softwareheritage.org/swh:1:dir:3bfac898ac86e7f20a5a2e9abfaf3de963e26b94;origin=https://github.com/cpsbvbng26-dotcom/errata-check;anchor=swh:1:rev:b2f3c7ca400a235e09b91fa6fbd32e6dff0e1687), under the identifier:

```
swh:1:dir:3bfac898ac86e7f20a5a2e9abfaf3de963e26b94
```

Citation metadata is also in [`CITATION.cff`](CITATION.cff).

## Use of language models

[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-D97757?style=for-the-badge)](https://claude.com/claude-code)

The implementation of this tool was written with Claude Code (Anthropic). This applies to `errata_check.py`, `tests/check_tool.py`, `examples/`, the README, and `CITATION.cff`. This English README was translated from the Japanese one with Claude.

The author decided what to check: the approach of auditing the errata deterministically against a frozen published artifact, the policy of using no inference in the judgement, the declaration format, and the way of testing by breaking a passing state and confirming that it fails. These are the author's decisions.

Every number the checks report was obtained by running them. No language model is an author. The author (Takuya Nemoto) is responsible for every claim.

The commits in this repository are authored as `Claude`, with a `Claude-Session:` trailer at the end identifying the working session. They can be traced with `git log --author=Claude`.

The Zenodo records for v0.1.0 and v0.2.0 do not carry this statement. Files cannot be replaced after publication, so only this side can be corrected (`TL-001` in [self-correction](https://github.com/cpsbvbng26-dotcom/self-correction)).

## Changelog

[CHANGELOG.md](CHANGELOG.md) (in Japanese). Those who have copied the tool need only read the entry for the version they copied.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) (in Japanese). When adding a check, add the breaking test with it. The tool is maintained by its author alone, with no institutional backing. The scope and the backward-compatibility policy are in the same document.

---

## Where it is going

It will be submitted to JOSS (Journal of Open Source Software). The paper is [`paper.md`](paper.md); the procedure and the reasons it may not pass are in [`SUBMIT.md`](SUBMIT.md) (in Japanese). There is no result yet.

---

## Licence

[MIT](LICENSE). © 2026 Takuya Nemoto

## Where it is used

- [trinity-infinity](https://github.com/cpsbvbng26-dotcom/trinity-infinity): the author's audit of the errata for the author's own three papers
