---
title: 'errata-check: deterministic auditing of correction records against frozen scholarly artifacts'
tags:
  - research integrity
  - post-publication correction
  - errata
  - reproducibility
  - continuous integration
  - Python
authors:
  - name: Takuya Nemoto
    orcid: 0009-0000-1406-0547
    affiliation: 1
affiliations:
  - name: Independent researcher, Japan
    index: 1
date: 10 September 2026
bibliography: paper.bib
---

# Summary

When a piece of research is published with a digital object identifier, the file
itself is frozen: it cannot be edited afterwards. What can still be edited is the
correction record — the errata document that says which statements in the frozen
file turned out to be wrong, which were withdrawn, and which cannot be repaired at
all. Because only one side of the pair can change, the two slowly drift apart. A
quoted sentence loses a character. A list that once had six entries is described
as having three. An item that was declared impossible to fix quietly reappears as
resolved.

`errata-check` compares the correction record against the frozen files it
describes and reports every disagreement. The comparison is written down in
advance, in a plain declaration file: which passages the record claims are printed
in the source, which it claims are absent, how many entries it declares, which
entries it has declared unrepairable, and a checksum of each source file.

The tool makes no judgement of its own. It has no language model and no
approximate matching; it reports presence, absence, and exact equality after a
documented normalisation of spacing and character forms. Because the output does
not need a human to re-read it, the comparison can run automatically on every
change, in the same way that a test suite does.

# Statement of need

Most tools that check scholarly claims act *before* publication and operate on the
manuscript. `statcheck` recomputes reported statistical tests from the printed
statistics and degrees of freedom [@nuijten2016]; the GRIM test asks whether a
reported mean is arithmetically reachable from integer data at the reported sample
size [@brown2017]; reference checkers confirm that citations resolve. All of these
examine a document that can still be edited.

The correction record is the opposite case, in three ways. It exists only *after*
publication. It is the one editable half of a frozen pair. And it is written and
maintained by the same author whose errors it enumerates. That last property is
why a machine is needed rather than care, and it is what two of the tool's checks
are aimed at:

- **Completeness.** If the record states that a claim appears in twelve places,
  twelve must be found. Under-counting is the cheapest way to make an admission
  smaller without saying anything false.
- **Unrepairability.** An entry declared unrepairable must not later appear as
  resolved unless the declaration itself is changed first.

The remaining checks catch ordinary mistakes rather than convenient ones: an
altered quotation, a substituted source file, a "last updated" date older than a
date inside the document, a count given in prose that disagrees with the count a
command actually produces.

The audience is any author or group maintaining errata for versioned, DOI-bearing
outputs — increasingly common with preprint servers and repositories that mint a
new identifier per version, where the published record and its corrections are
routinely separate documents.

# State of the field

`statcheck` and GRIM are the closest relatives, and the tool implements both ideas
independently, but they answer a different question: whether the numbers inside a
manuscript are internally consistent. They do not compare two documents, and they
have nothing to say about counts, unrepairable entries, or file substitution.

Reference linters and CI documentation linters check formatting and link
resolution within a single tree; version-control review compares two revisions of
an editable file. None of these apply when one side of the comparison is a
published artifact that cannot be revised.

The build-versus-contribute question was therefore whether to extend `statcheck`.
The answer was no: `statcheck` is a within-manuscript numerical checker, while the
object here is the relationship between two documents, only one of which may
change. Extending it would have meant replacing its core. Where existing work did
fit, it was reused rather than rewritten — PDF text extraction is delegated to
`pypdf`, and the statistical distributions used for recomputation are checked
against published tables rather than reimplemented from scratch.

# Software design

Four trade-offs shaped the implementation.

**Determinism over coverage.** No inference of any kind is permitted in a verdict.
This deliberately gives up detection of paraphrase-level drift. What it buys is
that a failure is never a suggestion: it can gate a continuous-integration run,
because no human has to decide whether the tool was right.

**An explicit declaration file rather than inference from prose.** The claims the
correction record makes must be written out in TOML before they can be checked.
This is more work for the author, and it is the point: adding a claim to the prose
without declaring it produces a failure, so the declaration cannot silently fall
behind the document.

**A single file with almost no dependencies.** The tool is one Python module;
`pypdf` is needed only for PDF sources. This makes it vendorable, and it is in
fact vendored into three separate repositories, each pinning a specific released
version and citing that version's identifier. The cost is that it forgoes some
conveniences of a larger package.

**Break-tests instead of pass-tests.** A checking tool cannot be trusted by
passing, because a tool that inspects nothing passes everything. The suite
therefore constructs a passing state and then breaks it in 26 distinct ways —
altering a quotation, declaring an absent passage present, substituting a source
file, deleting a checksum declaration, falsifying a count, rewriting an
unrepairable entry as resolved, and so on — asserting each time that exactly the
corresponding check fails. A final case asserts that a line wrapped across a page
boundary does *not* fail, constraining false positives as well. The suite reports
72 checks, and its test documents are generated by a script so that a pass cannot
be an artefact of one particular real file.

Because what can be settled deterministically from a printed page differs by
discipline, the declaration language also covers recomputation of *p* from printed
test statistics (*t*, *F*, χ², *r*), the GRIM test, check digits for ORCID, ISBN
and ISSN, declared arithmetic relations among printed numbers, Japanese era-year
to Gregorian mapping for archival work, and reference declarations recording which
passage of a cited source supports which claim.

# Research impact statement

The tool is in continuous use auditing four frozen bodies of work by the author:
three mathematical preprints, three papers in philosophy, and an archival source
note, comprising **240 declared audit items** across three repositories, run in
continuous integration on every change. Three repositories vendor the module at a
pinned released version and cite the corresponding archived identifier.

The audits have produced findings that were not visible by reading. A claim that a
verification script was bundled with a paper was believed to appear in three
places; counting by machine found six, and the files did not exist. A bibliography
entry was found that the body never cites, and separately a source named in the
body was found missing from the bibliography. One term was found rendered two
different ways in English within a single document. Each of these is recorded in
the corresponding errata file.

Use beyond the author has not yet occurred, and no claim of external adoption is
made here.

# AI usage disclosure

**Tools and where they were used.** The implementation (`errata_check.py`), the
test suite, the examples, the documentation, and the text of this paper were
written with Claude Code (Anthropic). The specific model used for each change is
recorded per-commit in the `Co-Authored-By` trailer of the repository's history
and can be listed with `git log`.

**Nature and scope of assistance.** Code generation, test scaffolding, refactoring,
documentation drafting, and drafting of this paper.

**Confirmation of review.** The author reviewed, edited and validated all
AI-assisted output, and made the core design decisions: the framing that the
correction record rather than the frozen artifact is the object to be audited; the
rule that no inference may enter a verdict; the structure of the declaration
language; and the break-test method described above. Every number reported in this
paper was produced by executing the code. AI is not an author. The author is
responsible for the accuracy, originality and licensing of all submitted material.

# Acknowledgements

No financial support was received for this work, and no sponsor had any
involvement in it. The author declares no conflicts of interest.

# References
