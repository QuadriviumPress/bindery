---
name: quadrivium-editorial-review
description: Proofread or editorially review QuadriviumPress textbook pages using the resumable Codex queue, source-aware corrections, and review ledgers. Use for prose, figure-description, or technical-content review; distinguish proofreading from a full editorial pass.
---

# Textbook proofreading and editorial review

Read the book's `AGENTS.md` and any local style guide. Work from the edition
of record and the student-facing table of contents; preserve source markup,
math, citations, labels, and the author's meaning while making corrections.
Published fleet prose generally uses American spelling. Preserve proper
names, quotations, upstream titles, and code; use local conventions to resolve
ambiguous compounds rather than performing a blanket replacement.

## Choose the requested review scope

**Proofreading** covers misspellings, wrong word forms, definite grammar,
doubled words, and broken sentences. Make separate word-level and
sentence-level passes, then reread each proposed correction in its full
sentence. Report only supported findings. Technical terminology, factual
values, and substantive clause rewrites need contextual review; they are not
high-confidence mechanical fixes. Optional wording, commas, and compound
styles are not defects by themselves.

**Editorial review** also checks explanations, equations, examples,
instructions, figure accuracy, accessibility, and consistency between pages.
Perform that broader review when requested. Derive or substantiate technical
corrections, inspect referenced figures, and keep changes consistent across
the prose, captions, diagrams, and generator sources. Laboratory claims need
checking against the actual apparatus and the assumptions behind the method.
A clean spelling report does not establish technical correctness.

## Resumable proofreading runner

Use [codex-proofread.md](../../doc/codex-proofread.md) for setup, flags,
report schema, and recovery. From bindery, a bounded report run is:

```bash
./scripts/codex-proofread.sh init --repo physicsOfWaves
./scripts/codex-proofread.sh run --repo physicsOfWaves --max-jobs 3
```

Replace the example repo with the target. Check existing queue state before
reinitializing. State and reports live in the fleet root's `.proofread/`,
not in a book repo. Default mode produces reports; fix mode applies only
high-confidence mechanical edits. Review the actual sentence before applying
any saved suggestion: reports may be stale after intervening changes.

The runner uses one bounded worker at a time with nested agents disabled.
It records failures and continues, stopping after eight consecutive failures.
Diagnose saved stderr and use `init` to requeue errors rather than increasing
concurrency. Source-only `osbooks-*` mirrors are skipped; review their HTML
twins. Check source selection for converted books with overlapping editions
(e.g. `differentialEquations` uses `trench-distro/TRENCH_DIFFEQ_BV.tex`).

## Editorial inventory and evidence

For MyST review, run the read-only inventory from bindery:

```bash
python3 scripts/audit-myst-fleet.py --book physicsOfWaves --json
```

It lists TOC pages, capabilities, missing/truncated alternative text, and
unlisted content candidates. Inspect those candidates in context; the audit
uses heuristics and does not prove a page has been read or a figure is sound.
For damaged alt text, inspect the image and surrounding explanation before
restoring the description, especially when conversion dropped inline math.

For a tracked MyST editorial campaign, record reviewed pages, substantive
findings, edits, checks, and limitations in the book's
`reviews/editorial-review.md`. Update bindery's
[review ledger](../../reviews/myst-fleet-2026.md) when that campaign is in scope.
Count only pages actually read. Distinguish verifier results, site builds,
HTML/link checks, and visual or export inspection; report blocked checks
accurately. The book's `verify` and `check` remain the project gates.

If a figure is generated, edit its source and rebuild the committed asset.
If H5P fallback text is generated, edit the quiz source and regenerate;
see [H5P activities](../quadrivium-h5p-activities/SKILL.md). Check the relevant
output when a fix affects PDF/DOCX or an interactive fallback.
