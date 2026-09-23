#!/usr/bin/env python3
"""Collecte l'activité d'une journée (git + sessions Claude Code + sessions Codex CLI).

Mode par défaut : blocs horaires du projet courant, pause de 90 min = nouveau bloc.
    timelog.py [--date YYYY-MM-DD] [--project CHEMIN]
Mode quick : projets touchés par jour, tous projets confondus, sans git.
    timelog.py --quick [--date YYYY-MM-DD | --days N | --range YYYY-MM-DD..YYYY-MM-DD]

Toutes les heures sont en heure locale de la machine. Aucune écriture, lecture seule.
"""
import argparse
import json
import os
import re
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path

GAP = timedelta(minutes=90)
MAX_MSG_PER_SESSION = 50
MAX_CHARS = 400  # longueur max d'un message affiché
HOME = Path.home()
CLAUDE_DIR = HOME / ".claude" / "projects"
CODEX_DIR = Path(os.environ.get("CODEX_HOME", HOME / ".codex")) / "sessions"


def local(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone()


def jsonl(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    yield json.loads(line)
                except ValueError:
                    continue
    except OSError:
        return


def claude_text(d):
    """Texte réellement tapé par l'utilisateur, ou None pour un message injecté."""
    if d.get("isMeta") or d.get("isCompactSummary"):
        return None
    content = d.get("message", {}).get("content")
    if isinstance(content, list):
        texts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
        content = texts[0] if texts else None  # que des retours d'outils
    content = re.sub(r"</?pasted_content[^>]*>", " ", content or "").strip()  # texte collé = saisie réelle
    if not content:
        return None
    if content.startswith("<"):
        cmd = re.search(r"<command-name>(.*?)</command-name>", content)
        if not cmd:
            return None  # notifications, sorties de commandes, contexte IDE
        args = re.search(r"<command-args>(.*?)</command-args>", content, re.S)
        return (cmd.group(1) + " " + (args.group(1).strip() if args else "")).strip()
    return content


def claude_sessions(since, project=None):
    """(cwd, fichier, [(heure, texte ou None)]) pour chaque session modifiée depuis `since`."""
    if not CLAUDE_DIR.is_dir():
        return
    prefix = re.sub(r"[^A-Za-z0-9]", "-", str(project)) if project else ""
    for d in CLAUDE_DIR.iterdir():
        if not d.name.startswith(prefix):
            continue
        for f in d.glob("*.jsonl"):
            if f.stat().st_mtime < since.timestamp():
                continue
            cwd, events = None, []
            for line in jsonl(f):
                cwd = cwd or line.get("cwd")
                if line.get("type") not in ("user", "assistant") or "timestamp" not in line:
                    continue
                text = claude_text(line) if line["type"] == "user" else None
                if line["type"] == "user" and text is None:
                    continue
                events.append((local(line["timestamp"]), text))
            if cwd:
                yield cwd, f, events


def codex_sessions(since):
    if not CODEX_DIR.is_dir():
        return
    for f in CODEX_DIR.glob("*/*/*/*.jsonl"):
        if f.stat().st_mtime < since.timestamp():
            continue
        cwd, events = None, []
        for line in jsonl(f):
            p = line.get("payload") or {}
            if line.get("type") == "session_meta":
                cwd = p.get("cwd")
            if line.get("type") != "response_item" or p.get("type") != "message" or "timestamp" not in line:
                continue
            if p.get("role") == "assistant":
                events.append((local(line["timestamp"]), None))
            elif p.get("role") == "user":
                for c in p.get("content", []):
                    t = (c.get("text") or "").strip()
                    if len(t) >= 5 and not t.startswith(("<", "# AGENTS")):
                        events.append((local(line["timestamp"]), t))
        if cwd:
            yield cwd, f, events


def in_project(cwd, project):
    return cwd == str(project) or cwd.startswith(str(project) + os.sep)


def sample(msgs):
    """Garde les premiers messages (le contexte) puis un échantillon régulier du reste."""
    if len(msgs) <= MAX_MSG_PER_SESSION:
        return msgs
    head, rest = msgs[:10], msgs[10:]
    step = len(rest) / (MAX_MSG_PER_SESSION - 10)
    return head + [rest[int(i * step)] for i in range(MAX_MSG_PER_SESSION - 10)]


def git_commits(project, start, end):
    def git(*args):
        r = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else ""

    if not git("rev-parse", "--git-dir"):
        return []
    email = git("config", "user.email").strip()
    fmt = ["--pretty=format:%x1e%aI%x1f%s", "--name-only"]
    out = git("log", "--all", f"--since={start.isoformat()}", f"--until={end.isoformat()}",
              *([f"--author={email}"] if email else []), *fmt)
    commits = []
    for rec in out.split("\x1e")[1:]:
        head, _, files = rec.partition("\n")
        ts, _, subject = head.partition("\x1f")
        names = [n for n in files.split("\n") if n.strip()]
        more = f" +{len(names) - 5}" if len(names) > 5 else ""
        commits.append((local(ts), f"{subject} (fichiers : {', '.join(names[:5])}{more})"))
    return commits


def hhmm(t):
    return f"{t.hour}h" if t.minute == 0 else f"{t.hour}h{t.minute:02d}"


def duration(td):
    minutes = round(td.total_seconds() / 60)
    return f"{minutes}min" if minutes < 60 else f"{minutes // 60}h{minutes % 60:02d}"


def day_bounds(d):
    start = datetime.combine(d, datetime.min.time()).astimezone()
    return start, start + timedelta(days=1)


def run_day(day, project):
    start, end = day_bounds(day)
    events = []  # (heure, source, texte ou None)
    for source, sessions in (("claude", claude_sessions(start, project)), ("codex", codex_sessions(start))):
        for cwd, _, evs in sessions:
            if not in_project(cwd, project):
                continue
            evs = [e for e in evs if start <= e[0] < end]
            msgs = sample([e for e in evs if e[1]])
            events += [(t, source, None) for t, txt in evs if not txt]
            events += [(t, source, txt) for t, txt in msgs]
    events += [(t, "git", s) for t, s in git_commits(project, start, end)]
    if not events:
        print(f"AUCUNE ACTIVITÉ pour {project} le {day.isoformat()}")
        return
    events.sort(key=lambda e: e[0])
    blocks = [[events[0]]]
    for e in events[1:]:
        if e[0] - blocks[-1][-1][0] > GAP:
            blocks.append([])
        blocks[-1].append(e)
    total = timedelta()
    print(f"PROJET {project} - {day.isoformat()}")
    for i, b in enumerate(blocks, 1):
        span = b[-1][0] - b[0][0]
        total += span
        print(f"\nBLOC {i} : {hhmm(b[0][0])}-{hhmm(b[-1][0])} ({duration(span)})")
        for t, source, txt in b:
            if txt:
                print(f"  [{source} {t:%H:%M}] {' '.join(txt.split())[:MAX_CHARS]}")
    if len(blocks) > 1:
        print(f"\nTOTAL : {duration(total)}")


def run_quick(first, last):
    start, _ = day_bounds(first)
    _, end = day_bounds(last)
    skip = {str(HOME), str(HOME / "Downloads"), str(HOME / "Téléchargements")}
    days = {}  # date -> set(cwd)
    sessions = [s for gen in (claude_sessions(start), codex_sessions(start)) for s in gen]
    for cwd, _, evs in sessions:
        firsts = [t for t, txt in evs if txt]
        if not firsts or cwd in skip or cwd.startswith(("/tmp", str(HOME / "Downloads"))):
            continue
        t = min(firsts)  # la session compte pour le jour de son premier message
        if start <= t < end:
            days.setdefault(t.date(), set()).add(cwd.rstrip(os.sep))
    if not days:
        print(f"AUCUNE ACTIVITÉ sur la plage {first.isoformat()}..{last.isoformat()}")
        return
    names = {}
    for cwd in set().union(*days.values()):
        names.setdefault(Path(cwd).name, set()).add(cwd)
    def label(cwd):
        p = Path(cwd)
        return f"{p.parent.name}/{p.name}" if len(names[p.name]) > 1 else p.name
    for d in sorted(days):
        print(f"{d.isoformat()} : {', '.join(sorted({label(c) for c in days[d]}, key=str.lower))}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", type=date.fromisoformat, default=date.today())
    ap.add_argument("--project", default=os.getcwd())
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--days", type=int)
    ap.add_argument("--range")
    a = ap.parse_args()
    if not a.quick:
        run_day(a.date, Path(a.project).resolve())
    elif a.range:
        first, last = (date.fromisoformat(x) for x in a.range.split(".."))
        run_quick(first, last)
    elif a.days:
        run_quick(date.today() - timedelta(days=a.days - 1), date.today())
    else:
        run_quick(a.date, a.date)


if __name__ == "__main__":
    main()
