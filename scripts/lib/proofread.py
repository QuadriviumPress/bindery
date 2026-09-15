#!/usr/bin/env python3
"""Paced Codex proofreading queue for the QuadriviumPress fleet.

Runs one `codex exec` job at a time, tracks a daily *active* time budget
(Codex wall time inside each invocation), and sleeps between jobs so the
workload stays under a 5h Codex limit and avoids bursty rate-limit patterns.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
BINDERY_ROOT = SCRIPT_DIR.parent.parent
FLEET_ROOT = Path(os.environ.get("QUADRIVIUM_WORKSPACE", BINDERY_ROOT.parent)).resolve()
CATALOG = Path(
    os.environ.get("REPOS_JSON", BINDERY_ROOT / "structure" / "repos.json")
).resolve()
PROMPT_TEMPLATE = SCRIPT_DIR / "proofread_prompt.md"
AGENT_SRC = BINDERY_ROOT / ".codex" / "agents" / "textbook-proofreader.toml"

DEFAULT_STATE_DIR = Path(
    os.environ.get("PROOFREAD_STATE_DIR", FLEET_ROOT / ".proofread")
).resolve()

SKIP_DIR_NAMES = {
    ".git",
    "node_modules",
    "_build",
    "_site",
    "vendor",
    "dist",
    "build",
    "work",
    ".proofread",
    "oem-*-media",  # not matched literally; filtered below
}
CONTENT_EXTS = {".md", ".myst", ".tex", ".cnxml", ".markdown"}
CONTENT_ROOT_NAMES = (
    "chapters",
    "content",
    "contents",
    "front",
    "back",
    "appendices",
    "tex",
    "source",
    "_posts",
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def today_key() -> str:
    return date.today().isoformat()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def parse_duration(text: str) -> int:
    """Parse durations like 5h, 4h30m, 90m, 2700s into seconds."""
    text = text.strip().lower()
    if text.isdigit():
        return int(text)
    total = 0
    for amount, unit in re.findall(r"(\d+)\s*([hms])", text):
        n = int(amount)
        if unit == "h":
            total += n * 3600
        elif unit == "m":
            total += n * 60
        else:
            total += n
    if total <= 0:
        raise argparse.ArgumentTypeError(f"invalid duration: {text!r}")
    return total


def human_duration(seconds: float) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"


@dataclass
class Settings:
    state_dir: Path
    daily_budget_s: int = 4 * 3600 + 30 * 60  # 4h30m active Codex time
    delay_min_s: int = 8 * 60
    delay_max_s: int = 15 * 60
    max_jobs: int | None = None
    mode: str = "report"  # report | fix
    model: str | None = None
    chunk_chars: int = 24_000
    repo_filter: list[str] | None = None
    dry_run: bool = False
    install_agent: bool = True
    codex_bin: str = "codex"
    skip_osbooks: bool = True
    jitter: bool = True


class ProofreadState:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.state_dir = settings.state_dir
        self.queue_path = self.state_dir / "queue.json"
        self.budget_path = self.state_dir / "budget.json"
        self.runs_dir = self.state_dir / "runs"
        self.reports_dir = self.state_dir / "reports"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_queue(self) -> dict[str, Any]:
        return load_json(
            self.queue_path,
            {
                "version": 1,
                "created_at": None,
                "updated_at": None,
                "jobs": [],
            },
        )

    def save_queue(self, queue: dict[str, Any]) -> None:
        queue["updated_at"] = utc_now().isoformat()
        dump_json(self.queue_path, queue)

    def load_budget(self) -> dict[str, Any]:
        data = load_json(self.budget_path, {"days": {}})
        data.setdefault("days", {})
        return data

    def save_budget(self, budget: dict[str, Any]) -> None:
        dump_json(self.budget_path, budget)

    def day_used(self, budget: dict[str, Any] | None = None) -> float:
        budget = budget or self.load_budget()
        day = budget.get("days", {}).get(today_key(), {})
        return float(day.get("active_seconds", 0.0))

    def remaining_budget(self) -> float:
        return max(0.0, self.settings.daily_budget_s - self.day_used())

    def add_active_time(self, seconds: float, job_id: str) -> None:
        budget = self.load_budget()
        day = budget["days"].setdefault(
            today_key(),
            {"active_seconds": 0.0, "jobs": 0, "job_ids": []},
        )
        day["active_seconds"] = float(day.get("active_seconds", 0.0)) + max(0.0, seconds)
        day["jobs"] = int(day.get("jobs", 0)) + 1
        ids = day.setdefault("job_ids", [])
        if job_id not in ids:
            ids.append(job_id)
        self.save_budget(budget)


def should_skip_dirname(name: str) -> bool:
    if name in SKIP_DIR_NAMES or name.startswith("."):
        return True
    if name.endswith("-media"):
        return True
    return False


def content_roots_for(repo_dir: Path) -> list[Path]:
    roots: list[Path] = []
    for name in CONTENT_ROOT_NAMES:
        p = repo_dir / name
        if p.is_dir():
            roots.append(p)
    for pattern in ("oem-*", "mecmath-*"):
        for p in sorted(repo_dir.glob(pattern)):
            if p.is_dir() and not should_skip_dirname(p.name):
                roots.append(p)
    # Fallback content roots when standard dirs are absent
    if not roots:
        for name in ("_chapters", "docs"):
            p = repo_dir / name
            if p.is_dir():
                roots.append(p)
    return roots


def iter_content_files(repo_dir: Path) -> list[Path]:
    files: list[Path] = []
    roots = content_roots_for(repo_dir)
    if not roots:
        return files
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if not should_skip_dirname(d))
            for name in sorted(filenames):
                path = Path(dirpath) / name
                if path.suffix.lower() in CONTENT_EXTS:
                    files.append(path)
    # de-dupe while preserving order
    seen: set[Path] = set()
    out: list[Path] = []
    for f in files:
        rp = f.resolve()
        if rp not in seen:
            seen.add(rp)
            out.append(f)
    return out


def file_fingerprint(path: Path) -> str:
    h = hashlib.sha1()
    h.update(str(path.stat().st_mtime_ns).encode())
    h.update(b":")
    h.update(str(path.stat().st_size).encode())
    return h.hexdigest()[:16]


def chunk_file(path: Path, chunk_chars: int) -> list[tuple[int, int, str]]:
    """Return list of (line_start, line_end, chunk_id_suffix). 1-based inclusive lines."""
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= chunk_chars:
        lines = text.count("\n") + (0 if text.endswith("\n") or text == "" else 1)
        if text == "":
            lines = 0
        return [(1, max(1, lines) if lines else 1, "full")]

    lines = text.splitlines(keepends=True)
    chunks: list[tuple[int, int, str]] = []
    start = 0
    idx = 0
    while start < len(lines):
        size = 0
        end = start
        while end < len(lines) and (size + len(lines[end]) <= chunk_chars or end == start):
            size += len(lines[end])
            end += 1
        idx += 1
        chunks.append((start + 1, end, f"c{idx:02d}"))
        start = end
    return chunks


def make_job_id(repo: str, rel: str, suffix: str) -> str:
    raw = f"{repo}:{rel}:{suffix}"
    return hashlib.sha1(raw.encode()).hexdigest()[:12]


def catalog_books(skip_osbooks: bool = True) -> list[dict[str, Any]]:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    books = []
    for repo in data.get("repos", []):
        if not repo.get("isBook"):
            continue
        name = repo["name"]
        if skip_osbooks and name.startswith("osbooks-"):
            continue
        books.append(repo)
    return books


def cmd_init(settings: Settings) -> int:
    state = ProofreadState(settings)
    queue = state.load_queue()
    existing = {j["id"]: j for j in queue.get("jobs", [])}
    books = catalog_books(settings.skip_osbooks)
    if settings.repo_filter:
        wanted = set(settings.repo_filter)
        books = [b for b in books if b["name"] in wanted]

    added = 0
    refreshed = 0
    jobs: list[dict[str, Any]] = []

    for book in books:
        name = book["name"]
        repo_dir = FLEET_ROOT / name
        if not repo_dir.is_dir() or not (repo_dir / ".git").exists():
            print(f"skip (missing local clone): {name}", file=sys.stderr)
            continue
        files = iter_content_files(repo_dir)
        print(f"{name}: {len(files)} content files")
        for path in files:
            rel = str(path.relative_to(repo_dir)).replace("\\", "/")
            fp = file_fingerprint(path)
            for line_start, line_end, suffix in chunk_file(path, settings.chunk_chars):
                jid = make_job_id(name, rel, suffix)
                prev = existing.get(jid)
                job = {
                    "id": jid,
                    "repo": name,
                    "path": rel,
                    "line_start": line_start,
                    "line_end": line_end,
                    "chunk": suffix,
                    "fingerprint": fp,
                    "format": book.get("format"),
                    "status": "pending",
                    "attempts": 0,
                    "last_error": None,
                    "completed_at": None,
                    "report_path": None,
                }
                if prev and prev.get("fingerprint") == fp and prev.get("status") == "done":
                    job["status"] = "done"
                    job["completed_at"] = prev.get("completed_at")
                    job["report_path"] = prev.get("report_path")
                    job["attempts"] = prev.get("attempts", 0)
                    refreshed += 1
                elif prev and prev.get("status") in {"done", "skipped", "error"}:
                    # content changed or retryable: re-queue changed files
                    if prev.get("fingerprint") != fp:
                        job["status"] = "pending"
                        added += 1
                    else:
                        job["status"] = prev["status"]
                        job["completed_at"] = prev.get("completed_at")
                        job["report_path"] = prev.get("report_path")
                        job["attempts"] = prev.get("attempts", 0)
                        job["last_error"] = prev.get("last_error")
                else:
                    added += 1
                jobs.append(job)

    # Keep done jobs for repos not in this init pass? Prefer replace full queue for filtered set.
    if settings.repo_filter:
        keep_repos = set(settings.repo_filter)
        retained = [j for j in existing.values() if j["repo"] not in keep_repos]
        jobs = retained + jobs

    queue = {
        "version": 1,
        "created_at": queue.get("created_at") or utc_now().isoformat(),
        "updated_at": utc_now().isoformat(),
        "fleet_root": str(FLEET_ROOT),
        "jobs": jobs,
    }
    state.save_queue(queue)
    pending = sum(1 for j in jobs if j["status"] == "pending")
    done = sum(1 for j in jobs if j["status"] == "done")
    print(
        f"Queue written to {state.queue_path}\n"
        f"jobs={len(jobs)} pending={pending} done={done} newly_queued≈{added}"
    )
    return 0


def cmd_status(settings: Settings) -> int:
    state = ProofreadState(settings)
    queue = state.load_queue()
    jobs = queue.get("jobs", [])
    if not jobs:
        print("No queue yet. Run: codex-proofread.sh init")
        return 1
    counts: dict[str, int] = {}
    by_repo: dict[str, dict[str, int]] = {}
    for j in jobs:
        counts[j["status"]] = counts.get(j["status"], 0) + 1
        br = by_repo.setdefault(j["repo"], {})
        br[j["status"]] = br.get(j["status"], 0) + 1
    used = state.day_used()
    rem = state.remaining_budget()
    print(f"state: {state.state_dir}")
    print(f"jobs:  {len(jobs)}  {counts}")
    print(
        f"today ({today_key()}): used {human_duration(used)} / "
        f"{human_duration(settings.daily_budget_s)} "
        f"(remaining {human_duration(rem)})"
    )
    print(
        f"pacing: delay {human_duration(settings.delay_min_s)}"
        f"–{human_duration(settings.delay_max_s)} between jobs; "
        f"mode={settings.mode}"
    )
    print("\nBy repo (pending/done/error):")
    for repo in sorted(by_repo):
        br = by_repo[repo]
        print(
            f"  {repo}: pending={br.get('pending', 0)} "
            f"done={br.get('done', 0)} error={br.get('error', 0)} "
            f"skipped={br.get('skipped', 0)}"
        )
    return 0


def next_pending(
    queue: dict[str, Any],
    repo_filter: list[str] | None,
    *,
    skip_dry_seen: bool = False,
) -> dict[str, Any] | None:
    for j in queue.get("jobs", []):
        if j.get("status") != "pending":
            continue
        if repo_filter and j["repo"] not in repo_filter:
            continue
        if skip_dry_seen and j.get("_dry_seen"):
            continue
        return j
    return None


def ensure_agent_installed(settings: Settings) -> None:
    if not settings.install_agent:
        return
    dest_dir = Path.home() / ".codex" / "agents"
    dest = dest_dir / "textbook-proofreader.toml"
    if not AGENT_SRC.exists():
        print(f"warning: agent template missing: {AGENT_SRC}", file=sys.stderr)
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    if not dest.exists() or dest.read_text(encoding="utf-8") != AGENT_SRC.read_text(
        encoding="utf-8"
    ):
        shutil.copy2(AGENT_SRC, dest)
        print(f"Installed Codex agent → {dest}")


def build_prompt(job: dict[str, Any], settings: Settings, abs_path: Path) -> str:
    template = PROMPT_TEMPLATE.read_text(encoding="utf-8")
    if settings.mode == "fix":
        mode_instructions = (
            "Mode is FIX: apply only high-confidence spelling/typo edits directly "
            "in the target file. Keep a finding entry for every change you make. "
            "Do not reformat the file. Do not touch other files."
        )
    else:
        mode_instructions = (
            "Mode is REPORT: do not modify any files. Only return JSON findings."
        )
    return template.format(
        rel_path=job["path"],
        abs_path=str(abs_path),
        mode=settings.mode,
        repo=job["repo"],
        job_id=job["id"],
        line_start=job.get("line_start", 1),
        line_end=job.get("line_end", 1),
        mode_instructions=mode_instructions,
    )


def run_codex(
    job: dict[str, Any], settings: Settings, prompt: str, repo_dir: Path
) -> tuple[int, str, float]:
    out_last = settings.state_dir / "runs" / f"{job['id']}.last.md"
    out_jsonl = settings.state_dir / "runs" / f"{job['id']}.jsonl"
    sandbox = "workspace-write" if settings.mode == "fix" else "read-only"
    cmd = [
        settings.codex_bin,
        "exec",
        "--skip-git-repo-check",
        "-C",
        str(repo_dir),
        "--sandbox",
        sandbox,
        "--json",
        "-o",
        str(out_last),
        # Keep each job single-threaded: no nested Codex fan-out.
        "-c",
        "agents.enabled=false",
    ]
    # Prefer the custom agent via prompt instruction; model override optional.
    if settings.model:
        cmd.extend(["-m", settings.model])
    if settings.mode == "fix":
        # Non-interactive writes need an approval path that won't hang.
        cmd.append("--approve-for-me")
    cmd.append(prompt)

    if settings.dry_run:
        target = repo_dir / job["path"]
        print("DRY-RUN:", " ".join(shlex.quote(c) for c in cmd[:12]), "... <prompt>")
        print(f"DRY-RUN prompt chars={len(prompt)} target={target}")
        return 0, "", 0.0

    started = time.monotonic()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        raise SystemExit(
            f"codex binary not found ({settings.codex_bin!r}). Install Codex CLI first."
        )
    elapsed = time.monotonic() - started
    out_jsonl.write_text(proc.stdout or "", encoding="utf-8")
    if proc.stderr:
        (settings.state_dir / "runs" / f"{job['id']}.stderr.txt").write_text(
            proc.stderr, encoding="utf-8"
        )
    last = out_last.read_text(encoding="utf-8") if out_last.exists() else ""
    return proc.returncode, last, elapsed


def extract_json_payload(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    # Fence fallback
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass
    # First { ... last }
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            data = json.loads(text[start : end + 1])
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            return None
    return None


def looks_like_rate_limit(rc: int, last: str, stderr_path: Path | None) -> bool:
    blob = last.lower()
    if stderr_path and stderr_path.exists():
        blob += "\n" + stderr_path.read_text(encoding="utf-8", errors="replace").lower()
    needles = ("429", "too many requests", "rate limit", "usage limit", "quota")
    return any(n in blob for n in needles) or rc in {429}


def cmd_run(settings: Settings) -> int:
    if not shutil.which(settings.codex_bin) and not settings.dry_run:
        print(f"error: `{settings.codex_bin}` not on PATH", file=sys.stderr)
        return 2

    ensure_agent_installed(settings)
    state = ProofreadState(settings)
    queue = state.load_queue()
    if not queue.get("jobs"):
        print("No queue. Run init first.", file=sys.stderr)
        return 1

    completed_this_session = 0
    while True:
        remaining = state.remaining_budget()
        if remaining <= 60:
            print(
                f"Daily active budget exhausted "
                f"({human_duration(settings.daily_budget_s)}). Stopping until tomorrow."
            )
            break
        if settings.max_jobs is not None and completed_this_session >= settings.max_jobs:
            print(f"Hit --max-jobs={settings.max_jobs}. Stopping.")
            break

        job = next_pending(
            queue, settings.repo_filter, skip_dry_seen=settings.dry_run
        )
        if not job:
            print("No pending jobs left.")
            break

        repo_dir = FLEET_ROOT / job["repo"]
        abs_path = repo_dir / job["path"]
        print(
            f"\n=== job {job['id']}  {job['repo']}/{job['path']} "
            f"lines {job.get('line_start')}-{job.get('line_end')} ==="
        )
        print(f"budget remaining today: {human_duration(remaining)}")

        if not abs_path.is_file():
            job["status"] = "skipped"
            job["last_error"] = "missing file"
            job["completed_at"] = utc_now().isoformat()
            state.save_queue(queue)
            continue

        prompt = build_prompt(job, settings, abs_path)
        # Nudge the custom agent without requiring spawn APIs.
        prompt = (
            "Use the textbook_proofreader agent behavior if available "
            "(no subagents). Stay single-threaded.\n\n"
            + prompt
        )

        rc, last, elapsed = run_codex(job, settings, prompt, repo_dir)
        if settings.dry_run:
            print("DRY-RUN complete (queue unchanged).")
            completed_this_session += 1
            job["_dry_seen"] = True
            if settings.max_jobs is not None and completed_this_session >= settings.max_jobs:
                break
            if (
                next_pending(queue, settings.repo_filter, skip_dry_seen=True)
                is None
            ):
                break
            print(
                f"DRY-RUN would sleep {human_duration(settings.delay_min_s)} "
                "before next job..."
            )
            continue

        state.add_active_time(elapsed, job["id"])
        job["attempts"] = int(job.get("attempts", 0)) + 1

        stderr_path = state.runs_dir / f"{job['id']}.stderr.txt"
        if looks_like_rate_limit(rc, last, stderr_path):
            job["status"] = "pending"
            job["last_error"] = "rate_limited"
            state.save_queue(queue)
            print(
                "Rate limit / usage signal detected. "
                "Leaving job pending and exiting to stay below radar."
            )
            return 3

        report = extract_json_payload(last) or {
            "job_id": job["id"],
            "repo": job["repo"],
            "path": job["path"],
            "summary": "unparseable agent output",
            "findings": [],
            "raw_excerpt": last[:4000],
            "exit_code": rc,
        }
        report_path = state.reports_dir / job["repo"] / f"{job['id']}.json"
        dump_json(report_path, report)
        job["report_path"] = str(report_path)
        job["last_error"] = None if rc == 0 else f"codex exit {rc}"
        job["status"] = "done" if rc == 0 else "error"
        job["completed_at"] = utc_now().isoformat()
        job["active_seconds"] = round(elapsed, 2)
        findings_n = len(report.get("findings") or [])
        print(
            f"done status={job['status']} active={human_duration(elapsed)} "
            f"findings={findings_n} report={report_path}"
        )
        state.save_queue(queue)
        completed_this_session += 1

        # More pending? Sleep before the next Codex call.
        if next_pending(queue, settings.repo_filter) is None:
            break
        if settings.max_jobs is not None and completed_this_session >= settings.max_jobs:
            break
        if state.remaining_budget() <= 60:
            break

        delay = settings.delay_min_s
        if settings.jitter and settings.delay_max_s > settings.delay_min_s:
            delay = random.randint(settings.delay_min_s, settings.delay_max_s)
        print(f"sleeping {human_duration(delay)} before next job...")
        time.sleep(delay)

    cmd_status(settings)
    return 0


def cmd_install_agent(settings: Settings) -> int:
    settings.install_agent = True
    ensure_agent_installed(settings)
    return 0


def cmd_reset_day(settings: Settings) -> int:
    state = ProofreadState(settings)
    budget = state.load_budget()
    if today_key() in budget.get("days", {}):
        del budget["days"][today_key()]
        state.save_budget(budget)
        print(f"Cleared today's budget counters ({today_key()}).")
    else:
        print("Nothing to clear for today.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Paced Codex proofreader for QuadriviumPress textbooks",
    )
    p.add_argument(
        "--state-dir",
        type=Path,
        default=DEFAULT_STATE_DIR,
        help=f"State/reports directory (default: {DEFAULT_STATE_DIR})",
    )
    p.add_argument(
        "--daily-budget",
        type=parse_duration,
        default=parse_duration(os.environ.get("PROOFREAD_DAILY_BUDGET", "4h30m")),
        help="Max active Codex time per calendar day (default: 4h30m)",
    )
    p.add_argument(
        "--delay-min",
        type=parse_duration,
        default=parse_duration(os.environ.get("PROOFREAD_DELAY_MIN", "8m")),
        help="Minimum sleep between jobs (default: 8m)",
    )
    p.add_argument(
        "--delay-max",
        type=parse_duration,
        default=parse_duration(os.environ.get("PROOFREAD_DELAY_MAX", "15m")),
        help="Maximum sleep between jobs (default: 15m)",
    )
    p.add_argument(
        "--mode",
        choices=("report", "fix"),
        default=os.environ.get("PROOFREAD_MODE", "report"),
        help="report=read-only findings; fix=apply high-confidence edits",
    )
    p.add_argument("--model", default=os.environ.get("PROOFREAD_MODEL"), help="Codex -m override")
    p.add_argument("--chunk-chars", type=int, default=24000)
    p.add_argument("--codex-bin", default=os.environ.get("CODEX_BIN", "codex"))
    p.add_argument("--no-install-agent", action="store_true")
    p.add_argument("--include-osbooks", action="store_true")

    def add_repo_opt(sp: argparse.ArgumentParser) -> None:
        sp.add_argument(
            "--repo",
            action="append",
            dest="repos",
            help="Limit to repo (repeatable)",
        )

    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("init", help="Build or refresh the proofreading queue")
    add_repo_opt(sp)
    sp.set_defaults(func=lambda s: cmd_init(s))

    sp = sub.add_parser("status", help="Show queue + today's budget")
    add_repo_opt(sp)
    sp.set_defaults(func=lambda s: cmd_status(s))

    sp = sub.add_parser("run", help="Process pending jobs within today's budget")
    add_repo_opt(sp)
    sp.add_argument("--max-jobs", type=int, default=None)
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(func=None)  # handled below

    sp = sub.add_parser("install-agent", help="Install ~/.codex/agents/textbook-proofreader.toml")
    sp.set_defaults(func=lambda s: cmd_install_agent(s))

    sp = sub.add_parser("reset-day", help="Clear today's active-time counters")
    sp.set_defaults(func=lambda s: cmd_reset_day(s))

    return p


def settings_from_args(args: argparse.Namespace) -> Settings:
    return Settings(
        state_dir=args.state_dir.expanduser().resolve(),
        daily_budget_s=args.daily_budget,
        delay_min_s=args.delay_min,
        delay_max_s=args.delay_max,
        max_jobs=getattr(args, "max_jobs", None),
        mode=args.mode,
        model=args.model,
        chunk_chars=args.chunk_chars,
        repo_filter=getattr(args, "repos", None),
        dry_run=bool(getattr(args, "dry_run", False)),
        install_agent=not args.no_install_agent,
        codex_bin=args.codex_bin,
        skip_osbooks=not args.include_osbooks,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = settings_from_args(args)
    if args.delay_max < args.delay_min:
        parser.error("--delay-max must be >= --delay-min")
    if args.command == "run":
        return cmd_run(settings)
    return args.func(settings)


if __name__ == "__main__":
    raise SystemExit(main())
