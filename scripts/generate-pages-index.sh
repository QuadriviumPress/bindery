#!/usr/bin/env bash
# Regenerate docs/index.html (the QuadriviumPress book index published to
# GitHub Pages) from structure/repos.json. Static output -- no client-side
# fetch, no build step required to view it.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CATALOG="${1:-$ROOT_DIR/structure/repos.json}"
OUT="$ROOT_DIR/docs/index.html"

command -v jq >/dev/null 2>&1 || { echo "jq is required" >&2; exit 1; }

esc() {
  # Minimal HTML-escape for text nodes.
  local s="$1"
  s="${s//&/&amp;}"
  s="${s//</&lt;}"
  s="${s//>/&gt;}"
  printf '%s' "$s"
}

lineage_label() {
  case "$1" in
    original) echo "Original edition" ;;
    openstax-remix) echo "OpenStax remix" ;;
    public-domain-adaptation) echo "Open-license adaptation" ;;
    *) echo "" ;;
  esac
}

card_html() {
  local json="$1"
  local name display desc url topics_html source_html
  name="$(jq -r '.name' <<<"$json")"
  display="$(esc "$(jq -r '.displayName' <<<"$json")")"
  desc="$(esc "$(jq -r '.description' <<<"$json")")"
  url="$(jq -r '.deployedUrl // .githubPagesUrl // ("https://github.com/QuadriviumPress/" + .name)' <<<"$json")"

  topics_html=""
  while IFS= read -r topic; do
    [[ -z "$topic" ]] && continue
    topics_html+="<li>$(esc "$topic")</li>"
  done < <(jq -r '(.subjectTopics // [])[:3][]' <<<"$json")

  source_html=""
  if jq -e '.source != null' <<<"$json" >/dev/null; then
    local author title
    author="$(esc "$(jq -r '.source.author' <<<"$json")")"
    title="$(esc "$(jq -r '.source.title' <<<"$json")")"
    source_html="  <p class=\"card-source\">After <cite>$title</cite> by $author</p>"
  fi

  local lineage lineage_text badge_html=""
  lineage="$(jq -r '.lineage // ""' <<<"$json")"
  lineage_text="$(lineage_label "$lineage")"
  [[ -n "$lineage_text" ]] && badge_html="<span class=\"badge badge-$lineage\">$(esc "$lineage_text")</span>"

  cat <<CARD
<article class="card" data-name="$(esc "$name")">
  <header class="card-head">
    <h3><a href="$(esc "$url")">$display</a></h3>
    $badge_html
  </header>
  <p class="card-desc">$desc</p>
$source_html
  <ul class="card-topics">$topics_html</ul>
</article>
CARD
}

BOOKS_JSON="$(jq -c '[.repos[] | select(.status == "active" and .isBook == true)] | sort_by(.displayName)' "$CATALOG")"
TOTAL="$(jq 'length' <<<"$BOOKS_JSON")"
# The output must depend only on catalog content. A commit-derived timestamp
# changes after the catalog and generated page are committed together, making
# the self-check report a false stale-page failure on the next CI run.

mkdir -p "$ROOT_DIR/docs"

{
  cat <<HTML
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QuadriviumPress books</title>
<style>
  :root { color-scheme: light dark; }
  body { font: 16px/1.5 system-ui, sans-serif; max-width: 72rem; margin: 0 auto; padding: 2rem 1rem 4rem; }
  h1 { margin-bottom: 0.25rem; }
  .subtitle { opacity: 0.75; margin-top: 0; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(18rem, 1fr)); gap: 1.25rem; margin-top: 2rem; }
  .card { border: 1px solid color-mix(in srgb, currentColor 20%, transparent); border-radius: 0.75rem; padding: 1rem 1.25rem; }
  .card-head { display: flex; align-items: baseline; justify-content: space-between; gap: 0.5rem; flex-wrap: wrap; }
  .card h3 { margin: 0; font-size: 1.05rem; }
  .card a { color: inherit; text-decoration: none; }
  .card a:hover { text-decoration: underline; }
  .card-desc { opacity: 0.85; font-size: 0.92rem; }
  .card-source { font-size: 0.85rem; opacity: 0.7; margin: 0.25rem 0; }
  .card-topics { list-style: none; display: flex; flex-wrap: wrap; gap: 0.4rem; padding: 0; margin: 0.5rem 0 0; }
  .card-topics li { font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 999px; background: color-mix(in srgb, currentColor 10%, transparent); }
  .badge { font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 999px; white-space: nowrap; background: color-mix(in srgb, currentColor 12%, transparent); }
  footer { margin-top: 3rem; font-size: 0.8rem; opacity: 0.6; }
</style>
</head>
<body>
<h1>QuadriviumPress</h1>
<p class="subtitle">$TOTAL open textbooks, generated from <a href="../structure/repos.json">structure/repos.json</a>.</p>
<div class="grid">
HTML

  jq -c '.[]' <<<"$BOOKS_JSON" | while IFS= read -r entry; do
    card_html "$entry"
  done

  cat <<HTML
</div>
<footer>Generated from <a href="../structure/repos.json">structure/repos.json</a> by <a href="https://github.com/QuadriviumPress/bindery">bindery</a>.</footer>
</body>
</html>
HTML
} > "$OUT"

echo "Wrote $OUT ($TOTAL active books)"
