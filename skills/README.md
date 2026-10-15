# QuadriviumPress skills

Reference docs for AI assistants working in a QuadriviumPress book repo. Bundled as the
`quadrivium` Claude Code plugin (see [`../.claude-plugin/`](../.claude-plugin/)) so a member
repo loads them as a unit instead of vendoring copies.

| Skill | Covers |
|---|---|
| [`quadrivium-repo-structure`](quadrivium-repo-structure/SKILL.md) | The directory layout and files every book repo shares, by format (MyST / Eleventy) |
| [`quadrivium-myst-presentation`](quadrivium-myst-presentation/SKILL.md) | Exercise, callout, and label conventions for MyST chapters |
| [`quadrivium-myst-directives`](quadrivium-myst-directives/SKILL.md) | Tabs and the `{openlyceum}` / `{phet}` / `{simulation}` embed directives |
| [`quadrivium-attribution`](quadrivium-attribution/SKILL.md) | How source attribution and licensing are documented for adapted vs. original works |
| [`quadrivium-media-plugins`](quadrivium-media-plugins/SKILL.md) | The `{animation}` / `{audio}` / `{video}` / `{h5p}` plugin family: iframe-plus-fallback architecture, the `BASE_URL` gotcha, adding an animation or embedding a video |
| [`quadrivium-h5p-activities`](quadrivium-h5p-activities/SKILL.md) | Setting up and authoring self-hosted H5P chapter-review questions, and their PDF/print fallback text |
| [`quadrivium-build-scripts`](quadrivium-build-scripts/SKILL.md) | MyST command baseline, reusable CI/deploy permissions and toolchains, export fetching, and optional launchers |
| [`quadrivium-print-exports`](quadrivium-print-exports/SKILL.md) | Generating PDF and DOCX editions from the same MyST chapter source: `export.mjs`, the jtex LaTeX template, the pandoc DOCX pipeline, and where each build runs in CI |

| [`quadrivium-pwa`](quadrivium-pwa/SKILL.md) | Offline setup, deployment paths, cache isolation between books, and fresh content for returning readers |
| [`quadrivium-editorial-review`](quadrivium-editorial-review/SKILL.md) | Proofreading queue, source-aware editorial corrections, figure descriptions, and review evidence |

Add a new skill by copying [`TEMPLATE.md`](TEMPLATE.md).
