---
name: quadrivium-build-scripts
description: Configure QuadriviumPress book build commands, reusable CI/Pages workflows, export downloads, and optional MyST launchers. Use when scaffolding tooling or diagnosing a local build that fails in CI.
---

# Book build commands and workflows

Read the target book's `AGENTS.md`, `package.json`, and workflows before copying
from a peer. The shared [MyST baseline](../../doc/myst-baseline.md) defines the
command contract; the starter implementation is `opiniatedMystmdBookTemplate`.
Keep capability scripts in the books that need them.

## MyST command contract

- Install with `npm ci` using the committed lockfile and local `mystmd` dependency.
  The baseline pins `mystmd` exactly to `1.11.0`, with Node >=26 and npm 10.
  Read the baseline and current starter for dependency details; do not copy an
  older peer's package versions over a book's newer dependency updates.
- Provide `start`, `build`, `verify`, and `check`. `verify` contains the book's
  fast checks; `check` combines verification and a strict HTML/link build.
- Preserve prebuild hooks such as `h5p:prepare` and postbuild PWA setup. Calling
  `myst build --html` directly bypasses npm lifecycle hooks; explicitly cover
  those steps if a workflow needs a custom build command.
- Record extra scripts, package keys, and command differences in `AGENTS.md`.

Keep `--strict --check-links`. The baseline's `myst.yml` error rules ignore
remote `link-resolves` failures for `"{http,https}://**"` and `doi-link-valid`,
while internal links and missing local files still fail. Copy those scoped
rules from the baseline rather than disabling link checking altogether.

## Reusable CI and Pages deployment

MyST callers normally use
`QuadriviumPress/bindery/.github/workflows/{ci,deploy}.yml@main`. Read those
files for supported inputs before adding custom workflow machinery. Both
expose `node_modules/.bin` through `$GITHUB_PATH`, so a local `myst` works
in subsequent plain shell steps. Do not replace the runner's entire `PATH`.

A deploy caller's permissions must include all four:

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
  actions: read
```

`actions: read` is requested by the reusable workflow for prior export
artifacts; a caller that restricts permissions must grant it even when its
own book has no print editions. Deploy should run the book's verifier before
publishing, commonly through `pre-build-command: npm run verify`. CI should
gate on `verify`/`check`, preserving each book's chosen checks.

Both workflows set `BASE_URL=/<repo>` for the job, including verification.
Use the same environment when investigating deployment-only asset failures;
see [media plugins](../quadrivium-media-plugins/SKILL.md) and
[PWA setup](../quadrivium-pwa/SKILL.md). Set `output-dir: _build/html` for
MyST or `_site` for Eleventy.

Specialized books may keep inline workflows. For Eleventy/LaTeX, match the
book's actual Node version (typically 24), recursive source submodules,
`update:vendor`, and figure tools. EPS needs Ghostscript/dvisvgm; TikZ may
also need pdflatex and TeX packages. The weekly
[fleet-health workflow](../../.github/workflows/fleet-health.yml) demonstrates
those distinctions. Executable notebooks may need a registered `python3`
ipykernel. A successful dependency install alone does not supply these tools.

## `fetch-exports.sh`: credentials and complete artifacts

For books with separate print builds, copy this script from a current peer
such as `modernPhysics` or `physicsOfMusic`. Match `GITHUB_REPOSITORY`,
workflow name, artifact names, release patterns, and expected filenames to
the target book. The script fetches the latest successful `exports.yml`
artifacts, then falls back to a release; it should accept only a complete
export set. See [print exports](../quadrivium-print-exports/SKILL.md).

Bindery maps `GH_TOKEN` in the deploy pre-build hook. A script used elsewhere
still needs credentials supplied by its caller or this compatibility mapping:

```bash
export GH_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
```

Actions tokens are available through the `github.token` context; shell steps
must explicitly receive them. Do not assume Actions automatically exports a
`GITHUB_TOKEN` environment variable. Keep token values out of logs.

## `run-myst.mjs`: optional compatibility launcher

`physicsOfMusic` retains a launcher for an unreliable nested `npm --version`
probe observed with MyST 1.10.1. It resolves npm's version from
`npm_config_user_agent` or `packageManager`, installs a temporary version-probe
shim, and invokes the local MyST executable. The current template and
`modernPhysics` invoke MyST directly; the launcher is not a fleet requirement.

Preserve it where the book documents that need. If the probe failure is
reproduced in a new environment, borrow the current launcher and its tests
from `physicsOfMusic` and cover all affected entry points, including export
scripts. Do not add it merely to fix a missing local CLI on `PATH`; the
reusable workflows already handle that case.
