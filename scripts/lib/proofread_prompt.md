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
