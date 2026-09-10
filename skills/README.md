# QuadriviumPress skills

Reference docs for AI assistants working in a QuadriviumPress book repo. Bundled as the
`quadrivium` Claude Code plugin (see [`../.claude-plugin/`](../.claude-plugin/)) so a member
repo loads them as a unit instead of vendoring copies.

| Skill | Covers |
|---|---|
| [`quadrivium-repo-structure`](quadrivium-repo-structure/SKILL.md) | The directory layout and files every book repo shares, by format (MyST / Eleventy / Jekyll) |
| [`quadrivium-myst-directives`](quadrivium-myst-directives/SKILL.md) | MyST admonitions, tabs, and the `{openphysics}` / `{phet}` / `{simulation}` embed directives |
| [`quadrivium-attribution`](quadrivium-attribution/SKILL.md) | How source attribution and licensing are documented for adapted vs. original works |

Add a new skill by copying [`TEMPLATE.md`](TEMPLATE.md).
