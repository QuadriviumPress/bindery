# Paced Codex textbook proofreading

Long-running, **below-radar** spelling/grammar pass over QuadriviumPress books using
local `codex exec` as a single-file worker (not a burst of Codex subagents).

## Why this shape

- ~2k content files across the fleet — a full pass is multi-day.
- Codex accounts often have a ~5h active usage window; this tool budgets **4h30m** of
  *active* `codex exec` time per calendar day (configurable).
- Jobs run **one at a time**, with an **8–15 minute jittered sleep** between them so
  request patterns stay quiet and 429s are less likely.
- Nested Codex subagents are disabled (`agents.enabled=false`) so each job cannot
  fan out and burn the daily limit.
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

# 4) Run a quiet session (report-only, default)
./scripts/codex-proofread.sh run

# Smoke-test one job without calling Codex
./scripts/codex-proofread.sh run --dry-run --max-jobs 1
```

Leave `run` going in a dedicated terminal / tmux session. When today's budget is
exhausted it exits cleanly; start it again tomorrow.

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
| `--daily-budget` / `PROOFREAD_DAILY_BUDGET` | `4h30m` | Active Codex time per day |
| `--delay-min` / `PROOFREAD_DELAY_MIN` | `8m` | Min sleep between jobs |
| `--delay-max` / `PROOFREAD_DELAY_MAX` | `15m` | Max sleep between jobs |
| `--max-jobs` | unlimited | Cap jobs in this process |
| `--model` / `PROOFREAD_MODEL` | agent default (`gpt-5.6-terra`) | `codex -m` override |
| `--reasoning-effort` / `PROOFREAD_REASONING_EFFORT` | `medium` | Codex reasoning depth (`low`, `medium`, `high`, or `xhigh`) |
| `--chunk-chars` | `24000` | Split large files into chunks |
| `--state-dir` / `PROOFREAD_STATE_DIR` | `$QUADRIVIUM_WORKSPACE/.proofread` | Queue + reports |

Example: denser but still under 5h (still one-at-a-time):

```bash
./scripts/codex-proofread.sh \
  --daily-budget 4h45m \
  --delay-min 3m \
  --delay-max 6m \
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
5. On rate-limit / usage signals the runner **exits** and leaves the job `pending` —
   wait and resume; do not raise concurrency.

## What it does *not* do

- No PR creation, commits, or pushes.
- No parallel Codex workers / subagent swarms.
- No `osbooks-*` CNXML mirrors (HTML twins are the review target).
- No style rewrites — spelling / clear typos / broken grammar only.
