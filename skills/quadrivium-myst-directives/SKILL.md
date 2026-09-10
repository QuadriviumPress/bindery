---
name: quadrivium-myst-directives
description: MyST admonitions, tabs, and the {openphysics}/{phet}/{phet-legacy}/{simulation} interactive-embed directives used across QuadriviumPress MyST books. Read before adding a sidebar, tab-set, or embedded simulation to a chapter.
---

# MyST directives in QuadriviumPress books

These are additive to chapter prose -- they don't replace or restructure the surrounding
text, headings, math, figures, or exercises.

## Admonitions

Standard MyST admonitions (`` ```{note} ``, `` ```{tip} ``, etc.) plus, where a chapter
genuinely has one, an extended/alternate derivation or a "for the curious" aside.

## Tabs

`` ```{tab-set} `` / `` ```{tab-item} `` -- only where the book genuinely presents more than
one approach (two solution methods, SI vs. natural units, non-relativistic vs. relativistic
limits). Not a substitute for normal prose structure.

## Interactive simulations

A chapter embeds a running browser simulation with `{openphysics}`, `{phet}`,
`{phet-legacy}`, or `{simulation}`, supplied by a repo's `plugins/simulation.mjs`:

````markdown
```{openphysics} InterferometryLab
:label: fig:ch04-interferometry-sim

Move a mirror and count fringes.
```
````

- `{openphysics}` embeds a sim from [OpenPhysics](https://github.com/OpenPhysics) by repo
  name.
- `{phet}` embeds a modern HTML5 [PhET](https://phet.colorado.edu) sim.
- `{phet-legacy}` reaches PhET's pre-HTML5 Java sims via CheerpJ -- slow to start and
  mouse-only; use only where no HTML5 equivalent exists.
- `{simulation}` embeds any URL that works in an iframe, for anything not from
  OpenPhysics or PhET.

On the website these render as a live embed. In a PDF, Word doc, exported Markdown, or
printed page -- none of which run JavaScript -- the same figure falls back to a screenshot
with its caption and a link to the running version; this fallback is handled by the plugin,
not by the chapter author.

Every chapter that has a matching sim should carry at least one; a book's `SOURCES.md` (see
[`quadrivium-attribution`](../quadrivium-attribution/SKILL.md)) lists which, chapter by
chapter, along with the attribution each supplier requires. See a book's own
`plugins/README.md` for the full directive option list.
