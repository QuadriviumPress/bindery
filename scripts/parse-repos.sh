#!/usr/bin/env bash
# Query structure/repos.json. list-repos.sh is the friendly CLI front-end for
# this; other scripts (clone-fleet, check-repo-compliance, generate-pages-index)
# source scripts/lib/repos.sh directly.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/repos.sh
source "$SCRIPT_DIR/lib/repos.sh"

usage() {
  cat <<'EOF'
Usage: parse-repos.sh <command> [filters] [options]

Commands:
  list           Print matching repos (default format: text, one per line)
  names          Print matching repo names, one per line
  paths          Print local workspace paths for matching repos
  get NAME       Print the full catalog entry for one repo, as JSON
  summary        Print a catalog summary

Filters:
  --book              Only book/bundle repositories (isBook == true)
  --no-book           Only non-book repositories
  --type TYPE         Filter by type (book|bundle|tool|config|site)
  --status STATUS     Filter by status (active|draft|wip|archived|template)
  --lineage LINEAGE   Filter by lineage (original|openstax-remix|public-domain-adaptation)
  --format FORMAT     Filter by build format (myst|eleventy|jupyter-book|static-html)
  --catalog PATH      Override path to repos.json

Options (list):
  --format-out text|json|names   Output format (default: text)

Options (paths):
  --require-local     Only print paths that exist on disk
EOF
}

[[ $# -ge 1 ]] || { usage >&2; exit 2; }
COMMAND="$1"; shift

repos_reset_filters
OUT_FORMAT="text"
GET_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --book) FILTER_BOOK=true; shift ;;
    --no-book) FILTER_BOOK=false; shift ;;
    --type) FILTER_TYPE="${2:?Missing value for --type}"; shift 2 ;;
    --status) FILTER_STATUS="${2:?Missing value for --status}"; shift 2 ;;
    --lineage) FILTER_LINEAGE="${2:?Missing value for --lineage}"; shift 2 ;;
    --format) FILTER_FORMAT="${2:?Missing value for --format}"; shift 2 ;;
    --catalog) REPOS_JSON="${2:?Missing value for --catalog}"; shift 2 ;;
    --format-out) OUT_FORMAT="${2:?Missing value for --format-out}"; shift 2 ;;
    --require-local) REQUIRE_LOCAL=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      if [[ "$COMMAND" == "get" && -z "$GET_NAME" ]]; then
        GET_NAME="$1"; shift
      else
        echo "Unknown argument: $1" >&2; usage >&2; exit 2
      fi
      ;;
  esac
done

case "$COMMAND" in
  names)
    repos_names
    ;;
  paths)
    repos_paths
    ;;
  get)
    [[ -n "$GET_NAME" ]] || { echo "get requires a repo name" >&2; exit 2; }
    repos_get "$GET_NAME"
    ;;
  summary)
    repos_summary
    ;;
  list)
    case "$OUT_FORMAT" in
      json) repos_list_json ;;
      names) repos_names ;;
      text)
        repos_filtered_json_lines | repos_add_local_exists | jq -r '
          "\(.name)\t\(.type)\t\(.status)\t\(.format // "-")\t\(.displayName)"
        ' | column -t -s $'\t'
        ;;
      *) echo "Unknown --format-out: $OUT_FORMAT" >&2; exit 2 ;;
    esac
    ;;
  *)
    echo "Unknown command: $COMMAND" >&2
    usage >&2
    exit 2
    ;;
esac
