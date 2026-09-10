---
name: quadrivium-attribution
description: How source attribution and licensing are documented for adapted vs. original QuadriviumPress books, and why content license is per-repo rather than inherited from .github. Read before adding a new book to the catalog or editing a README's license section.
---

# Source attribution and licensing

Unlike code repos, where a single org-wide LICENSE (in `QuadriviumPress/.github`) covers
everyone, **content license is per-repo** here, because each book adapts a different
upstream work under that work's own terms. Every book repo must ship one of:

- a root `LICENSE` (or `LICENSE.txt`) file, or
- a `## License` (or `## Source and license`) section in `README.md`

naming the license the *edition* is published under. `scripts/check-repo-compliance.sh`
fails a repo missing both.

## The three lineages

`structure/repos.json`'s `lineage` field records provenance:

- **`original`** -- wholly new QuadriviumPress work (`modernPhysics`, `opticsTextbook`,
  `college-physics-textbook`) or a substantial enough rewrite of an earlier open edition
  that it isn't a direct adaptation (`modern-classical-mechanics` explicitly credits and
  distinguishes itself from Danny Caballero's earlier notes). `source` is `null`.
- **`openstax-remix`** -- an Eleventy HTML build from raw OpenStax CNXML (see the
  `osbooks-*` upstream-reference repos, e.g. `osbooks-astronomy` feeds `astronomy`).
  `source.author` is `"OpenStax"`, `source.license` is OpenStax's
  Attribution-NonCommercial-ShareAlike terms.
- **`public-domain-adaptation`** -- a named author's openly licensed book, adapted into a
  QuadriviumPress edition (`thermodynamics` <- Olivier Cleynen, `mecmath-trigonometry` <-
  Michael Corral, `PrinciplesOfMechanics` <- Salma Alrasheed, ...). `source` names the
  author, title, and, where a canonical page or DOI exists, its URL.

## Filling in `source`

`source.url` and `source.license` are `null` in the catalog when not yet confirmed against
that repo's own README -- **don't guess a DOI, URL, or license string**; grep the target
repo's `README.md` for the actual text (most have a "Source and license" section citing a
DOI or a Creative Commons license link) and copy it verbatim, or leave the field `null`
until someone does. A wrong license claim is worse than a missing one.

## Per-chapter attribution (MyST books)

MyST books additionally carry a root `SOURCES.md` cataloging, chapter by chapter, any
embedded simulation and the attribution its supplier requires (see
[`quadrivium-myst-directives`](../quadrivium-myst-directives/SKILL.md)). This is separate
from the book-level content license and doesn't replace it.
