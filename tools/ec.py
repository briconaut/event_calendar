#!/usr/bin/env python3
"""ec – Hilfs-CLI für den Event Calendar (siehe docs/spec.md, „Tools“).

Befehle:
  validate                         Daten und Konfiguration prüfen
  render [--calendar] [--from]     Soll-Zustand für den Kalender-Sync als JSON
  new-event / new-location         Gerüst-Dateien anlegen
  list                             Übersichten nach Kalender/Status/Zeitraum
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import jsonschema
import yaml

REPO = Path(__file__).resolve().parent.parent
CALENDARS = ("weihnachtsmaerkte", "feuerwerke", "events")
FOOTER_RE = re.compile(r"ec:(?P<id>\d{4}/[\w-]+) · h:(?P<hash>[0-9a-f]{8})")
FIREWORK_DEFAULT_MINUTES = 30


# --------------------------------------------------------------------------- Laden

class _StringLoader(yaml.SafeLoader):
    """SafeLoader, der Datums-/Zeitwerte als String belässt (Schema prüft Strings)."""


_StringLoader.yaml_implicit_resolvers = {
    k: [(tag, rx) for tag, rx in v if tag != "tag:yaml.org,2002:timestamp"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as f:
        return yaml.load(f, Loader=_StringLoader)


def load_schema(repo: Path, name: str) -> dict:
    return json.loads((repo / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))


@dataclass
class Repo:
    """Geladener Gesamtstand: Settings, Locations, Events (+ Ladefehler)."""
    root: Path
    settings: dict = field(default_factory=dict)
    locations: dict[str, dict] = field(default_factory=dict)
    events: dict[str, dict] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, root: Path) -> "Repo":
        r = cls(root)
        r._load_file(root / "config" / "settings.yaml", "settings", lambda d: setattr(r, "settings", d))
        for p in sorted((root / "config" / "locations").glob("*.yaml")):
            r._load_file(p, "location", lambda d, p=p: r.locations.__setitem__(p.stem, d))
        for p in sorted((root / "data" / "events").glob("*/*.yaml")):
            r._load_file(p, "event", lambda d, p=p: r.events.__setitem__(event_id(p), d))
        return r

    def _load_file(self, path: Path, schema: str, store) -> None:
        rel = path.relative_to(self.root)
        try:
            data = load_yaml(path)
        except (OSError, yaml.YAMLError) as e:
            self.errors.append(f"{rel}: nicht lesbar: {e}")
            return
        validator = jsonschema.Draft202012Validator(load_schema(self.root, schema))
        problems = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        for e in problems:
            loc = "/".join(str(x) for x in e.path) or "<root>"
            self.errors.append(f"{rel}: {loc}: {e.message}")
        if not problems:
            store(data)


def event_id(path: Path) -> str:
    """Event-ID = Pfad relativ zu data/events ohne Endung, z. B. 2026/2026-07-04-slug."""
    return f"{path.parent.name}/{path.stem}"


def event_path(root: Path, eid: str) -> Path:
    return root / "data" / "events" / f"{eid}.yaml"


# --------------------------------------------------------------------------- Zeit

def parse_point(value: str) -> dt.datetime:
    """'YYYY-MM-DD' oder 'YYYY-MM-DDTHH:MM' als naive lokale Zeit."""
    return dt.datetime.fromisoformat(value)


def is_date_only(value: str) -> bool:
    return "T" not in value


def event_span(ev: dict) -> tuple[dt.datetime, dt.datetime]:
    """Zeitraum [start, end) für Vergleiche; ganztägig: end exklusiv (Folgetag)."""
    start = parse_point(ev["start"])
    end_raw = ev.get("end") or ev["start"]
    if ev["all_day"]:
        return start, parse_point(end_raw) + dt.timedelta(days=1)
    if ev.get("end"):
        return start, parse_point(end_raw)
    return start, start + dt.timedelta(minutes=FIREWORK_DEFAULT_MINUTES)


# --------------------------------------------------------------------------- Validierung

def region_level(repo: Repo, location: dict, calendar: str) -> str:
    if location.get("exclude"):
        return "none"
    if location.get("include"):
        return "all"
    region = repo.settings["regions"].get(location["region"])
    return region["levels"][calendar] if region else "none"


def find_series(location: dict, series_id: str | None) -> dict | None:
    if not series_id:
        return None
    return next((s for s in location.get("series", []) if s["id"] == series_id), None)


def validate(repo: Repo) -> tuple[list[str], list[str]]:
    """Liefert (errors, warnings). Schemafehler stammen bereits aus dem Laden."""
    errors, warnings = list(repo.errors), []
    if not repo.settings:
        return errors, warnings
    s = repo.settings

    for lid, loc in repo.locations.items():
        if loc["region"] not in s["regions"]:
            errors.append(f"location {lid}: unbekannte Region '{loc['region']}'")
        if loc.get("include") and loc.get("exclude"):
            errors.append(f"location {lid}: include und exclude gleichzeitig gesetzt")
        seen = set()
        for ser in loc.get("series", []):
            if ser["id"] in seen:
                errors.append(f"location {lid}: Serie '{ser['id']}' doppelt")
            seen.add(ser["id"])
            if ser["calendar"] == "events" and ser.get("category") not in s["categories"]:
                errors.append(f"location {lid}: Serie '{ser['id']}': unbekannte Kategorie '{ser.get('category')}'")
            if (ser.get("directions") or ser.get("viewpoints")) and not ser.get("sources"):
                errors.append(f"location {lid}: Serie '{ser['id']}': directions/viewpoints ohne sources")

    for eid, ev in repo.events.items():
        errors += [f"event {eid}: {m}" for m in _check_event(repo, eid, ev)]

    warnings += _duplicate_suspects(repo)
    return errors, warnings


def _check_event(repo: Repo, eid: str, ev: dict) -> list[str]:
    s, out = repo.settings, []
    cal = ev["calendar"]

    # Dateiname und Ordner müssen zum Startdatum passen
    year, stem = eid.split("/", 1)
    if not stem.startswith(ev["start"][:10]) or year != ev["start"][:4]:
        out.append(f"Dateiname/Ordner passen nicht zum Start {ev['start']}")

    # Kalenderspezifische Felder
    if cal == "events":
        if ev.get("category") not in s["categories"]:
            out.append(f"unbekannte oder fehlende Kategorie '{ev.get('category')}'")
    elif "category" in ev:
        out.append("category nur im Kalender events erlaubt")
    if cal == "feuerwerke":
        if not ev.get("show_types"):
            out.append("show_types fehlt (Pflicht im Kalender feuerwerke)")
    elif "show_types" in ev:
        out.append("show_types nur im Kalender feuerwerke erlaubt")
    if ev.get("parent") and cal != "feuerwerke":
        out.append("parent nur im Kalender feuerwerke erlaubt")

    # Zeitmodell
    out += _check_times(ev)

    # Referenzen
    loc = repo.locations.get(ev["location"])
    if loc is None:
        out.append(f"unbekannte Location '{ev['location']}'")
    else:
        ser = find_series(loc, ev.get("series"))
        if ev.get("series") and ser is None:
            out.append(f"unbekannte Serie '{ev['series']}' in Location '{ev['location']}'")
        if ser and ser["calendar"] != cal:
            out.append(f"Serie '{ser['id']}' gehört zum Kalender {ser['calendar']}")
        level = region_level(repo, loc, cal)
        if level == "none":
            out.append(f"Region '{loc['region']}' ist für {cal} ausgeschlossen")
        elif level == "major" and not (ser and ser.get("major")):
            out.append(f"Region '{loc['region']}' erlaubt in {cal} nur Großevents (Serie mit major: true)")

    parent = ev.get("parent")
    if parent:
        if parent == eid:
            out.append("parent verweist auf sich selbst")
        elif parent not in repo.events:
            out.append(f"unbekanntes parent '{parent}'")

    if (ev.get("directions") or ev.get("viewpoints")) and not ev.get("sources"):
        out.append("directions/viewpoints ohne sources")
    return out


def _check_times(ev: dict) -> list[str]:
    out = []
    cal, all_day, start, end = ev["calendar"], ev["all_day"], ev["start"], ev.get("end")
    unknown = ev.get("time_unknown", False)
    if all_day:
        if not is_date_only(start) or (end and not is_date_only(end)):
            out.append("all_day: start/end müssen reine Daten (YYYY-MM-DD) sein")
    else:
        if is_date_only(start) or (end and is_date_only(end)):
            out.append("nicht ganztägig: start/end brauchen eine Uhrzeit (YYYY-MM-DDTHH:MM)")
    if cal in ("weihnachtsmaerkte", "events") and not all_day:
        out.append(f"Kalender {cal} erwartet ganztägige Termine")
    if cal in ("weihnachtsmaerkte", "events") and end is None:
        out.append("end fehlt")
    if cal == "feuerwerke":
        if unknown and (not all_day or (end and end != start)):
            out.append("time_unknown: ganztägig an genau einem Tag erwartet")
        if all_day and not unknown:
            out.append("Feuerwerke sind zeitgenau; ohne Uhrzeit time_unknown: true setzen")
    elif unknown:
        out.append("time_unknown nur im Kalender feuerwerke erlaubt")
    if not out and end:
        try:
            if parse_point(end) < parse_point(start):
                out.append("end liegt vor start")
        except ValueError as e:
            out.append(f"ungültige Zeitangabe: {e}")
    return out


def _duplicate_suspects(repo: Repo) -> list[str]:
    """Gleiche Location+Serie (bzw. gleicher Titel) mit überlappendem Zeitraum."""
    out, items = [], []
    for eid, ev in repo.events.items():
        if ev["status"] == "abgesagt":
            continue
        try:
            span = event_span(ev)
        except ValueError:
            continue
        key = (ev["calendar"], ev["location"], ev.get("series") or ev["title"].casefold())
        items.append((key, span, eid))
    items.sort()
    for i, (key, (s1, e1), id1) in enumerate(items):
        for key2, (s2, e2), id2 in items[i + 1:]:
            if key2 != key:
                break
            if s2 < e1 and s1 < e2:
                out.append(f"Dubletten-Verdacht: {id1} und {id2}")
    return out


# --------------------------------------------------------------------------- Rendern

def _fmt_day(d: dt.datetime) -> str:
    return d.strftime("%d.%m.%Y")


def format_period(ev: dict) -> str:
    start, end = parse_point(ev["start"]), parse_point(ev.get("end") or ev["start"])
    if ev["all_day"]:
        return _fmt_day(start) if start == end else f"{_fmt_day(start)}–{_fmt_day(end)}"
    text = f"{_fmt_day(start)} {start:%H:%M}"
    if ev.get("end"):
        text += f"–{end:%H:%M}" if end.date() == start.date() else f" – {_fmt_day(end)} {end:%H:%M}"
    return text + " Uhr"


def icon_for(settings: dict, ev: dict) -> str:
    if ev["calendar"] == "feuerwerke":
        return "".join(settings["show_types"][t]["icon"] for t in ev.get("show_types", []))
    if ev["calendar"] == "events" and ev.get("category") in settings["categories"]:
        return settings["categories"][ev["category"]]["icon"]
    return settings["calendars"][ev["calendar"]]["icon"]


def render_summary(repo: Repo, ev: dict) -> str:
    s = repo.settings
    loc_name = repo.locations[ev["location"]]["name"]
    prefix = s["display"]["status_prefix"].get(ev["status"])
    parts = [p for p in (prefix, icon_for(s, ev), f"{ev['title']} – {loc_name}") if p]
    return " ".join(parts)


STATUS_TEXT = {
    "geschätzt": "⚠️ Termin geschätzt – noch nicht offiziell bestätigt.",
    "angekündigt": "ℹ️ Termin angekündigt – Details können sich noch ändern.",
}


def render_description(repo: Repo, eid: str, ev: dict) -> str:
    """Beschreibung nach fester Vorlage (ohne Sync-Fußzeile)."""
    s, loc = repo.settings, repo.locations[ev["location"]]
    ser = find_series(loc, ev.get("series")) or {}
    blocks: list[str] = []
    if ev.get("description"):
        blocks.append(ev["description"].strip())
    lines = []
    if ev.get("opening_hours"):
        lines.append(f"🕒 Öffnungszeiten: {ev['opening_hours'].strip()}")
    lines.append(f"📍 {ev['venue']}, {loc['name']}" if ev.get("venue") else f"📍 {loc['name']}")
    if ev.get("maps_url"):
        lines.append(f"🗺️ {ev['maps_url']}")
    homepage = ev.get("homepage") or ser.get("homepage")
    if homepage:
        lines.append(f"🌐 {homepage}")
    blocks.append("\n".join(lines))
    directions = ev.get("directions") or ser.get("directions")
    if directions:
        blocks.append(f"🚶 Anfahrt/Zugang (laut Veranstalter):\n{directions.strip()}")
    viewpoints = ev.get("viewpoints") or ser.get("viewpoints")
    if viewpoints:
        blocks.append("👀 Aussichtspunkte:\n" + "\n".join(f"• {v}" for v in viewpoints))
    if ev.get("parent") and ev["parent"] in repo.events:
        p = repo.events[ev["parent"]]
        cal = s["calendars"][p["calendar"]]["name"]
        blocks.append(f"🔗 Teil von: {p['title']} ({cal}, {format_period(p)})")
    shows = sorted((cid, c) for cid, c in repo.events.items()
                   if c.get("parent") == eid and c["status"] != "abgesagt")
    if shows:
        blocks.append("🎆 Show(s):\n" + "\n".join(
            f"• {icon_for(s, c)} {c['title']} – {format_period(c)}" for _, c in shows))
    status = STATUS_TEXT.get(ev["status"])
    note = ev.get("status_note")
    if status or note:
        blocks.append(" ".join(x for x in (status, note) if x))
    blocks.append(f"Stand: {ev['checked_at']}")
    return "\n\n".join(blocks)


def _google_times(ev: dict) -> tuple[str, str]:
    start, end = event_span(ev)
    return start.strftime("%Y-%m-%dT%H:%M:00"), end.strftime("%Y-%m-%dT%H:%M:00")


def render_event(repo: Repo, eid: str, ev: dict) -> dict:
    s, loc = repo.settings, repo.locations[ev["location"]]
    start, end = _google_times(ev)
    body = {
        "summary": render_summary(repo, ev),
        "location": f"{ev['venue']}, {loc['name']}" if ev.get("venue") else loc["name"],
        "allDay": ev["all_day"],
        "startTime": start,
        "endTime": end,
        "timeZone": s["timezone"],
        "colorId": s["display"]["status_colors"].get(ev["status"]),
        "description": render_description(repo, eid, ev),
    }
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:8]
    body["description"] += f"\n\nec:{eid} · h:{digest}"
    return {
        "id": eid,
        "calendar": ev["calendar"],
        "calendarId": s["calendars"][ev["calendar"]]["google_id"],
        "hash": digest,
        **body,
        "availability": s["display"]["availability"],
        "useDefaultReminders": s["display"]["use_default_reminders"],
    }


def render(repo: Repo, calendar: str | None = None, since: dt.date | None = None) -> list[dict]:
    """Soll-Zustand: alle nicht abgesagten Events, die am/nach `since` enden."""
    out = []
    for eid, ev in sorted(repo.events.items()):
        if ev["status"] == "abgesagt" or (calendar and ev["calendar"] != calendar):
            continue
        if since and event_span(ev)[1] <= dt.datetime.combine(since, dt.time()):
            continue
        out.append(render_event(repo, eid, ev))
    return out


# --------------------------------------------------------------------------- Gerüste

_TRANSLIT = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue"})


def slugify(text: str) -> str:
    text = text.translate(_TRANSLIT).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def new_event(root: Path, calendar: str, start: str, title: str, location: str,
              series: str | None = None, end: str | None = None) -> Path:
    if calendar not in CALENDARS:
        raise ValueError(f"unbekannter Kalender '{calendar}'")
    timed = not is_date_only(start)
    eid = f"{start[:4]}/{start[:10]}-{slugify(title)}"
    path = event_path(root, eid)
    if path.exists():
        raise FileExistsError(f"{path.relative_to(root)} existiert bereits")
    data: dict = {"calendar": calendar}
    if calendar == "events":
        data["category"] = "TODO"
    if calendar == "feuerwerke":
        data["show_types"] = ["pyro"]
    data |= {
        "title": title,
        "status": "angekündigt",
        "start": start,
        "end": end if end is not None else (None if timed else start),
        "all_day": not timed,
    }
    if calendar == "feuerwerke" and not timed:
        data["time_unknown"] = True
    data["location"] = location
    if series:
        data["series"] = series
    data |= {"sources": ["https://TODO"], "checked_at": dt.date.today().isoformat()}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def new_location(root: Path, lid: str, name: str, state: str, region: str) -> Path:
    path = root / "config" / "locations" / f"{lid}.yaml"
    if path.exists():
        raise FileExistsError(f"{path.relative_to(root)} existiert bereits")
    data = {"name": name, "state": state, "region": region, "series": []}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


# --------------------------------------------------------------------------- Übersicht

def list_events(repo: Repo, calendar: str | None = None, status: str | None = None,
                since: dt.date | None = None, until: dt.date | None = None) -> list[tuple[str, dict]]:
    out = []
    for eid, ev in sorted(repo.events.items()):
        if calendar and ev["calendar"] != calendar or status and ev["status"] != status:
            continue
        start, end = event_span(ev)
        if since and end <= dt.datetime.combine(since, dt.time()):
            continue
        if until and start.date() > until:
            continue
        out.append((eid, ev))
    return out


# --------------------------------------------------------------------------- CLI

def _date(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ec", description=__doc__.splitlines()[0])
    p.add_argument("--repo", type=Path, default=REPO, help="Repo-Wurzel (Default: übergeordnetes Verzeichnis von tools/)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate", help="Daten und Konfiguration prüfen")

    r = sub.add_parser("render", help="Soll-Zustand für den Sync als JSON")
    r.add_argument("--calendar", choices=CALENDARS)
    r.add_argument("--from", dest="since", type=_date, default=dt.date.today(),
                   help="nur Termine, die am/nach diesem Datum enden (Default: heute)")
    r.add_argument("--all", action="store_true", help="auch vergangene Termine")

    e = sub.add_parser("new-event", help="Event-Gerüst anlegen")
    e.add_argument("--calendar", required=True, choices=CALENDARS)
    e.add_argument("--start", required=True, help="YYYY-MM-DD (ganztägig) oder YYYY-MM-DDTHH:MM")
    e.add_argument("--end")
    e.add_argument("--title", required=True)
    e.add_argument("--location", required=True)
    e.add_argument("--series")

    lo = sub.add_parser("new-location", help="Location-Gerüst anlegen")
    lo.add_argument("--id", required=True, dest="lid", help="Dateiname, z. B. bingen-am-rhein")
    lo.add_argument("--name", required=True)
    lo.add_argument("--state", required=True)
    lo.add_argument("--region", required=True)

    li = sub.add_parser("list", help="Übersicht")
    li.add_argument("--calendar", choices=CALENDARS)
    li.add_argument("--status", choices=["geschätzt", "angekündigt", "bestätigt", "abgesagt"])
    li.add_argument("--from", dest="since", type=_date)
    li.add_argument("--to", dest="until", type=_date)
    li.add_argument("--json", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.repo.resolve()

    if args.cmd == "new-event":
        try:
            path = new_event(root, args.calendar, args.start, args.title, args.location, args.series, args.end)
        except (ValueError, FileExistsError) as e:
            print(f"Fehler: {e}", file=sys.stderr)
            return 1
        print(path.relative_to(root))
        return 0
    if args.cmd == "new-location":
        try:
            path = new_location(root, args.lid, args.name, args.state, args.region)
        except FileExistsError as e:
            print(f"Fehler: {e}", file=sys.stderr)
            return 1
        print(path.relative_to(root))
        return 0

    repo = Repo.load(root)
    errors, warnings = validate(repo)
    for w in warnings:
        print(f"WARNUNG: {w}", file=sys.stderr)

    if args.cmd == "validate":
        for e in errors:
            print(f"FEHLER: {e}", file=sys.stderr)
        print(f"{len(repo.locations)} Locations, {len(repo.events)} Events: "
              f"{len(errors)} Fehler, {len(warnings)} Warnungen")
        return 1 if errors else 0

    if errors:  # render/list nur auf validen Daten
        for e in errors:
            print(f"FEHLER: {e}", file=sys.stderr)
        print("Abbruch: zuerst 'ec.py validate' bereinigen.", file=sys.stderr)
        return 1

    if args.cmd == "render":
        data = render(repo, args.calendar, None if args.all else args.since)
        json.dump(data, sys.stdout, ensure_ascii=False, indent=1)
        print()
        return 0

    if args.cmd == "list":
        rows = list_events(repo, args.calendar, args.status, args.since, args.until)
        if args.json:
            json.dump([{"id": i, **ev} for i, ev in rows], sys.stdout, ensure_ascii=False, indent=1)
            print()
        else:
            for eid, ev in rows:
                print(f"{ev['status']:<12} {ev['calendar']:<17} {format_period(ev):<36} {eid}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
