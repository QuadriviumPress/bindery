---
name: quadrivium-repo-structure
description: The directory layout every QuadriviumPress book repo follows, by build format (MyST / Eleventy). Read this before adding a chapter, script, or workflow file.
---

# QuadriviumPress repo structure

Published QuadriviumPress books use MyST or Eleventy. The fleet also contains
source-only OpenStax CNXML mirrors and non-book infrastructure. `structure/repos.json` in
[bindery](https://github.com/QuadriviumPress/bindery) records which one each repo uses
(`format` field) and where its build output lands (`build.outputDir`). Full baseline: see
[`../../CONVENTIONS.md`](../../CONVENTIONS.md).

## MyST repos

Source of truth is Markdown under `chapters/`, `content/`, or a book-specific
layout such as `experiments/` (or `front/` + `chapters/` + `back/` +
`appendices/` for books with distinct front/back matter, e.g. `thermodynamics`,
`dynamicsTextbook`). Common files at root:

```
myst.yml              # project metadata: title, authors, keywords, TOC
AGENTS.md             # baseline link, commands, and intentional differences
index.md              # landing page / table of contents
preface.md
SOURCES.md            # per-chapter attribution (see quadrivium-attribution)
chapters/ch-NN-*.md
scripts/              # figure generation, verification (verify_book.py, export-metadata.mjs)
plugins/              # custom MyST directives (see quadrivium-myst-directives)
templates/book/       # LaTeX/PDF export template, when the repo builds print editions
tests/
```

Build: `npm run build` -> `myst build --html` -> `_build/html`. `npm run start` runs the
MyST dev server, `npm run verify` runs the book-specific fast checks, and
`npm run check` is the production-equivalent verification/build entry point.
Node 26 and npm 11.20.0 are the fleet floor (`engines` and `packageManager`
in `package.json`). Install with `npm ci`; use the exact `mystmd@1.12.0`
baseline pin. Start new books from
`opiniatedMystmdBookTemplate`, then borrow optional capabilities from a peer.
The [baseline](../../doc/myst-baseline.md) specifies package key ordering,
metadata, and scripts. Keep existing content paths and book-specific verifiers.

Every MyST `AGENTS.md` has **Standard**, **Commands**, **Intentional
differences**, and **Presentation gap** sections. Document layout and tooling
exceptions there; baseline alignment does not require rewriting chapter prose.
`myst.yml` includes `short_title`, `open_access: true`, and
`github: QuadriviumPress/<repo>` alongside the other required project metadata.
Print exports, H5P, audio, and notebook execution are optional capabilities.

## Eleventy repos

Source is usually LaTeX (`tex/` or a `*-distro` folder) converted to Markdown/Nunjucks by a
one-time or repeatable script under `scripts/`. Common files:

```
eleventy.config.js
_data/ _includes/
index.njk  pages.njk  chapter-print.njk  summary.njk  summary-json.njk  sw.njk  manifest.njk
LICENSE                # ships with the repo -- see quadrivium-attribution
```

Build: `npm run build` -> `eleventy` -> `_site`. Read the book's README and
workflows for conversion steps and tools. They use Node 26, `update:vendor`,
and figure conversion before verification.

Eleventy source families are distinct:

- LaTeX adaptations: preserve the upstream tree and converter; closest peers
  include `electromagneticsVolOneTextbook` and `mecmath-trigonometry`.
- OpenStax HTML editions: `astronomy` and the `*-bundle` books consume a
  `source/` submodule pointing to their `osbooks-*` twin. Check out submodules
  recursively; edit the edition or upstream source appropriate to the task.
- Authored Markdown: `college-physics-textbook` uses `contents/` without an
  OpenStax source submodule. Follow its own build and QA scripts.

`osbooks-*` repos are source-only CNXML mirrors: do not add Pages or a site
build. Their non-prefixed twins are the web editions.

## Catalog and publication

Treat the fleet root as a collection of independent clones, not a monorepo.
Use `structure/repos.json` for catalog metadata and build recipes, checking
the live repo tree when the catalog lags a migration. For registration, follow
[add-book.md](../../doc/add-book.md), including catalog validation and
regenerating `docs/index.html`.

Book Pages URLs normally use `https://quadriviumpress.com/<repo>/`.
Confirm the actual Pages configuration before claiming a book is deployed;
a missing catalog URL alone does not prove it is unpublished. The org landing
repo `QuadriviumPress.github.io` owns the apex site; bindery owns orchestration
and the generated catalog index.

## Everything shares

- A `README.md` with an H1 title.
- Either a root `LICENSE` file or a `## License` section in the README documenting the
  content license (see quadrivium-attribution -- this is per-repo, not inherited).
- `.github/workflows/ci.yml` and (if it deploys) `deploy.yml`, ideally calling bindery's
  reusable workflows (`QuadriviumPress/bindery/.github/workflows/{ci,deploy}.yml@main`)
  rather than reimplementing checkout/setup/deploy boilerplate. See
  [build scripts](../quadrivium-build-scripts/SKILL.md) for caller permissions
  and the inline workflows retained by specialized books.
