#!/usr/bin/env bash
# Validate structure/repos.json against structure/repos.schema.json, plus a
# few invariants a JSON Schema can't express on its own.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CATALOG="${1:-$ROOT_DIR/structure/repos.json}"
SCHEMA="$ROOT_DIR/structure/repos.schema.json"

for tool in jq python3; do
  command -v "$tool" >/dev/null 2>&1 || { echo "$tool is required" >&2; exit 1; }
done

if ! python3 -c "import jsonschema" >/dev/null 2>&1; then
  echo "python3 module 'jsonschema' is required (pip install jsonschema)" >&2
  exit 1
fi

echo "Validating $CATALOG against $SCHEMA"
python3 - "$SCHEMA" "$CATALOG" <<'PY'
import json, sys
import jsonschema

schema_path, catalog_path = sys.argv[1], sys.argv[2]
schema = json.load(open(schema_path))
catalog = json.load(open(catalog_path))
jsonschema.validate(catalog, schema)
print(f"Schema OK -- {len(catalog['repos'])} repos")
PY

echo "Checking invariants..."
fail=0

# name is unique
dupes="$(jq -r '.repos[].name' "$CATALOG" | sort | uniq -d)"
if [[ -n "$dupes" ]]; then
  echo "FAIL: duplicate repo name(s):" >&2
  echo "$dupes" >&2
  fail=1
fi

# repos.json entries are sorted by type then name is NOT required; skip.

# every deployedUrl for an active book resolves to a real host (best-effort:
# non-null and starts with https:// or http://)
bad_urls="$(jq -r '
  .repos[]
  | select(.status == "active" and .isBook == true and .deployedUrl != null)
  | select((.deployedUrl | test("^https?://")) | not)
  | .name
' "$CATALOG")"
if [[ -n "$bad_urls" ]]; then
  echo "FAIL: active book(s) with a malformed deployedUrl:" >&2
  echo "$bad_urls" >&2
  fail=1
fi

# every active book declares a build recipe (needed by fleet-health / deploy)
missing_build="$(jq -r '
  .repos[]
  | select(.status == "active" and .isBook == true and (.build == null))
  | .name
' "$CATALOG")"
if [[ -n "$missing_build" ]]; then
  echo "FAIL: active book(s) missing a build recipe:" >&2
  echo "$missing_build" >&2
  fail=1
fi

if [[ $fail -ne 0 ]]; then
  exit 1
fi

echo "All invariants OK."
