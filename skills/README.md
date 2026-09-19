# QuadriviumPress skills

Reference docs for AI assistants working in a QuadriviumPress book repo. Bundled as the
`quadrivium` Claude Code plugin (see [`../.claude-plugin/`](../.claude-plugin/)) so a member
repo loads them as a unit instead of vendoring copies.

| Skill | Covers |
|---|---|
| [`quadrivium-repo-structure`](quadrivium-repo-structure/SKILL.md) | The directory layout and files every book repo shares, by format (MyST / Eleventy) |
| [`quadrivium-myst-directives`](quadrivium-myst-directives/SKILL.md) | MyST admonitions, tabs, and the `{openphysics}` / `{phet}` / `{simulation}` embed directives |
| [`quadrivium-attribution`](quadrivium-attribution/SKILL.md) | How source attribution and licensing are documented for adapted vs. original works |
| [`quadrivium-media-plugins`](quadrivium-media-plugins/SKILL.md) | The `{animation}` / `{audio}` / `{video}` / `{h5p}` plugin family: iframe-plus-fallback architecture, the `BASE_URL` gotcha, adding an animation or embedding a video |
| [`quadrivium-h5p-activities`](quadrivium-h5p-activities/SKILL.md) | Setting up and authoring self-hosted H5P chapter-review questions, and their PDF/print fallback text |
| [`quadrivium-build-scripts`](quadrivium-build-scripts/SKILL.md) | Vendoring `scripts/fetch-exports.sh` and `scripts/run-myst.mjs` without re-hitting their known bugs |
| [`quadrivium-print-exports`](quadrivium-print-exports/SKILL.md) | Generating PDF and DOCX editions from the same MyST chapter source: `export.mjs`, the jtex LaTeX template, the pandoc DOCX pipeline, and where each build runs in CI |

Add a new skill by copying [`TEMPLATE.md`](TEMPLATE.md).
