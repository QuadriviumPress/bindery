---
name: quadrivium-print-exports
description: How QuadriviumPress MyST books generate printable PDF and Word (DOCX) editions from the same chapter source as the website -- the export.mjs transform, the local jtex LaTeX template, the pandoc-based DOCX pipeline, and where each piece runs in CI. Read before adding print support to a MyST book, or debugging a PDF/DOCX that drops content the website shows fine.
---

# PDF and DOCX exports from a MyST book

Real implementations: `modernPhysics/` and `physicsOfMusic/` (also `modernClassicalMechanics/`).
One chapter source produces four kinds of output -- the website, a full PDF (with worked
solutions), a student PDF (without), and a DOCX -- plus one standalone PDF offprint per chapter.
Nothing in `chapters/*.md` is written differently for print; the pipeline below adapts the same
Markdown, gated entirely by environment variables so a plain `myst build --html` is unaffected.

## Why not MyST's own `--docx`

MyST's DOCX renderer writes every equation as `Math(MathRun(latex))` -- the raw LaTeX *string*
dropped into a Word equation field, unreadable without a manual Convert-to-Professional per
equation. At the scale of a full textbook (`modernPhysics` has roughly 470 display equations and
6000 inline ones) that renderer is unusable. The fix: export `pdf+tex` (`format: pdf+tex` in
`myst.yml`'s `exports:` entry) to keep MyST's intermediate `.tex`, and build the DOCX from
*that* with pandoc, which converts LaTeX math to OMML that Word actually renders and edits. PDF
and DOCX therefore always share one set of numbers and cross-references, because they're built
from the same source file, not built in parallel from Markdown.

## `plugins/export.mjs`: teaching the LaTeX renderer five node types

`myst-to-tex` only renders a fixed set of node types and silently drops anything else. Five
types most books lean on heavily aren't in that set: `exercise`, `solution`, `aside` (`{margin}`
notes), `details` (`{dropdown}`), and `iframe` (every embedded simulation/animation/video --
intentional, see [`quadrivium-media-plugins`](../quadrivium-media-plugins/SKILL.md)). Without
this plugin a PDF silently loses the entire Problems section of every chapter, buried under a
wall of `Unhandled LaTeX conversion for node of "<type>"` build errors.

MyST's plugin loader only reads `directives`, `roles`, and `transforms` -- there's no way to
register an export-format renderer directly -- so `export.mjs` is a **transform** that rewrites
those five node types into ones the renderer already understands, and only when an export is
being built:

- **Gated by `MYST_PRINT`**, read once at module scope. Unset (the website build) makes the
  plugin a no-op; `full` or `student` selects the edition, and `student` additionally strips
  every `solution` node -- that env var is the *only* difference between the two book PDFs.
- **Runs at `stage: 'project'`**, which is *after* `resolveReferencesTransform` -- every
  `enumerator` ("4.1") is already assigned and every cross-reference's link text already
  resolved by the time this transform sees the tree. Rewriting the node types earlier (document
  stage) would lose both.
- **Nothing it emits may be boxed.** LaTeX cannot open a float inside `framed`/`minipage`/any
  other box; roughly a quarter of worked solutions contain a `{figure}`, and a naive
  exercise-as-`framed` rewrite fails with "Not in outer par mode" and silently drops the figure,
  its caption, and every `{numref}` pointing at it.
- **Cross-references need an explicit label.** A plain rewritten block carries no `\label`, so
  in-text links to `#ex-...` would dangle. Each rewritten exercise/solution opens with raw TeX
  that pins `\@currentlabel` to MyST's own enumerator *before* emitting `\label`, so the printed
  number matches the website's number rather than whatever counter LaTeX happens to hold at that
  point.
- **`MYST_SITE_URL`** (also read once) redirects internal cross-book references ("see Chapter
  7") to the live website instead of an in-document jump, for chapter offprints only -- a
  single-chapter PDF has no Chapter 7 to jump to. It must be emptied, not just left unset, when
  building the *whole* book (see the ordering note in `build-exports.sh` below), or the book's
  own internal links leak out to the web.

If you add a sixth custom MyST node type a chapter relies on, it needs the same treatment here or
it will vanish from print without a visible error beyond a build-log warning.

## `templates/book/template.tex`: a local jtex template

Referenced from `myst.yml` as `template: ./templates/book`, this began as MyST's stock
`plain_latex_book` and diverges in ways specific to being printed rather than read on a screen:
page geometry and running heads sized for paper, a `\frontmatter` copyright page and preface
(since `index.md` is the website's landing page, not part of the printed book, and the preface
must stay unnumbered), sectioning depth pinned to match the website's numbering exactly, the
`\mystexercisestart`/`\mystsolutionstart`/etc. commands `export.mjs` brackets exercises and
solutions with, and a `[# if options.chapter #]` branch that switches `\documentclass` from
`book` to `article` for a **standalone single-chapter offprint**, with the chapter's original
number restored into LaTeX's counters so it isn't renumbered as "Chapter 1."

Built with XeLaTeX specifically (`fontspec`, not the pdfTeX `fontenc`+`inputenc` pair), because
the source carries raw Unicode math and prose symbols (Å, β, °, ×, ⊕, ℓ) that 8-bit EC fonts
under T1 encoding silently drop as "Missing character" warnings and blank space.

## `scripts/build-exports.sh`: orchestration and its ordering gotcha

```
scripts/build-exports.sh [book|student|chapters|docx|pdf|all]
npm run build:exports   # == build-exports.sh all
npm run build:pdf       # the two book PDFs only
```

Requires Node 22, a TeX Live with XeLaTeX + latexmk, Inkscape (MyST's only supported SVG→PDF
converter), and for the DOCX step: pandoc, poppler-utils, and optionally ImageMagick.

The one non-obvious thing here: **the full and student PDFs both build to the single `output:`
path** named in `myst.yml`, so `build_student` runs *before* the book is built with
`MYST_PRINT=full`, and the student output is renamed out of the way immediately after. `all`
therefore orders `build_student` → `build_docx` (which rebuilds the full edition and owns the
`.tex` the DOCX needs) → `build_chapters` last. Building `docx` alone silently rebuilds the full
PDF first for exactly this reason -- a Word file quietly missing every solution is not a failure
anyone would notice by reading it. `MYST_SITE_URL` is explicitly emptied (not just inherited)
when building the whole book, and explicitly set only for `build_chapters`, matching the
`export.mjs` behavior above.

## `scripts/tex-to-docx.py`: pandoc, not myst --docx

Takes the `.tex` the PDF step already produced and:

1. Wraps it in a minimal preamble with no-op stubs for the four `\mystexercise*`/`\mystsolution*`
   spacing commands `export.mjs` emits -- pandoc can't parse the template's real preamble and
   doesn't need to, since it's only asked to read the document body.
2. Flattens `\include{ch-NN}` manually (concatenates each chapter file into the master) rather
   than trusting pandoc's own include resolution, which resolves paths relative to the working
   directory rather than the source tree.
3. Rasterizes every referenced PDF figure to PNG, since Word has no PDF image support. Uses
   **poppler's `pdftoppm`**, not ImageMagick, as the primary path: Ubuntu's ImageMagick policy
   refuses to read PDF at all (it delegates to Ghostscript, which the policy also blocks), so an
   ImageMagick-based rasterizer works on a developer's laptop and silently ships a Word file with
   every figure missing on a CI runner. ImageMagick is kept only as a local-machine fallback when
   `pdftoppm` isn't installed.

Then calls `pandoc --from=latex --to=docx --number-sections` so the Word file's section numbers
match the PDF's and the website's.

## Where each piece runs

- **`exports.yml`** is the *only* place PDFs/DOCX get built — monthly cron, on a `v*` tag, or
  manual dispatch, uploading artifacts (90-day retention) and, on a tag push, a durable GitHub
  Release. `deploy.yml` **does not** rebuild exports on every push to `main`: it downloads the
  most recent successful `exports.yml` artifact instead (see `scripts/fetch-exports.sh` in
  [`quadrivium-build-scripts`](../quadrivium-build-scripts/SKILL.md)), because installing TeX
  Live and running XeLaTeX on every one-word prose fix would make ordinary pushes slow. This
  means the site's download menu tracks the last monthly/tagged/manual export, not the current
  commit — expected, not a bug.
- **`export-smoke.yml`** runs on pull requests that touch `plugins/`, `templates/`,
  `scripts/build-exports.sh`, `scripts/tex-to-docx.py`, `myst.yml`, or `chapters/**`, and is
  deliberately cheap: it runs the fast unit/content tests (`npm run test:exports`, which exercises
  `plugins/export.mjs`'s node-rewriting logic directly rather than building a full PDF) plus a
  **PDF build of one representative chapter and whichever chapters the PR actually changed** —
  not the whole book — so a broken export transform is caught on the PR, without paying the full
  book's XeLaTeX build time on every push.
- **`myst.yml`'s `downloads:` list** wires the built files into the site's per-page download
  menu. Each entry needs `static: true`: without it, a missing file (true on a fresh clone or
  during `myst start`, since the PDFs are CI-only build artifacts) is an unsuppressible error;
  with it, the complaint is downgraded to the `static-action-file-copied` warning rule.

## Borrowing this for a new book

Not in `opiniatedMystmdBookTemplate` -- print export is an opt-in, sizeable addition (a TeX Live
+ Inkscape + pandoc toolchain, a dedicated CI workflow) that only makes sense once a book commits
to shipping print editions. To bring it into an existing MyST book, copy from `modernPhysics` or
`physicsOfMusic` (whichever has the closer chapter structure -- front/back matter vs. flat
chapters changes the `articles:` list below) and rename the book-specific slug everywhere it
appears:

1. `plugins/export.mjs` and `templates/book/{template.tex,template.yml}` -- copy as-is; nothing
   in either is book-specific except the title-page/copyright text inside `template.tex`'s
   `\frontmatter` block and the `title/authors/license` in `template.yml`.
2. `scripts/build-exports.sh`, `scripts/tex-to-docx.py`, and `scripts/export-metadata.mjs` --
   copy as-is; `build-exports.sh`'s `BOOK` path and `tex-to-docx.py`'s `--tex-dir`/`--output`
   defaults derive from the `output:` path set in step 3, so update the constants there rather
   than passing flags at every call site.
3. `myst.yml`: add an `exports:` entry (`format: pdf+tex`, `output: exports/<slug>.pdf`, and the
   book's own `articles:` list with `level: 0`/`level: -1` matching its actual front/back
   matter), plus the three `downloads:` entries (`static: true`, per the note above) once exports
   exist to download.
4. `package.json`: the `build:pdf`/`build:docx`/`build:chapters`/`build:exports` scripts and
   `test:exports`, verbatim.
5. `.github/workflows/exports.yml` and `.github/workflows/export-smoke.yml` -- copy as-is except
   the artifact names (`<slug>-exports`, `<slug>-docx`), the release-upload filenames, and
   `export-smoke.yml`'s representative chapter path and `paths:` trigger list (which should name
   this book's own `plugins/`, `templates/`, `chapters/` -- copying another book's exact paths
   silently makes the smoke test never trigger).
6. Confirm `scripts/fetch-exports.sh` (see
   [`quadrivium-build-scripts`](../quadrivium-build-scripts/SKILL.md)) and `deploy.yml` download
   from *this* repo's `exports.yml` run, not the peer's.

Skip this whole skill for a book that only ever ships as a website -- most of the fleet does not
have a `templates/book/` directory, and that's the default, not a gap.
