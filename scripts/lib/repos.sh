#!/usr/bin/env bash
# Shared helpers for reading structure/repos.json with jq.
set -euo pipefail

REPOS_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS_SCRIPT_DIR="${REPOS_SCRIPT_DIR:-$REPOS_LIB_DIR/..}"
REPOS_JSON="${REPOS_JSON:-$REPOS_SCRIPT_DIR/../structure/repos.json}"
QUADRIVIUM_WORKSPACE="${QUADRIVIUM_WORKSPACE:-$(cd "$REPOS_SCRIPT_DIR/../.." && pwd)}"

FILTER_TYPE=""
FILTER_STATUS=""
FILTER_BOOK=""
FILTER_LINEAGE=""
FILTER_FORMAT=""
FILTER_NAME=""
REQUIRE_LOCAL=0

repos_require_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    echo "jq is required (install with: sudo apt install jq)" >&2
    exit 1
  fi
}

repos_catalog_path() {
  local path="$REPOS_JSON"
  if [[ -d "$(dirname "$path")" ]]; then
    path="$(cd "$(dirname "$path")" && pwd)/$(basename "$path")"
  fi
  printf '%s\n' "$path"
}

repos_workspace_root() {
  printf '%s\n' "$QUADRIVIUM_WORKSPACE"
}

repos_reset_filters() {
  FILTER_TYPE=""
  FILTER_STATUS=""
  FILTER_BOOK=""
  FILTER_LINEAGE=""
  FILTER_FORMAT=""
  FILTER_NAME=""
  REQUIRE_LOCAL=0
}

repos_jq_select_expr() {
  local parts=()

  if [[ -n "$FILTER_NAME" ]]; then
    parts+=(".name == \"$FILTER_NAME\"")
  fi
  if [[ -n "$FILTER_TYPE" ]]; then
    parts+=(".type == \"$FILTER_TYPE\"")
  fi
  if [[ -n "$FILTER_STATUS" ]]; then
    parts+=(".status == \"$FILTER_STATUS\"")
  fi
  if [[ -n "$FILTER_BOOK" ]]; then
    parts+=(".isBook == $FILTER_BOOK")
  fi
  if [[ -n "$FILTER_LINEAGE" ]]; then
    parts+=(".lineage == \"$FILTER_LINEAGE\"")
  fi
  if [[ -n "$FILTER_FORMAT" ]]; then
    parts+=(".format == \"$FILTER_FORMAT\"")
  fi

  if [[ ${#parts[@]} -eq 0 ]]; then
    printf '.'
    return
  fi

  local expr="${parts[0]}"
  local part
  for part in "${parts[@]:1}"; do
    expr="$expr and $part"
  done
  printf 'select(%s)' "$expr"
}

repos_jq_homepage_def='
def gh_pages_url:
  if ((.deployedUrl // "") | length) > 0 then
    .deployedUrl
  elif .name == ".github" or .name == "bindery" or (.type == "tool") then
    null
  else
    "https://quadriviumpress.github.io/\(.name)"
  end;
'

repos_jq_enrich_program() {
  local select_expr
  select_expr="$(repos_jq_select_expr)"
  cat <<JQ
$repos_jq_homepage_def
.repos[]
| $select_expr
| . + {
    githubPagesUrl: gh_pages_url,
    localPath: (\$workspace + "/" + .name)
  }
JQ
}

repos_filtered_json_lines() {
  repos_require_jq
  jq -c --arg workspace "$(repos_workspace_root)" "$(repos_jq_enrich_program)" "$(repos_catalog_path)"
}

repos_add_local_exists() {
  local workspace
  workspace="$(repos_workspace_root)"
  while IFS= read -r repo; do
    local name path exists=false
    name="$(jq -r '.name' <<<"$repo")"
    path="$workspace/$name"
    if [[ -d "$path" ]]; then
      exists=true
    fi
    jq -c --argjson localExists "$exists" '. + {localExists: $localExists}' <<<"$repo"
  done
}

repos_filtered_json() {
  repos_filtered_json_lines | repos_add_local_exists | jq -s '.'
}

repos_names() {
  repos_filtered_json_lines | jq -r '.name'
}

repos_book_names() {
  local previous="$FILTER_BOOK"
  FILTER_BOOK="true"
  repos_names
  FILTER_BOOK="$previous"
}

repos_get() {
  local name="${1:?Repository name required}"
  FILTER_NAME="$name"
  local result
  result="$(repos_filtered_json_lines | repos_add_local_exists | head -n 1)"
  FILTER_NAME=""
  if [[ -z "$result" ]]; then
    echo "Repository not found: $name" >&2
    return 1
  fi
  jq '.' <<<"$result"
}

repos_list_json() {
  repos_filtered_json
}

repos_paths() {
  local workspace
  workspace="$(repos_workspace_root)"
  while IFS= read -r name; do
    local path="$workspace/$name"
    if [[ "$REQUIRE_LOCAL" -eq 1 && ! -d "$path" ]]; then
      continue
    fi
    printf '%s\n' "$path"
  done < <(repos_names)
}

repos_summary() {
  repos_require_jq
  local catalog workspace
  catalog="$(repos_catalog_path)"
  workspace="$(repos_workspace_root)"
  jq -r '
    "organization: \(.organization // "QuadriviumPress")",
    "schemaVersion: \(.schemaVersion // "unknown")",
    "total: \(.repos | length)",
    (.repos | group_by(.type) | map("  \(.[0].type): \(length)") | .[]),
    "workspaceRoot: '"$workspace"'",
    "catalog: '"$catalog"'"
  ' "$catalog"
}

repos_for_each() {
  local exit_code=0
  local command=("$@")
  if [[ ${#command[@]} -eq 0 ]]; then
    echo "for-each requires a command" >&2
    return 2
  fi

  while IFS= read -r repo; do
    local name homepage description repo_type status lineage format display_name local_path local_exists
    name="$(jq -r '.name' <<<"$repo")"
    homepage="$(jq -r '.githubPagesUrl // ""' <<<"$repo")"
    description="$(jq -r '.description // ""' <<<"$repo")"
    repo_type="$(jq -r '.type // ""' <<<"$repo")"
    status="$(jq -r '.status // ""' <<<"$repo")"
    lineage="$(jq -r '.lineage // ""' <<<"$repo")"
    format="$(jq -r '.format // ""' <<<"$repo")"
    display_name="$(jq -r '.displayName // .name' <<<"$repo")"
    local_path="$(jq -r '.localPath' <<<"$repo")"
    local_exists="$(jq -r '.localExists' <<<"$repo")"

    REPO_NAME="$name" \
    REPO_DISPLAY_NAME="$display_name" \
    REPO_TYPE="$repo_type" \
    REPO_STATUS="$status" \
    REPO_LINEAGE="$lineage" \
    REPO_FORMAT="$format" \
    REPO_DESCRIPTION="$description" \
    REPO_HOMEPAGE="$homepage" \
    REPO_PATH="$local_path" \
    REPO_LOCAL_EXISTS="$([[ "$local_exists" == "true" ]] && echo 1 || echo 0)" \
      "${command[@]}" || exit_code=$?
  done < <(repos_filtered_json_lines | repos_add_local_exists)

  return "$exit_code"
}
