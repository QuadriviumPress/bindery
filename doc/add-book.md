# Adding a book to the catalog

1. **Add an entry to [`structure/repos.json`](../structure/repos.json)** following
   [`repos.schema.json`](../structure/repos.schema.json). At minimum: `name`, `displayName`,
   `type` (`book` or `bundle`), `isBook: true`, `lineage`, `source` (or `null` if original),
   `format`, `language`, `description`, `deployedUrl`, `subjectTopics`, `build`, `status`.
   Don't guess `source.url` / `source.license` -- grep the actual repo's README for a
   "Source and license" section and copy it verbatim, or leave `null`. See
   [`skills/quadrivium-attribution/SKILL.md`](../skills/quadrivium-attribution/SKILL.md).
2. **Validate**: `scripts/check-repos-catalog.sh`.
3. **Regenerate the landing page**: `scripts/generate-pages-index.sh` and commit the
   resulting `docs/index.html` (CI checks it's not stale --
   [`bindery-selfcheck.yml`](../.github/workflows/bindery-selfcheck.yml)).
4. **Wire the repo's own CI/deploy** to bindery's reusable workflows -- see
   [`CONVENTIONS.md`](../CONVENTIONS.md).
5. **Check compliance**: `scripts/check-repo-compliance.sh /path/to/the-repo`.
6. If the repo should be part of the local multi-repo workspace, `scripts/clone-fleet.sh
   --only <name>` picks it up automatically -- no separate registration needed, since
   `repos.json` is the only source of truth clone-fleet reads from.
