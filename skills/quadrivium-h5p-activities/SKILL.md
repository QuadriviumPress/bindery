---
name: quadrivium-h5p-activities
description: How self-hosted H5P chapter-review activities are set up and authored in QuadriviumPress MyST books -- directory layout, the generator script for hand-authored questions, and the PDF/print fallback text a question must carry. Read before adding or editing an {h5p} activity.
---

# H5P chapter reviews

Self-hosted, static-only H5P: no h5p.com account, no server, no database. A question is a
folder of JSON; `h5p-standalone` is the vendored client-side player; a build-time packager
resolves the dependency union so the shipped runtime only includes what the book's activities
actually use. Real implementations: `modernPhysics/h5p/`, `modernPhysics/scripts/{generate-h5p-quizzes,h5p-review-fallback}.mjs`,
and the equivalent tree in `physicsOfMusic`. The embedding directive itself
(`plugins/h5p.mjs`, the iframe-plus-fallback pattern, `BASE_URL`) is covered by
[`quadrivium-media-plugins`](../quadrivium-media-plugins/SKILL.md); this skill is about the
content side.

## Layout

```
h5p/
  embed.html       generic loader: reads ?id=<content-id> from its own URL
  player/           vendored h5p-standalone runtime
  libraries/        catalog of unpacked H5P content-type libraries (H5P.MultiChoice, H5P.DragText, ...)
  packages/         optional standard .h5p packages, named <content-id>.h5p
  content/<id>/
    h5p.json          content metadata: title, main library, preloadedDependencies
    content/content.json   the question text and answer choices
.generated/h5p/     build output; git-ignored, published at /h5p/... by myst.yml static_files
```

`npm run h5p:prepare` (`scripts/prepare-h5p.mjs`) reads every activity's declared dependencies,
follows them recursively through each library's `library.json`, and writes `.generated/h5p/` --
only the union of libraries the book's activities actually require, each library emitted once
regardless of how many activities use it. It runs in `prestart` and before build; a missing
dependency or duplicate content id fails the build rather than shipping a broken activity.

## Two ways to author an activity

1. **Packaged**: export a standard `.h5p` file from any H5P authoring tool, drop it at
   `h5p/packages/<id>.h5p`. The filename (minus `.h5p`) is the content id the `{h5p}` directive
   references. Good for content types more complex than the generator below covers.
2. **Hand-authored JSON**: `content/<id>/h5p.json` + `content/<id>/content/content.json`,
   convenient for small questions and readable diffs. `library.json` dependency declarations
   don't need to be flattened -- the packager follows them -- but every named library has to
   exist under `libraries/` or inside a `.h5p` package.

## The five-question chapter-review generator

Both `modernPhysics` and `physicsOfMusic` converged on the same convention: each chapter gets
one `{h5p}` review activity with exactly five questions, one of each type, generated from a
single source-of-truth script (`scripts/generate-h5p-quizzes.mjs`) rather than hand-edited JSON
per chapter. It exports small builder functions per content type --

```js
multiChoice( seed, question, choices, media )   // H5P.MultiChoice
trueFalse( seed, statement, isTrue )            // H5P.TrueFalse
dragText( seed, task, textField, distractors )  // H5P.DragText, *word* marks the blank
fillBlanks( seed, text, questions )             // H5P.Blanks
markTheWords( seed, task, textField )           // H5P.MarkTheWords, *word* marks a target
```

-- and a stable UUID is derived by hashing a per-question `seed` string (chapter + question
role), so regenerating the file doesn't spuriously rewrite every `subContentId` on an unrelated
edit. `npm run h5p:generate` writes the JSON; `npm run h5p:check` (part of `verify`) re-derives
it and diffs against what's committed, so hand-edits to a generated `content.json` are caught
rather than silently drifting from the generator. Edit the questions in the generator script,
not the generated JSON.

A question that references a chapter figure uses the generator's `image()` helper (names a file
under `images/`) rather than an inline data URI -- the writer copies the file into the activity
and adds the `H5P.Image` dependency automatically.

## The PDF/print fallback, and its Unicode-math gotcha

An H5P activity can't run in PDF, DOCX, or Markdown export -- the `{h5p}` directive's body is
that fallback (same mechanism as `{animation}`/`{video}`: see
[`quadrivium-media-plugins`](../quadrivium-media-plugins/SKILL.md)). For a chapter review, that
body is auto-generated too, by `scripts/h5p-review-fallback.mjs`'s `renderReview()` /
`replaceReview()`: it renders each of the five questions back to plain prose matching its H5P
type (`**Multiple choice.** ...`, `**True or false.** ...`, `**Drag the words.** ... (Terms:
...)`, etc.), including a spoken-out description of any referenced figure, since a PDF reader
can't hover an interactive image the way the website can.

**Known gotcha:** H5P question JSON is free to use Unicode math glyphs (`γ`, `π`, `−`, `²`,
`ℏ`) directly in strings -- the browser renders them as ordinary text. The book's PDF export
uses a Latin Modern font that does **not** cover most of that range, so those glyphs print as
tofu/missing-glyph boxes if they leak into the fallback text unconverted.
`h5p-review-fallback.mjs`'s `printMath()` walks the fallback string, treats `$...$`-delimited
spans as already-TeX, and converts stray Unicode math symbols elsewhere in the text to their TeX
macro (`γ` → `\gamma`, `−` → `-`, `²` → `^2`, ...) before the PDF template ever sees them. If you
add a new symbol to a question, check `printMath()`'s `symbols` map covers it, or the PDF
edition will silently ship a missing-glyph box where the HTML edition shows the character fine.

`replaceReview()` splices the freshly rendered fallback into the chapter file between the
`` :::{h5p} <id> `` fence and its closing `:::`, replacing whatever fallback text was there
before -- so, again, edit the generator/questions, not the chapter's fallback prose directly.

## Borrowing this for a new book

This is not in `opiniatedMystmdBookTemplate` and shouldn't default into it (see the size note in
[`quadrivium-media-plugins`](../quadrivium-media-plugins/SKILL.md)) -- bring it in wholesale from
`modernPhysics` or `physicsOfMusic` only when a book actually wants self-hosted quizzes:

1. Copy the whole `h5p/` tree (`embed.html`, `player/`, `libraries/`) and
   `plugins/h5p.mjs`/`plugins/simulation.css`'s H5P-specific rules from the closer peer in
   subject matter -- the vendored `libraries/` only needs to cover the content types you'll
   actually author (`H5P.MultiChoice`, `H5P.TrueFalse`, `H5P.DragText`, `H5P.Blanks`,
   `H5P.MarkTheWords` cover the five-question convention above; drop any you won't use to keep
   the vendored tree smaller than the source repo's).
2. Copy `scripts/prepare-h5p.mjs`, `scripts/generate-h5p-quizzes.mjs`, and
   `scripts/h5p-review-fallback.mjs`, then **replace the question content** in
   `generate-h5p-quizzes.mjs` with the new book's own chapters -- nothing else in that file is
   book-specific except the questions and chapter ids.
3. Wire `h5p:generate`, `h5p:check`, and `h5p:prepare` into `package.json`'s `scripts`
   (`prestart`/`prebuild` should run `h5p:prepare`; `verify` should run `h5p:check`), matching
   either source repo's `package.json`.
4. Add `.generated/h5p` to `.gitignore` and `project.static_files` in `myst.yml` (see
   [`quadrivium-media-plugins`](../quadrivium-media-plugins/SKILL.md) for the `BASE_URL` wiring
   `plugins/h5p.mjs` needs).
5. If the book also exports PDF/DOCX, confirm the copied `plugins/export.mjs` already rewrites
   the `{h5p}` directive's `iframe` node (both source repos' do) and re-run the PDF fallback
   Unicode-math check above against the new book's own symbols.
