---
name: quadrivium-repo-structure
description: The directory layout every QuadriviumPress book repo follows, by build format (MyST / Eleventy / Jekyll). Read this before adding a chapter, script, or workflow file.
---

# QuadriviumPress repo structure

QuadriviumPress books are built with one of three formats. `structure/repos.json` in
[bindery](https://github.com/QuadriviumPress/bindery) records which one each repo uses
(`format` field) and where its build output lands (`build.outputDir`). Full baseline: see
[`../../CONVENTIONS.md`](../../CONVENTIONS.md).

## MyST repos

Source of truth is Markdown under `chapters/` (or `front/` + `chapters/` + `back/` +
`appendices/` for books with distinct front/back matter, e.g. `thermodynamics`,
`Dynamics_Textbook`). Common files at root:

```
myst.yml              # project metadata: title, authors, keywords, TOC
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
Node 22 is the fleet floor (`engines.node` in `package.json`).

## Eleventy repos

Source is usually LaTeX (`tex/` or a `*-distro` folder) converted to Markdown/Nunjucks by a
one-time or repeatable script under `scripts/`. Common files:

```
eleventy.config.js
_data/ _includes/
index.njk  pages.njk  chapter-print.njk  summary.njk  summary-json.njk  sw.njk  manifest.njk
LICENSE                # ships with the repo -- see quadrivium-attribution
```

Build: `npm run build` -> `eleventy` -> `_site`.

## Jekyll repos

`musicTheory` is the only current example: `_config.yml`, `Gemfile`, content as loose
Markdown pages at the repo root plus `_includes/` / `_layouts/` / `_sass/`. Build:
`bundle exec jekyll build` -> `_site`.

## Everything shares

- A `README.md` with an H1 title.
- Either a root `LICENSE` file or a `## License` section in the README documenting the
  content license (see quadrivium-attribution -- this is per-repo, not inherited).
- `.github/workflows/ci.yml` and (if it deploys) `deploy.yml`, ideally calling bindery's
  reusable workflows (`QuadriviumPress/bindery/.github/workflows/{ci,deploy}.yml@main`)
  rather than reimplementing checkout/setup/deploy boilerplate.
