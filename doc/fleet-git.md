# Fleet git commands

Run everyday git operations across **every QuadriviumPress repo checked out locally** — the sibling
clones that live beside `bindery` in the workspace (`pull all`, `push all`, `status all`, …).

## The short version

[`scripts/fleet`](../scripts/fleet) runs any git command across every local catalog checkout:

```bash
fleet push
fleet pull --ff-only
fleet status -s
fleet --book log -1 --oneline
```

Put it on your `PATH` once (symlink is enough if `~/.local/bin` is already there):

```bash
ln -sfn ~/QuadriviumPress/bindery/scripts/fleet ~/.local/bin/fleet
```

Or call it as `bindery/scripts/fleet …` / `scripts/fleet …` from the bindery directory.

> If you also use [OpenPhysics/Baton](https://github.com/OpenPhysics/Baton)'s `fleet`, only one
> symlink can own `~/.local/bin/fleet` at a time — re-point it when you switch orgs, or call the
> scripts by path.

These operate on your **local working trees**. A related tool covers a different job:

| You want to… | Use |
|---|---|
| Update / clone every catalog repo into the workspace | [`scripts/clone-fleet.sh --update`](../scripts/clone-fleet.sh) |
| Run an ad-hoc git command across your local checkouts | [`scripts/fleet`](../scripts/fleet) (below) |

---

## Filters

Same catalog filters as the rest of the tooling:

```bash
fleet --book status -s                # books/bundles only
fleet --lineage openstax-remix status -s
fleet --type tool branch -vv          # tools only
fleet --no-book fetch --all           # everything that isn't a book
fleet --format myst status -s
```

> Without a filter the list includes `bindery` and `.github` too. Add `--book` if you want to
> skip them.

---

## Common operations

**Status of all repos:**

```bash
fleet status -s
```

**Branch + dirty-count overview** — quick "where is everything" snapshot (custom format,
so use the building-block loop):

```bash
scripts/parse-repos.sh paths --require-local | while read -r p; do
  printf '%-24s %-28s %s dirty\n' "$(basename "$p")" \
    "$(git -C "$p" rev-parse --abbrev-ref HEAD)" \
    "$(git -C "$p" status --porcelain | wc -l)"
done
```

**Pull all** — prefer `clone-fleet.sh --update`: it fast-forwards every existing repo *and* clones
any catalog repo you're missing, in one pass:

```bash
scripts/clone-fleet.sh --update
```

Or, to pull only what's already on disk (no new clones):

```bash
fleet pull --ff-only
```

**Fetch all** (update remotes without touching working trees):

```bash
fleet fetch --all --prune
```

**Push all** — pushes the current branch of each repo. Pushing writes to remotes, so review with
`fleet status -s` first. `git push` is a no-op for repos with nothing to push:

```bash
fleet push
```

For a brand-new local branch, set the upstream the first time:

```bash
fleet push -u origin HEAD
```

**Create the same branch everywhere:**

```bash
fleet checkout -b chore/my-change
```

**Last commit per repo:**

```bash
fleet log -1 --oneline
```

---

## The building block

[`parse-repos.sh paths --require-local`](../scripts/parse-repos.sh) prints the on-disk path of
every catalog repo that actually exists in your workspace. `scripts/fleet` is a thin wrapper
around that; use the loop directly when you need something that isn't a plain `git` invocation:

```bash
scripts/parse-repos.sh paths --require-local | while read -r p; do
  printf '%-24s %-28s %s dirty\n' "$(basename "$p")" \
    "$(git -C "$p" rev-parse --abbrev-ref HEAD)" \
    "$(git -C "$p" status --porcelain | wc -l)"
done
```

---

## Notes

- **Read-only first.** `status`, `fetch`, and `log` change nothing — run them freely. `pull`,
  `push`, and `checkout` change state; eyeball a status overview before a bulk `push`.
- **`pull --ff-only`** refuses to create merge commits, so a repo with diverged local work fails
  loudly instead of silently merging. Resolve those repos by hand.
- **Non-zero exit if any repo fails.** `fleet` keeps going after a failure, then exits `1` if
  any repo's git command failed — scan the output for which ones.
- **Workspace location.** Scripts assume `bindery` sits beside the member repos. If your checkout
  differs, set `QUADRIVIUM_WORKSPACE` or pass `--catalog /path/to/repos.json`.
