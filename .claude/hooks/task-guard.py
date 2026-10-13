#!/usr/bin/env python3
"""PreToolUse-Hook: setzt die sequenzielle Abarbeitung von docs/tasks/ durch.

Regeln (Verstoß → Exit 2, Begründung auf stderr, der Tool-Aufruf wird blockiert):
- `set-status <id> ~` (Task beginnen/nacharbeiten) nur für die Task, die `taskctl next` liefert.
  Steht diese auf R/C/B, ist der Plan blockiert: keine andere Task beginnen.
- `set-status <id> X` für eine Task auf [R] ist die Abnahme und damit dem Nutzer vorbehalten.
- `--force` und `--set-status` bei taskctl-Aufrufen sind dem Nutzer vorbehalten.
- docs/tasks/ wird nie direkt bearbeitet, nur über taskctl.
"""
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

PROJECT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
TASKS_DIR = "docs/tasks"
SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\n|\|")
WRITE_HINTS = re.compile(r"(^|\s)(>|>>|tee|rm|mv|cp|truncate|sed\s+-i|perl\s+-i)(\s|$)")


def deny(reason: str) -> None:
    print(f"task-guard: {reason}", file=sys.stderr)
    sys.exit(2)


def taskctl_json(root: str, *args: str) -> dict:
    """taskctl --json <args>; fail closed, wenn taskctl nicht läuft."""
    try:
        r = subprocess.run([str(PROJECT / "tools" / "taskctl"), "--root", root, "--json", *args],
                           cwd=PROJECT, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as e:
        deny(f"taskctl nicht ausführbar ({e}); Statuswechsel wird nicht zugelassen.")
    try:
        data = json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        deny(f"taskctl {args[0]} lieferte keine JSON-Ausgabe: {r.stderr.strip()}")
    if r.returncode != 0:
        deny(f"taskctl {args[0]} fehlgeschlagen ({data.get('reason') or r.stderr.strip()}).")
    return data


def tokens(segment: str) -> list[str]:
    try:
        return shlex.split(segment)
    except ValueError:
        return segment.split()


def check_segment(segment: str) -> None:
    toks = tokens(segment)
    is_taskctl = any("taskctl" in t for t in toks)
    if "set-status" not in toks and not is_taskctl:
        return
    if "--force" in toks or "--set-status" in toks:
        deny("--force/--set-status bei taskctl sind dem Nutzer vorbehalten.")
    if "set-status" not in toks:
        return
    i = toks.index("set-status")
    args = toks[i + 1:i + 3]
    if len(args) < 2 or args[1] not in ("~", "X"):
        return  # übrige Übergänge (R, C, B) prüft taskctl selbst
    task_id, target = args
    if not re.fullmatch(r"[0-9a-f]{6}", task_id):
        deny(f"Task-ID muss literal angegeben werden (gefunden: '{task_id}').")
    root = toks[toks.index("--root") + 1] if "--root" in toks[:-1] else "docs"
    if target == "~":
        nxt = taskctl_json(root, "next")
        if nxt.get("id") != task_id:
            status = nxt.get("status", "").strip()
            blocked = f" und steht auf [{status}] – Plan blockiert, auf den Nutzer warten" if status in ("R", "C", "B") else ""
            deny(f"Task {task_id} ist nicht dran; `taskctl next` liefert {nxt.get('id')} '{nxt.get('name')}'{blocked}.")
    elif target == "X":
        current = taskctl_json(root, "show", task_id).get("status", "").strip()
        if current == "R":
            deny(f"Task {task_id} steht auf [R]: die Abnahme setzt der Nutzer selbst.")


def check_bash(command: str) -> None:
    for segment in SEGMENT_SPLIT.split(command):
        if TASKS_DIR in segment and WRITE_HINTS.search(segment) and "taskctl" not in segment:
            deny(f"{TASKS_DIR}/ nur über taskctl ändern.")
    # Funktionen/Subshells über mehrere Segmente: set-status-Aufrufe einzeln prüfen
    for segment in re.split(r"&&|\|\||;|\n|\{|\}|\(|\)", command):
        if segment.strip():
            check_segment(segment)


def main() -> None:
    try:
        event = json.load(sys.stdin)
    except json.JSONDecodeError:
        return
    tool, inp = event.get("tool_name", ""), event.get("tool_input", {}) or {}
    if tool == "Bash":
        check_bash(inp.get("command", ""))
    elif tool in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
        path = Path(inp.get("file_path") or inp.get("notebook_path") or "")
        try:
            rel = path.resolve().relative_to(PROJECT.resolve()).as_posix()
        except ValueError:
            return
        if rel.startswith(TASKS_DIR + "/"):
            deny(f"{TASKS_DIR}/ nur über taskctl ändern.")


if __name__ == "__main__":
    main()
