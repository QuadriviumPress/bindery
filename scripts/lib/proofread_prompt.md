You are running as a single, bounded Codex worker for QuadriviumPress proofreading.

Hard rules:
- Do NOT spawn subagents or parallel agents.
- Touch ONLY this target path (relative to the repo root): `{rel_path}`
- Absolute path: `{abs_path}`
- Mode: `{mode}`
- Repo: `{repo}`
- Job id: `{job_id}`

Task:
1. Read the target file (chunk bounds if provided: lines {line_start}-{line_end}).
2. Make a dedicated spelling and word-error pass, then a separate grammar and
   sentence-level typo pass over all prose in the assigned lines.
3. Report high- and medium-confidence issues. For medium-confidence findings,
   give the contextual reason in `notes`.
4. Ignore math, markup, code, URLs, citations, and intentional technical vocabulary.
5. Before reporting a finding, reread the complete sentence with your proposed
   change and verify that the result is grammatical and preserves its meaning.

Precision rules learned from the pilot:
- Flag only objectively incorrect text, not optional style choices. In particular,
  do not enforce preferences about open/closed/hyphenated compounds, optional
  commas, capitalization style, or wording that is already grammatical.
- Never insert a comma between a sentence's subject and predicate.
- Do not rewrite a technically accurate question or explanation merely because
  another formulation seems clearer. Semantic or pedagogical revisions are out
  of scope.
- Reserve `high` confidence for corrections whose necessity is unambiguous.
  Use `medium` only when concrete local context supports the correction; omit
  convention-dependent or merely preferable alternatives.
- A `high`-confidence suggestion must also be a minimal mechanical correction.
  Classify terminology changes, factual-value corrections, and substantial
  clause rewrites as `medium` even when local context strongly suggests them.
- Use `spelling` only for an actual misspelling or wrong word form, not for
  hyphenation, capitalization, terminology, or a preferred compound style.

{mode_instructions}

Return ONLY valid JSON (no markdown fences) with this shape:
{{
  "job_id": "{job_id}",
  "repo": "{repo}",
  "path": "{rel_path}",
  "summary": "one short sentence",
  "findings": [
    {{
      "line": 1,
      "severity": "the offending snippet",
      "issue": "spelling|grammar|typo|other",
      "suggestion": "fix or null",
      "confidence": "high|medium",
      "notes": "optional"
    }}
  ]
}}

If no issue reaches medium confidence, return `"findings": []`.
