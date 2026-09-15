#!/usr/bin/env bash
# List QuadriviumPress repositories from structure/repos.json.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'EOF'
Usage: list-repos.sh [options]

Options:
  --book             Only book/bundle repositories
  --no-book          Only non-book repositories (tool|config|site)
  --type TYPE        Filter by repos.json type field
  --status STATUS    Filter by status (active|draft|wip|archived|template)
  --lineage LINEAGE  Filter by lineage (original|openstax-remix|public-domain-adaptation)
  --format FORMAT    Filter by build format (myst|eleventy|jupyter-book|static-html)
  --json             Output JSON
  --names            Output names only (one per line)
  --paths            Output local workspace paths
  --require-local    With --paths, only existing directories
  --summary          Print catalog summary
  -h, --help         Show this help

Examples:
  list-repos.sh --book --names
  list-repos.sh --json
  list-repos.sh --paths --book --require-local
EOF
}

ARGS=()
FORMAT="text"
COMMAND="list"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --book|--no-book)
      ARGS+=("$1")
      shift
      ;;
    --type|--status|--lineage|--format)
      ARGS+=("$1" "${2:?Missing value for $1}")
      shift 2
      ;;
    --json)
      FORMAT="json"
      shift
      ;;
    --names)
      FORMAT="names"
      shift
      ;;
    --paths)
      COMMAND="paths"
      shift
      ;;
    --require-local)
      ARGS+=("--require-local")
      shift
      ;;
    --summary)
      COMMAND="summary"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$COMMAND" == "summary" ]]; then
  exec "$SCRIPT_DIR/parse-repos.sh" summary "${ARGS[@]}"
fi

if [[ "$COMMAND" == "paths" ]]; then
  exec "$SCRIPT_DIR/parse-repos.sh" paths "${ARGS[@]}"
fi

exec "$SCRIPT_DIR/parse-repos.sh" list --format-out "$FORMAT" "${ARGS[@]}"
