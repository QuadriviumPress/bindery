# Codex textbook proofreading

Spelling/grammar pass over QuadriviumPress books using local `codex exec` as a
single-file worker (not a burst of Codex subagents).

## Why this shape

- ~2k content files across the fleet. The runner works the queue back to back.
- There is **no daily active-time cap** unless you set `--daily-budget`.
- Jobs run **one at a time**, with at most a **5 second** jitter between them.
- A failed job, including a usage-limit response, is recorded and the queue
  continues. The session stops only after eight failures in a row.
- Nested Codex subagents are disabled (`agents.enabled=false`) so each job cannot
  fan out.
- Files are split at **64k characters**, so large chapters are fewer Codex calls.
- Queue + reports live under the fleet checkout (default
  `$QUADRIVIUM_WORKSPACE/.proofread/`) and are **resumable**.

## Quick start

```bash
cd /home/veillette/QuadriviumPress/bindery

# 1) Install the custom Codex agent once
./scripts/codex-proofread.sh install-agent

# 2) Build the queue (skips osbooks-* by default)
./scripts/codex-proofread.sh init

# Optional: one book first
./scripts/codex-proofread.sh init --repo physicsOfWaves

# 3) See remaining budget / pending work
./scripts/codex-proofread.sh status

# 4) Run the queue (report-only, default)
./scripts/codex-proofread.sh run

# Smoke-test one job without calling Codex
./scripts/codex-proofread.sh run --dry-run --max-jobs 1
```

Leave `run` going in a dedicated terminal / tmux session. It keeps going until
the queue is empty. Re-run `init` after changing `--chunk-chars`; an existing
queue keeps its previous chunk boundaries until then.

## Modes

| Mode | Sandbox | Behavior |
| --- | --- | --- |
| `report` (default) | `read-only` | JSON findings only; no edits |
| `fix` | `workspace-write` + `--approve-for-me` | High-confidence spelling/typo edits only |

```bash
./scripts/codex-proofread.sh --mode fix run --repo physicsOfWaves --max-jobs 3
```

Review diffs in the target repo before committing — this tool never commits or pushes.

The proofreader uses medium reasoning effort and makes separate word-level and
sentence-level passes. Report mode includes both high- and medium-confidence
candidates (with an explanation for medium-confidence items); fix mode still edits
only high-confidence issues.

## Pacing knobs

| Flag / env | Default | Meaning |
| --- | --- | --- |
| `--daily-budget` / `PROOFREAD_DAILY_BUDGET` | `0` (no cap) | Active Codex time per day. `0` disables the cap |
| `--delay-min` / `PROOFREAD_DELAY_MIN` | `0` | Min sleep between jobs |
| `--delay-max` / `PROOFREAD_DELAY_MAX` | `5s` | Max sleep between jobs |
| `--max-jobs` | unlimited | Cap jobs in this process |
| `--model` / `PROOFREAD_MODEL` | agent default (`gpt-5.6-terra`) | `codex -m` override |
| `--reasoning-effort` / `PROOFREAD_REASONING_EFFORT` | `medium` | Codex reasoning depth (`low`, `medium`, `high`, or `xhigh`) |
| `--chunk-chars` | `64000` | Split large files into chunks |
| `--state-dir` / `PROOFREAD_STATE_DIR` | `$QUADRIVIUM_WORKSPACE/.proofread` | Queue + reports |

Quieter pace, if a usage window needs headroom (still one-at-a-time):

```bash
./scripts/codex-proofread.sh \
  --daily-budget 4h30m \
  --delay-min 8m \
  --delay-max 15m \
  run
```

## Outputs

```
.proofread/
  queue.json           # resumable job list
  budget.json          # per-day active seconds
  reports/<repo>/*.json
  runs/<job-id>.*      # last message, jsonl, stderr
```

## Suggested multi-day cadence

1. `init` once (re-run after large content imports; unchanged done jobs stay done).
2. Start with a small MyST book (`--repo physicsOfWaves`) in `report` mode; skim reports.
3. Broaden to more repos once findings look trustworthy.
4. Only then use `--mode fix` on a short leash (`--max-jobs 5`) and review `git diff`.
5. A rate-limit or other Codex failure is recorded as `error` and the queue
   continues. The runner stops after eight failures in a row. Diagnose the saved
   stderr, then rerun `init` to requeue failed jobs. Do not raise concurrency.

## What it does *not* do

- No PR creation, commits, or pushes.
- No parallel Codex workers / subagent swarms.
- No `osbooks-*` CNXML mirrors (HTML twins are the review target).
- No style rewrites — spelling / clear typos / broken grammar only.

## Content discovery

The queue reads files referenced by a MyST book's `myst.yml` table of contents,
then supplements them with conventional content roots such as `chapters/`,
`content/`, `tex/`, and `source/`. This includes unusual student-facing layouts
without sweeping in MyST material that the book deliberately excludes.

Repositories containing overlapping source editions may have a narrow explicit
source selection in `scripts/lib/proofread.py`. For example,
`differentialEquations` queues only the documented edition of record,
`trench-distro/TRENCH_DIFFEQ_BV.tex`.
