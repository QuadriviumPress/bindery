#!/usr/bin/env bash
# Launcher for a long-running Codex proofread inside tmux.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BINDERY="$ROOT/bindery"
LOG="${PROOFREAD_TMUX_LOG:-$ROOT/.proofread/tmux.log}"

mkdir -p "$(dirname "$LOG")"
export PYTHONUNBUFFERED=1
export QUADRIVIUM_WORKSPACE="$ROOT"

cd "$BINDERY"
{
  echo "[qp-proofread starting $(date -Is)]"
  echo "workspace=$ROOT log=$LOG"
  ./scripts/codex-proofread.sh status || true
  echo "----"
  ./scripts/codex-proofread.sh run
  echo "[qp-proofread exited $? at $(date -Is)]"
} 2>&1 | tee -a "$LOG"

exec bash
