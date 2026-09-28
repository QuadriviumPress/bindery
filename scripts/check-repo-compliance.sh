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

project_has_key() {
  local key="$1"
  awk -v key="$key" '
    /^project:[[:space:]]*$/ { in_project = 1; next }
    in_project && /^[^[:space:]#]/ { exit }
    in_project && $0 ~ "^  " key ":" { found = 1; exit }
    END { exit(found ? 0 : 1) }
  ' "$REPO_PATH/myst.yml"
}

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
      if grep -q 'actions:[[:space:]]*read' "$REPO_PATH/.github/workflows/deploy.yml" 2>/dev/null; then
        pass "deploy.yml grants actions:read for bindery reusable deploy"
      else
        fail "deploy.yml must grant actions: read (bindery deploy requests it; otherwise startup fails)"
      fi
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
    [[ -f "$REPO_PATH/SOURCES.md" ]] \
      && pass "SOURCES.md records provenance and component attribution" \
      || fail "MyST book must include SOURCES.md"

    if [[ -f "$REPO_PATH/myst.yml" ]]; then
      for key in title short_title description authors license github keywords toc; do
        if project_has_key "$key"; then
          pass "myst.yml declares project.$key"
        else
          fail "myst.yml is missing project.$key"
        fi
      done
      if project_has_key open_access \
         && awk '
              /^project:[[:space:]]*$/ { in_project = 1; next }
              in_project && /^[^[:space:]#]/ { exit }
              in_project && /^  open_access:[[:space:]]+true([[:space:]]*#.*)?$/ { found = 1; exit }
              END { exit(found ? 0 : 1) }
            ' "$REPO_PATH/myst.yml"; then
        pass "myst.yml declares project.open_access: true"
      else
        fail "myst.yml must declare project.open_access: true"
      fi
    fi
    ;;
  eleventy)
    [[ -f "$REPO_PATH/eleventy.config.js" ]] && pass "eleventy.config.js present" || fail "format is eleventy but eleventy.config.js is missing"
    ;;
esac

# Node engines pin, when the repo is Node-based
if [[ -f "$REPO_PATH/package.json" ]]; then
  node_range="$(jq -r '.engines.node // ""' "$REPO_PATH/package.json")"
  if [[ "$node_range" == ">=22" || "$node_range" == "22.x" ]]; then
    pass "package.json declares the Node 22 fleet floor"
  elif [[ -n "$node_range" ]]; then
    warn "package.json engines.node is '$node_range' (fleet standard: >=22 or 22.x)"
  else
    warn "package.json has no engines.node pin (fleet standard: >=22)"
  fi

  if [[ "$FORMAT" == "myst" ]]; then
    if node -e '
      const fs = require("fs");
      const pkg = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
      const required = ["name","version","private","description","license","packageManager","engines","scripts","devDependencies"];
      const optional = ["dependencies","keywords","repository","bugs","homepage","overrides"];
      const keys = Object.keys(pkg);
      const errors = [];
      if (keys.slice(0, required.length).join() !== required.join()) {
        errors.push("top-level keys must start with " + required.join(", ") + " (found " + keys.join(", ") + ")");
      }
      const rest = keys.slice(required.length);
      const allowedRest = optional.filter((key) => rest.includes(key));
      if (rest.join() !== allowedRest.join()) {
        errors.push("optional keys must follow in this order only: " + optional.join(", ") + " (found " + (rest.join(", ") || "none") + ")");
      }
      if (pkg.private !== true) errors.push("private must be true");
      if (pkg.packageManager !== "npm@10.9.8") errors.push("packageManager must be npm@10.9.8");
      if (!pkg.engines || pkg.engines.node !== ">=22" || pkg.engines.npm !== ">=10 <11") {
        errors.push("engines must be node >=22 and npm >=10 <11");
      }
      if (!pkg.devDependencies || pkg.devDependencies.mystmd !== "1.11.0") {
        errors.push("devDependencies.mystmd must be exactly 1.11.0");
      }
      if (pkg.dependencies && Object.prototype.hasOwnProperty.call(pkg.dependencies, "mystmd")) {
        errors.push("mystmd must not be listed under dependencies");
      }
      for (const script of ["start", "build", "verify", "check"]) {
        if (typeof pkg.scripts?.[script] !== "string" || pkg.scripts[script].length === 0) {
          errors.push("scripts." + script + " must be a non-empty string");
        }
      }
      const check = pkg.scripts?.check || "";
      if (!check.includes("--strict") || !check.includes("--check-links")) {
        errors.push("scripts.check must include --strict and --check-links");
      }
      if (errors.length) {
        console.error(errors.join("\n"));
        process.exit(1);
      }
    ' "$REPO_PATH/package.json"; then
      pass "package.json matches the MyST baseline"
    else
      fail "package.json does not match doc/myst-baseline.md"
    fi
    [[ -f "$REPO_PATH/package-lock.json" ]] \
      && pass "package-lock.json present" \
      || fail "MyST repo must commit package-lock.json"
    if [[ -f "$REPO_PATH/AGENTS.md" ]] \
       && grep -q '^## Intentional differences' "$REPO_PATH/AGENTS.md" \
       && grep -q '^## Presentation gap' "$REPO_PATH/AGENTS.md"; then
      pass "AGENTS.md records differences and the presentation gap"
    else
      fail "MyST repo must have AGENTS.md with Intentional differences and Presentation gap sections"
    fi
  fi
fi

if [[ -f "$REPO_PATH/package.json" ]]; then
  [[ -f "$REPO_PATH/.github/dependabot.yml" ]] \
    && pass "Dependabot configuration present" \
    || warn "Node-based repo has no .github/dependabot.yml"
fi

echo "----"
echo "$REPO_NAME: $fails failure(s), $warns warning(s)"
[[ $fails -eq 0 ]]
