# QuadriviumPress `bindery`

Orchestration repository for the [QuadriviumPress](https://github.com/QuadriviumPress)
organization. Bindery owns the **operational** side of the org: the reusable CI/CD
workflows every book calls, the machine-readable repository catalog, cross-repo fleet
scripts, and the GitHub Pages book index. Modeled on
[OpenPhysics/Baton](https://github.com/OpenPhysics/Baton), which does the same job for
QuadriviumPress's sister org of interactive physics simulations -- see
[`CONVENTIONS.md`](CONVENTIONS.md) for what didn't (yet) come along for the ride.

> Community-health defaults (license, contributing, code of conduct, security policy,
> issue/PR templates, org profile) live in [QuadriviumPress/.github](https://github.com/QuadriviumPress/.github).
> **Content** license is different: each book adapts a different upstream work under that
> work's own terms, so it's documented per-repo -- see
> [`skills/quadrivium-attribution/SKILL.md`](skills/quadrivium-attribution/SKILL.md).

## Why a catalog instead of submodules

QuadriviumPress is 25+ book repos across three build formats (MyST, Eleventy, Jekyll), plus
a handful of `osbooks-*` repos that just hold raw OpenStax source as an upstream reference.
Each book deploys independently to its own GitHub Pages site; nothing needs a synchronized
whole-org checkout. [`structure/repos.json`](structure/repos.json) is the single source of
truth -- adding a repo there is all `clone-fleet.sh` needs to pick it up, with no submodule
pointer-bump commits to keep in sync.

## Contents

| Path | Purpose |
|---|---|
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Reusable CI workflow (auto-detects Node/Python, runs a caller-supplied build command) |
| [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) | Reusable GitHub Pages deploy workflow (caller supplies `output-dir`) |
| [`.github/workflows/shared-compliance-check.yml`](.github/workflows/shared-compliance-check.yml) | Weekly + on-demand audit of every active repo against `CONVENTIONS.md` |
| [`.github/workflows/fleet-health.yml`](.github/workflows/fleet-health.yml) | Weekly build-health check of every active book, using its catalog build recipe |
| [`.github/workflows/bindery-selfcheck.yml`](.github/workflows/bindery-selfcheck.yml) | Validates bindery's own invariants: catalog schema, shell syntax, plugin manifest, Pages freshness |
| [`.github/workflows/pages.yml`](.github/workflows/pages.yml) | Deploys `docs/index.html` to `quadriviumpress.github.io/bindery` |
| [`scripts/`](scripts/) | Catalog query/clone/compliance/pages-generation tooling -- see below |
| [`doc/codex-proofread.md`](doc/codex-proofread.md) | Paced fleet-wide Codex spelling/typo pass (`scripts/codex-proofread.sh`) |
| [`config/`](config/) | Canonical Dependabot and Claude-settings templates |
| [`structure/repos.json`](structure/repos.json) | Machine-readable catalog of org repositories |
| [`structure/repos.schema.json`](structure/repos.schema.json) | JSON Schema for the catalog (`schemaVersion` 1.0.0) |
| [`CONVENTIONS.md`](CONVENTIONS.md) | Shared repo structure every book follows |
| [`skills/`](skills/) | QuadriviumPress authoring reference docs for AI assistants |
| [`.claude-plugin/`](.claude-plugin/) | Marketplace + plugin manifests packaging `skills/` as the `quadrivium@quadriviumpress` Claude Code plugin |
| [`docs/`](docs/) | Generated book index ([quadriviumpress.github.io/bindery](https://quadriviumpress.github.io/bindery/)) |
| [`doc/add-book.md`](doc/add-book.md) | Checklist for adding a book to the catalog |
| [`doc/quire-git.md`](doc/quire-git.md) | Cheat sheet: everyday git across local checkouts (`pull`/`push`/`status` all) |

## Claude Code plugin

This repo doubles as a Claude Code [marketplace](.claude-plugin/marketplace.json). It
publishes one plugin, **`quadrivium`**, bundling the [`skills/`](skills/) reference docs
(repo structure by format, MyST directive usage, attribution/licensing conventions) so any
book repo can load them as a unit.

Member repos enable it from `.claude/settings.json` (canonical keys in
[`config/claude-settings.json`](config/claude-settings.json)):

```json
{
  "extraKnownMarketplaces": {
    "quadriviumpress": { "source": { "source": "github", "repo": "QuadriviumPress/bindery" } }
  },
  "enabledPlugins": { "quadrivium@quadriviumpress": true }
}
```

Or interactively: `claude plugin marketplace add QuadriviumPress/bindery` then
`claude plugin install quadrivium@quadriviumpress`.

## Shared CI

A book's `.github/workflows/ci.yml` calls the reusable workflow, telling it how to build:

```yaml
jobs:
  ci:
    uses: QuadriviumPress/bindery/.github/workflows/ci.yml@main
    with:
      build-command: npm run build        # myst build --html / eleventy / jekyll build
      install-hunspell: true               # if the build spell-checks prose
```

And, for any book that deploys:

```yaml
on:
  push: { branches: [main] }
  workflow_dispatch:

jobs:
  deploy:
    uses: QuadriviumPress/bindery/.github/workflows/deploy.yml@main
    with:
      build-command: npm run build
      output-dir: _build/html             # MyST; Eleventy/Jekyll use _site
    permissions:
      contents: read
      pages: write
      id-token: write
```

`output-dir` isn't defaulted because it genuinely differs by format -- check the book's own
entry in `structure/repos.json` (`build.outputDir`) rather than guessing.

## Compliance check

[`shared-compliance-check.yml`](.github/workflows/shared-compliance-check.yml) runs weekly
and on manual dispatch: it reads `structure/repos.json`, clones each active repo, and runs
[`scripts/check-repo-compliance.sh`](scripts/check-repo-compliance.sh). It **fails** a repo
missing a README title or a documented content license, and **warns** (without failing) on
migration gaps -- not yet calling bindery's reusable `ci.yml`/`deploy.yml`, a missing
`engines.node` pin -- since a repo with its own working CI still ships fine. Run locally:

```bash
scripts/check-repo-compliance.sh /path/to/book-repo
```

## Repository catalog

[`structure/repos.json`](structure/repos.json) lists all QuadriviumPress repositories with
metadata: `displayName`, `type` (book/bundle/tool/config/site), `lineage` (original /
openstax-remix / public-domain-adaptation), `source` (author/title/url/license for adapted
works), `format` (myst/eleventy/jekyll), `deployedUrl`, `subjectTopics`, `build` recipe, and
`status`. Schema: [`structure/repos.schema.json`](structure/repos.schema.json), validated by
[`scripts/check-repos-catalog.sh`](scripts/check-repos-catalog.sh). Query it:

```bash
scripts/check-repos-catalog.sh
scripts/list-repos.sh --summary
scripts/list-repos.sh --book --format myst --names
scripts/list-repos.sh --json
```

**Adding a book**: see [`doc/add-book.md`](doc/add-book.md).

Scripts assume `bindery` lives beside member repos in a shared workspace; set
`QUADRIVIUM_WORKSPACE` or pass `--catalog /path/to/repos.json` if your checkout differs.

## Fleet operations

- **Clone the fleet** -- [`scripts/clone-fleet.sh`](scripts/clone-fleet.sh) clones every
  catalog repo as a sibling directory (`--update` fast-forwards ones already present;
  `--book`/`--type`/`--lineage`/`--only`/`--skip` filter which; `--dry-run` previews).
- **Everyday git fan-out** -- [`scripts/quire`](scripts/quire) runs any git command across
  every local catalog checkout (`quire push`, `quire pull --ff-only`, `quire status -s`).
  Cheat sheet: [`doc/quire-git.md`](doc/quire-git.md). Symlink onto `PATH` with
  `ln -sfn ~/QuadriviumPress/bindery/scripts/quire ~/.local/bin/quire` (coexists with
  OpenPhysics/Baton's `fleet`).
- **Compliance audit** -- weekly via `shared-compliance-check.yml` (above).
- **Build health** -- [`fleet-health.yml`](.github/workflows/fleet-health.yml) runs weekly,
  fanning out one job per active book using its catalog `build` recipe. Read-only; surfaces
  books broken by an upstream dependency bump before the live site goes stale.
- **Book index** -- `scripts/generate-pages-index.sh` regenerates `docs/index.html` from the
  catalog; `bindery-selfcheck.yml` fails CI if it's out of date with a committed change to
  `structure/repos.json`.

## Node version

The fleet's Node floor is **`22`**, the default in `ci.yml` / `deploy.yml` / `fleet-health.yml`.
Node-based member repos should declare `engines.node: ">=22"`.
