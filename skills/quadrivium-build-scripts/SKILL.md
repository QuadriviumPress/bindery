---
name: quadrivium-build-scripts
description: Two vendored helper scripts most MyST book repos need and the non-obvious bugs both modernPhysics and physicsOfMusic independently hit -- scripts/fetch-exports.sh's gh CLI token, and scripts/run-myst.mjs's npm-version-probe launcher for MyST 1.10.1. Read before writing either from scratch in a new book repo.
---

# Book-local build scripts

Unlike `ci.yml`/`deploy.yml`, which call bindery's reusable workflows, `scripts/fetch-exports.sh`
and `scripts/run-myst.mjs` are **vendored per repo** -- copy an existing one (e.g. from
`modernPhysics` or `physicsOfMusic`) rather than writing either from scratch; both books
independently reinvented, and separately re-broke, the same two fixes below on the same day.

## `fetch-exports.sh`: `gh` needs `GH_TOKEN`, not `GITHUB_TOKEN`

Purpose: download the print editions produced by a separate `exports.yml` workflow (or fall
back to the latest release) before the HTML build, so `myst.yml`'s `downloads:` entries resolve.
It shells out to the `gh` CLI (`gh run list`, `gh run download`), which reads `GH_TOKEN` --
GitHub Actions only injects `GITHUB_TOKEN` into the environment by default, and bindery's
`deploy.yml` only maps one to the other around its *own* export-fetch step, not inside a script
a repo runs independently (`export-smoke.yml`, a manual local run, a differently-shaped
workflow). Every vendored `fetch-exports.sh` needs its own mapping at the top:

```bash
#!/usr/bin/env bash
set -euo pipefail

# `gh` requires GH_TOKEN; Actions exposes GITHUB_TOKEN by default.
export GH_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
```

Both `modernPhysics` and `physicsOfMusic` shipped without this line, then added it in an
identically-worded commit ("Map GITHUB_TOKEN to GH_TOKEN in fetch-exports") once CI's `gh run
list` started failing with an auth error. Include the line when first vendoring the script.

## `run-myst.mjs`: MyST 1.10.1's broken npm probe

MyST 1.10.1 bundles `check-node-version`, which shells out to `npm --version` from Node and
reads its stdout to validate the toolchain. On some Node/npm combinations that nested probe
returns exit status 0 with **empty stdout**, so MyST reports `npm Package Not Found` and exits
before building anything -- even though the real `npm` on `PATH` works fine for every other
purpose. `scripts/run-myst.mjs` works around it without patching MyST itself:

1. Resolves the actual npm version from `npm_config_user_agent` (set by npm itself when it runs
   a script) or the `packageManager` field in `package.json`.
2. Writes a tiny shim script to a temp dir that answers `npm --version` with that resolved
   version and delegates every other invocation to the real npm (found via `npm_execpath` or a
   `PATH` search).
3. Puts that shim dir ahead of `PATH`, then execs the local `node_modules/.bin/myst` directly --
   which also sidesteps a separate `npx`/bare-`myst` problem: `node_modules/.bin` isn't on
   `PATH` in Bindery's plain `run:` steps, so a bare `myst` invocation there exits 127.

Every build entry point should go through this launcher, not a bare `myst` or `npx myst` call --
npm scripts, `deploy.yml`, an export-smoke workflow, and any other script that shells out to
MyST. `physicsOfMusic`'s adoption commit ("Invoke MyST through a launcher that hands it a
working npm probe") touched `package.json`, `deploy.yml`, `export-smoke.yml`,
`build-exports.sh`, and `smoke-exports.py` in one pass for exactly this reason -- a launcher only
one of several entry points goes through still leaves the other entry points exposed to the same
failure.

## Borrowing these for a new book

Neither script is provided by bindery or the template -- both are copy-from-a-peer, same as
everything else here. When scaffolding a new MyST book (or adding print exports to an existing
one, see [`quadrivium-print-exports`](../quadrivium-print-exports/SKILL.md), which needs
`fetch-exports.sh`):

1. Copy `scripts/fetch-exports.sh` verbatim from `modernPhysics` or `physicsOfMusic` -- the
   `GH_TOKEN` mapping at the top is the only line that matters and it's already there; only the
   `exports.yml` workflow name and the downloaded filenames need to match the new repo.
2. Copy `scripts/run-myst.mjs` verbatim -- it's fully generic (derives everything from
   `package.json`/`npm_config_user_agent`, nothing book-specific). Point every build entry point
   at it: `package.json`'s `start`/`build`/`check` scripts, `deploy.yml`, `ci.yml`'s
   `build-command` input if it calls MyST directly, and any export workflow.
3. Copy the matching `tests/run-myst.test.mjs` and `tests/fetch-exports.test.mjs`/equivalent
   alongside them rather than skipping tests for "just infrastructure" -- both bugs above were
   caught by exactly this kind of test once added, not before.
