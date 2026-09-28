# MyST baseline

Shared tooling and presentation contract for every QuadriviumPress MyST book.
Structural rules that apply to every repo still live in [`../CONVENTIONS.md`](../CONVENTIONS.md).
Start a new book from [`opiniatedMystmdBookTemplate`](https://github.com/QuadriviumPress/opiniatedMystmdBookTemplate),
then record any extra scripts in that book's `AGENTS.md`. The template is the
package.json implementation of this contract. Do not keep a second copy here.

`scripts/check-repo-compliance.sh` fails a MyST repo that drifts from the
tooling rules below.

## package.json

Top-level keys, always present and in this order:

1. `name`
2. `version` (`1.0.0` unless the book already publishes another version)
3. `private` (`true`)
4. `description`
5. `license` (SPDX id; the template uses `MIT` for starter code)
6. `packageManager` (`npm@10.9.8`)
7. `engines` (`node` `>=22`, `npm` `>=10 <11`)
8. `scripts`
9. `devDependencies`

Optional keys may follow, only in this order: `dependencies`, `keywords`,
`repository`, `bugs`, `homepage`, `overrides`. Name every optional key in
`AGENTS.md`.

`mystmd` is an exact `devDependencies` pin at `1.11.0`. When the book uses
them, `sharp` stays at `0.35.4` and `yaml` at `2.9.1`. DevDependency order is
`mystmd`, `sharp`, `yaml`, then any other packages alphabetically.

## Scripts

These four names exist in every book. Command bodies match the template unless
`AGENTS.md` explains why not.

- `start` — `myst start`
- `build` — `myst build --html && node scripts/setup-pwa.mjs` when the book has the PWA step
- `verify` — book-specific fast checks. Do not merge verifiers across books.
- `check` — `npm run verify && myst build --html --strict --check-links`

Key order inside `scripts`:

1. `check:toolchain`, then `h5p:*`
2. `prestart`, `start`, `prebuild`, `build`, `precheck`, `verify`, `check`
3. other `check:*`
4. `test`, then `test:*`
5. `build:exports`, `build:pdf`, `build:chapters`, `build:docx`
6. any other names, alphabetically

Capability scripts (H5P, print exports, executable notebooks, notation, audio,
optics validation) stay in the book that needs them and are listed under
**Intentional differences** in `AGENTS.md`.

## AGENTS.md

Every MyST book has a root `AGENTS.md` with these headings:

- **Standard** — links here and to the presentation skill
- **Commands** — `start`, `build`, `verify`, `check`, plus extra scripts
- **Intentional differences** — extra package.json keys, extra scripts, layout, verifier, missing PWA
- **Presentation gap** — how exercises and callouts are marked up today

## Presentation

New chapters follow [`../skills/quadrivium-myst-presentation/SKILL.md`](../skills/quadrivium-myst-presentation/SKILL.md).
The template sample chapters are the copy to imitate. Existing textbooks are
not rewritten to that markup in the tooling pass; each book's **Presentation
gap** section says what still differs and why.
