#!/usr/bin/env bash
# Codex proofreading across the QuadriviumPress fleet.
# See ../doc/codex-proofread.md
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export QUADRIVIUM_WORKSPACE="${QUADRIVIUM_WORKSPACE:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
export REPOS_JSON="${REPOS_JSON:-$SCRIPT_DIR/../structure/repos.json}"

exec python3 "$SCRIPT_DIR/lib/proofread.py" "$@"
