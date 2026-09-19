---
name: quadrivium-media-plugins
description: How locally-authored MyST media directives ({animation}, {audio}, {video}, {h5p}) are built -- the shared iframe-plus-fallback architecture, the BASE_URL/SITE_ROOT gotcha, and how to add a new looping animation or embed a curated video. Read before writing a new plugins/*.mjs directive or debugging a broken embed on Pages.
---

# Locally-authored media plugins

`{simulation}` / `{openphysics}` / `{phet}` (see
[`quadrivium-myst-directives`](../quadrivium-myst-directives/SKILL.md)) embed *someone else's*
interactive content. `{animation}`, `{audio}`, `{video}`, and `{h5p}` are the sibling family for
media the book itself owns or curates -- a locally authored looping figure, a synthesized audio
clip, a curated YouTube/Vimeo explainer, a self-hosted H5P question (see
[`quadrivium-h5p-activities`](../quadrivium-h5p-activities/SKILL.md) for that one specifically).
Real implementations: `modernPhysics/plugins/{animation,video,h5p}.mjs`,
`physicsOfMusic/plugins/{animation,audio,h5p}.mjs`.

## The iframe-plus-fallback shape

MyST's `iframe` node is rendered by the website theme and nothing else -- PDF (tex/typst),
DOCX, and plain Markdown output have no iframe support at all. Every directive in this family
therefore emits an `iframe` **and** a plain `image` as sibling children of one `figure`, and lets
CSS/the export pipeline pick one:

| Output | What survives |
|---|---|
| HTML site | the live iframe; `plugins/simulation.css` hides the fallback image |
| Printed web page | CSS flips it: iframe hidden, fallback image shown |
| PDF (tex/typst) | `plugins/export.mjs` drops the iframe node; `\includegraphics`/`#image` of the fallback |
| DOCX | iframe unsupported; the fallback image lands |
| Markdown export | the fallback becomes the `{figure}` argument |

A directive's fallback is not optional decoration -- it's what most export formats actually
ship. `{animation}` falls back to an existing static SVG (`:figure:`, or `images/<id>.svg` by
convention); `{video}` falls back to a poster image derived from the video id (YouTube) or
supplied explicitly (`:poster:`, required for Vimeo, since its thumbnail needs a network oEmbed
call the build can't make); `{h5p}` falls back to the question text itself (see
`quadrivium-h5p-activities`).

## BASE_URL / SITE_ROOT

Every directive in this family serves its assets from a `/`-rooted path (`/animations/...`,
`/audio/...`, `.generated/h5p` published at `/h5p/...`) because MyST resolves a `/`-prefixed
`image`/`iframe` URL against the *project root*, not the source file's directory, and a plugin
has no way to know which chapter file it was called from. But a project-Pages site isn't served
at the domain root -- it's at `https://quadriviumpress.com/<repoName>/` -- so every plugin
computes its root from `BASE_URL`, which bindery's reusable `ci.yml`/`deploy.yml` set to
`/${{ github.event.repository.name }}` for the whole job:

```js
const rawBaseUrl = process.env.BASE_URL || '/';
const SITE_ROOT = rawBaseUrl === '/'
  ? ''
  : `/${ rawBaseUrl.replace( /^\/+|\/+$/g, '' ) }`;
const ANIMATION_ROOT = `${ SITE_ROOT }/animations`;
```

Copy this pattern verbatim for a new plugin rather than inventing another way to join the base
path -- it's identical across `animation.mjs`, `audio.mjs`, and `h5p.mjs` in both `modernPhysics`
and `physicsOfMusic` today.

**The gotcha that broke every one of these plugins at least once:** the constant is computed
*once, at module import time*. Bindery's `verify`/`check` pre-build step runs with
`BASE_URL=/<repo>` already set (the same job env as the real deploy), so a test file that just
`import`s the plugin and asserts root-relative URLs (`/audio/...`) passes locally and fails on
every push to main -- it silently imported the plugin *after* BASE_URL was already poisoned by
whatever ran first in the same test process. Fix, used consistently across
`tests/{audio,h5p-plugin,media-plugins}.test.mjs`:

```js
// Bindery sets BASE_URL for deploy/CI. Load the default cases with it cleared,
// and add a case that re-imports with the deployment base path set -- the
// behaviour that broke was untested.
const savedBaseUrl = process.env.BASE_URL;
delete process.env.BASE_URL;
// ... import/require the plugin fresh, assert root-relative URLs ...
if (savedBaseUrl === undefined) delete process.env.BASE_URL;
else process.env.BASE_URL = savedBaseUrl;
```

Then add a second test that sets `process.env.BASE_URL = '/repoName'` before a fresh import and
asserts the prefixed form -- that's the actual deploy-time behavior, and it's the case that was
untested when this broke.

## Adding an animation

1. Author the looping figure as a standalone HTML page under `animations/<id>.html` (canvas or
   SVG, no external deps beyond what the page inlines).
2. Provide a static fallback: an existing chapter SVG, or a new one under `images/`.
3. Embed it:

   ````markdown
   ```{animation} ch05-building-a-sawtooth
   :figure: /images/ch07-fourier-synthesis.svg
   :label: fig:ch07-fourier-synthesis
   :alt: Successively larger sums of sinusoidal harmonics approach a sharply localized sawtooth waveform.

   Caption prose here -- this is the figure caption in every output, not just a description of
   the animation.
   ```
   ````
4. The theme's default iframe aspect ratio (~16:10) fits most figures; a wider single-panel plot
   needs a matching rule added to `plugins/simulation.css`, same as `{simulation}`.

## Embedding a video

```{video} https://www.youtube.com/watch?v=pTn6Ewhb27k
:video-title: Why No One Has Measured The Speed Of Light
:label: fig:ch01-speed-of-light-video
:alt: An explainer walks through one-way versus two-way light-speed measurements and the role of clock synchronization.

Caption prose connecting the video to the surrounding section -- not a restatement of the title.
```

- YouTube and Vimeo only (`youtube.com`, `youtu.be`, `*.youtube-nocookie.com`, `vimeo.com`,
  `player.vimeo.com`); the website embed uses the privacy-conscious `-nocookie` player.
- YouTube's poster is derived from the video id automatically. Vimeo has no stable
  thumbnail-by-id URL, so its directive **requires** an explicit `:poster:`.
- Before adding a video, verify the credited channel against YouTube's oEmbed API
  (`author_name`), not a search-engine summary -- `modernPhysics` shipped several confidently
  wrong attributions from summary-only sourcing (see 66ad270, "Fix video attributions found
  wrong after oEmbed verification") before this became the rule. Record every embedded video in
  `SOURCES.md`'s video table: chapter, title, publisher, URL.
- `:label:`/`:alt:` are required for cross-referencing and accessibility, same as any other
  figure directive in the fleet.

## Borrowing this for a new book

Nothing here lives in `opiniatedMystmdBookTemplate` or in bindery itself -- these are
per-repo plugin files, copied peer-to-peer the way AGENTS.md's fleet guide expects, not pulled
in from a shared package. To add one directive to a new or existing book:

1. Copy the single file for the directive you want from the nearest peer -- `plugins/video.mjs`
   has no dependencies beyond the directive itself and is the cheapest to add in isolation;
   `plugins/animation.mjs`/`audio.mjs`/`h5p.mjs` each expect a matching content directory
   (`animations/`, `audio/`, `h5p/` respectively) to exist too, so bring the directory layout,
   not just the `.mjs`.
2. Register it in `myst.yml`'s `plugins:` list (see the comments already there in `modernPhysics`
   or `physicsOfMusic` for the one-line description convention).
3. If the plugin serves static assets, add the matching entry to `myst.yml`'s
   `project.static_files` (e.g. `animations/`, `audio/`) so the build copies them unhashed.
4. Copy the plugin's `tests/*.test.mjs` alongside it -- particularly the BASE_URL reset pattern
   above -- rather than writing a fresh test file from scratch; that pattern is exactly what
   both source repos got wrong the first time.
5. If the book also builds PDF/DOCX exports (see
   [`quadrivium-print-exports`](../quadrivium-print-exports/SKILL.md)), confirm `plugins/export.mjs`
   already handles this directive's `iframe` node -- it does for all four covered here, but a
   sixth locally-authored directive would need the same treatment added.

Don't copy all four directives into a book that doesn't need them: `{h5p}` in particular pulls in
a large vendored library tree (see
[`quadrivium-h5p-activities`](../quadrivium-h5p-activities/SKILL.md)) that's dead weight without
real questions behind it.
