#!/usr/bin/env bash
# Audit one QuadriviumPress book/tool checkout against the shared conventions
# in ../CONVENTIONS.md. FAILs are structural gaps every repo should already
# meet; WARNs are migration items (e.g. "not yet wired to bindery's reusable
# CI") that don't block the repo from working today.
#
# Usage: check-repo-compliance.sh /path/to/repo-checkout [--catalog PATH]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CATALOG="$ROOT_DIR/structure/repos.json"

REPO_PATH=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --catalog) CATALOG="${2:?Missing value for --catalog}"; shift 2 ;;
    -h|--help)
      echo "Usage: check-repo-compliance.sh /path/to/repo-checkout [--catalog PATH]"
      exit 0
      ;;
    *)
      if [[ -z "$REPO_PATH" ]]; then REPO_PATH="$1"; shift
      else echo "Unexpected argument: $1" >&2; exit 2; fi
      ;;
  esac
done

[[ -n "$REPO_PATH" ]] || { echo "Usage: check-repo-compliance.sh /path/to/repo-checkout" >&2; exit 2; }
[[ -d "$REPO_PATH" ]] || { echo "Not a directory: $REPO_PATH" >&2; exit 2; }
command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 1; }

REPO_NAME="$(basename "$REPO_PATH")"
ENTRY="$(jq -c --arg name "$REPO_NAME" '.repos[] | select(.name == $name)' "$CATALOG" 2>/dev/null || true)"

if [[ -z "$ENTRY" ]]; then
  echo "note: '$REPO_NAME' is not in structure/repos.json -- checking with defaults only"
  IS_BOOK="unknown"
  FORMAT="unknown"
  STATUS="unknown"
  DEPLOYED_URL=""
else
  IS_BOOK="$(jq -r '.isBook' <<<"$ENTRY")"
  FORMAT="$(jq -r '.format // "unknown"' <<<"$ENTRY")"
  STATUS="$(jq -r '.status' <<<"$ENTRY")"
  DEPLOYED_URL="$(jq -r '.deployedUrl // ""' <<<"$ENTRY")"
fi

fails=0
warns=0

fail() { echo "FAIL: $1"; fails=$((fails + 1)); }
warn() { echo "WARN: $1"; warns=$((warns + 1)); }
pass() { echo "  ok: $1"; }

echo "== $REPO_NAME (isBook=$IS_BOOK format=$FORMAT status=$STATUS) =="

# README
if [[ -f "$REPO_PATH/README.md" ]]; then
  if grep -q '^# ' "$REPO_PATH/README.md"; then
    pass "README.md has an H1 title"
  else
    warn "README.md has no top-level '# Title' heading"
  fi
else
  fail "README.md is missing"
fi

# Attribution / license travels with the content, since it varies per source
# work -- unlike code repos, this is NOT inherited from the org .github repo.
if [[ "$IS_BOOK" == "true" ]]; then
  if [[ -f "$REPO_PATH/LICENSE" || -f "$REPO_PATH/LICENSE.txt" ]] \
     || grep -qi 'license' "$REPO_PATH/README.md" 2>/dev/null; then
    pass "content license is documented (LICENSE file or README section)"
  else
    fail "no LICENSE file and no license section in README -- content provenance must be documented"
  fi
fi

# CI / deploy wiring to bindery's reusable workflows (migration, not a hard
# requirement -- a repo can have its own CI and still work).
if [[ -f "$REPO_PATH/.github/workflows/ci.yml" ]]; then
  if grep -q 'QuadriviumPress/bindery/.github/workflows/ci.yml' "$REPO_PATH/.github/workflows/ci.yml" 2>/dev/null; then
    pass "ci.yml calls bindery's reusable CI workflow"
  else
    warn "ci.yml does not call QuadriviumPress/bindery/.github/workflows/ci.yml -- not yet migrated"
  fi
else
  warn "no .github/workflows/ci.yml"
fi

if [[ "$STATUS" == "active" && -n "$DEPLOYED_URL" ]]; then
  if [[ -f "$REPO_PATH/.github/workflows/deploy.yml" ]]; then
    if grep -q 'QuadriviumPress/bindery/.github/workflows/deploy.yml' "$REPO_PATH/.github/workflows/deploy.yml" 2>/dev/null; then
      pass "deploy.yml calls bindery's reusable deploy workflow"
    else
      warn "deploy.yml does not call QuadriviumPress/bindery/.github/workflows/deploy.yml -- not yet migrated"
    fi
  else
    warn "deployedUrl is set but no .github/workflows/deploy.yml found"
  fi
fi

# Format-specific project file
case "$FORMAT" in
  myst)
    [[ -f "$REPO_PATH/myst.yml" ]] && pass "myst.yml present" || fail "format is myst but myst.yml is missing"
    ;;
  eleventy)
    [[ -f "$REPO_PATH/eleventy.config.js" ]] && pass "eleventy.config.js present" || fail "format is eleventy but eleventy.config.js is missing"
    ;;
  jekyll)
    [[ -f "$REPO_PATH/_config.yml" ]] && pass "_config.yml present" || fail "format is jekyll but _config.yml is missing"
    ;;
esac

# Node engines pin, when the repo is Node-based
if [[ -f "$REPO_PATH/package.json" ]]; then
  if jq -e '.engines.node' "$REPO_PATH/package.json" >/dev/null 2>&1; then
    pass "package.json declares engines.node"
  else
    warn "package.json has no engines.node pin (fleet standard: >=22)"
  fi
fi

echo "----"
echo "$REPO_NAME: $fails failure(s), $warns warning(s)"
[[ $fails -eq 0 ]]
