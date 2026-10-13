"""Tests für tools/ec.py – laufen gegen ein temporäres Mini-Repo."""
import datetime as dt
import io
import shutil
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import ec  # noqa: E402

BINGEN = """
name: Bingen am Rhein
state: Rheinland-Pfalz
region: rheingau-mittelrhein
series:
  - id: rhein-in-flammen
    name: Rhein in Flammen
    calendar: feuerwerke
    major: true
    homepage: https://www.rhein-in-flammen.com/
  - id: winzerfest
    name: Binger Winzerfest
    calendar: events
    category: weinfest
"""

KOELN = """
name: Köln
state: Nordrhein-Westfalen
region: rheinland
series:
  - id: koelner-lichter
    name: Kölner Lichter
    calendar: feuerwerke
  - id: ringfest
    name: Ringfest
    calendar: events
    category: stadtfest
  - id: karneval
    name: Kölner Karneval
    calendar: events
    category: parade
    major: true
"""

FEST = """
calendar: events
category: weinfest
title: Binger Winzerfest
status: bestätigt
start: 2027-09-03
end: 2027-09-12
all_day: true
location: bingen
series: winzerfest
opening_hours: täglich 11–23 Uhr
sources: [https://example.org/winzerfest]
checked_at: 2027-06-01
"""

SHOW = """
calendar: feuerwerke
show_types: [pyro, drone]
title: Abschlussfeuerwerk Winzerfest
status: angekündigt
start: 2027-09-12T21:30
end: null
all_day: false
location: bingen
series: rhein-in-flammen
parent: 2027/2027-09-03-binger-winzerfest
viewpoints: [Kulturufer Bingen]
sources: [https://example.org/winzerfest]
checked_at: 2027-06-01
"""


class RepoCase(unittest.TestCase):
    """Legt pro Test ein Mini-Repo mit echten Schemas und Settings an."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(REPO / "schemas", self.tmp / "schemas")
        (self.tmp / "config" / "locations").mkdir(parents=True)
        shutil.copy(REPO / "config" / "settings.yaml", self.tmp / "config" / "settings.yaml")
        self.write("config/locations/bingen.yaml", BINGEN)
        self.write("config/locations/koeln.yaml", KOELN)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, rel, text):
        path = self.tmp / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")
        return path

    def event(self, eid, text, **overrides):
        body = textwrap.dedent(text).lstrip()
        for key, value in overrides.items():
            lines = [ln for ln in body.splitlines() if not ln.startswith(f"{key}:")]
            if value is not None:
                lines.append(f"{key}: {value}")
            body = "\n".join(lines) + "\n"
        return self.write(f"data/events/{eid}.yaml", body)

    def load(self):
        return ec.Repo.load(self.tmp)

    def errors(self):
        return ec.validate(self.load())[0]


class TestValidate(RepoCase):
    def test_valid_repo(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST)
        self.event("2027/2027-09-12-abschlussfeuerwerk-winzerfest", SHOW)
        errors, warnings = ec.validate(self.load())
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_dates_stay_strings(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST)
        ev = self.load().events["2027/2027-09-03-binger-winzerfest"]
        self.assertEqual(ev["start"], "2027-09-03")

    def test_schema_error_reported(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST, status="vielleicht")
        self.assertTrue(any("status" in e for e in self.errors()))

    def test_filename_must_match_start(self):
        self.event("2027/2027-09-04-binger-winzerfest", FEST)
        self.assertTrue(any("Dateiname" in e for e in self.errors()))

    def test_unknown_location_series_parent(self):
        self.event("2027/2027-09-12-abschlussfeuerwerk-winzerfest", SHOW,
                   series="gibtsnicht", parent="2027/2027-01-01-fehlt")
        errs = self.errors()
        self.assertTrue(any("unbekannte Serie" in e for e in errs))
        self.assertTrue(any("unbekanntes parent" in e for e in errs))

    def test_category_rules(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST, category="quatsch")
        self.assertTrue(any("Kategorie" in e for e in self.errors()))

    def test_show_types_required_for_fireworks(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST)
        self.event("2027/2027-09-12-abschlussfeuerwerk-winzerfest", SHOW, show_types=None)
        self.assertTrue(any("show_types fehlt" in e for e in self.errors()))

    def test_events_calendar_must_be_all_day(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST,
                   start="2027-09-03T10:00", end="2027-09-12T23:00", all_day="false")
        self.assertTrue(any("ganztägige" in e for e in self.errors()))

    def test_firework_without_time_needs_time_unknown(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST)
        self.event("2027/2027-09-12-abschlussfeuerwerk-winzerfest", SHOW,
                   start="2027-09-12", end="2027-09-12", all_day="true")
        self.assertTrue(any("time_unknown" in e for e in self.errors()))
        self.event("2027/2027-09-12-abschlussfeuerwerk-winzerfest", SHOW,
                   start="2027-09-12", end="2027-09-12", all_day="true", time_unknown="true")
        self.assertEqual(self.errors(), [])

    def test_end_before_start(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST, end="2027-09-01")
        self.assertTrue(any("end liegt vor start" in e for e in self.errors()))

    def test_region_major_only(self):
        ringfest = FEST.replace("bingen", "koeln").replace("winzerfest", "ringfest").replace("weinfest", "stadtfest")
        self.event("2027/2027-09-03-binger-winzerfest", ringfest)
        self.assertTrue(any("nur Großevents" in e for e in self.errors()))

    def test_region_major_allowed_with_major_series(self):
        karneval = FEST.replace("bingen", "koeln").replace("series: winzerfest", "series: karneval") \
                       .replace("weinfest", "parade")
        self.event("2027/2027-09-03-binger-winzerfest", karneval)
        self.assertEqual(self.errors(), [])

    def test_region_none_and_include_override(self):
        self.write("config/locations/berlin.yaml",
                   "name: Berlin\nstate: Berlin\nregion: sonstige\n")
        self.event("2027/2027-09-03-binger-winzerfest", FEST.replace("series: winzerfest\n", ""),
                   location="berlin")
        self.assertTrue(any("ausgeschlossen" in e for e in self.errors()))
        self.write("config/locations/berlin.yaml",
                   "name: Berlin\nstate: Berlin\nregion: sonstige\ninclude: true\n")
        self.assertEqual(self.errors(), [])

    def test_exclude_overrides_region(self):
        self.write("config/locations/bingen.yaml", BINGEN + "exclude: true\n")
        self.event("2027/2027-09-03-binger-winzerfest", FEST)
        self.assertTrue(any("ausgeschlossen" in e for e in self.errors()))

    def test_parent_only_for_fireworks(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST, parent="2027/2027-09-03-binger-winzerfest")
        self.assertTrue(any("parent nur" in e for e in self.errors()))

    def test_duplicate_suspect_warning(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST)
        self.event("2027/2027-09-05-binger-winzerfest-2", FEST, start="2027-09-05")
        _, warnings = ec.validate(self.load())
        self.assertEqual(len(warnings), 1)
        self.assertIn("Dubletten-Verdacht", warnings[0])


class TestRender(RepoCase):
    def setUp(self):
        super().setUp()
        self.event("2027/2027-09-03-binger-winzerfest", FEST)
        self.event("2027/2027-09-12-abschlussfeuerwerk-winzerfest", SHOW)

    def rendered(self, **kw):
        return {r["id"]: r for r in ec.render(self.load(), **kw)}

    def test_summary_icons_and_prefix(self):
        r = self.rendered()
        self.assertEqual(r["2027/2027-09-03-binger-winzerfest"]["summary"], "🍷 Binger Winzerfest – Bingen am Rhein")
        self.assertEqual(r["2027/2027-09-12-abschlussfeuerwerk-winzerfest"]["summary"],
                         "🎆🛸 Abschlussfeuerwerk Winzerfest – Bingen am Rhein")
        self.event("2027/2027-09-03-binger-winzerfest", FEST, status="geschätzt")
        fest = self.rendered()["2027/2027-09-03-binger-winzerfest"]
        self.assertTrue(fest["summary"].startswith("❓ 🍷"))
        self.assertEqual(fest["colorId"], "8")

    def test_all_day_end_is_exclusive(self):
        fest = self.rendered()["2027/2027-09-03-binger-winzerfest"]
        self.assertTrue(fest["allDay"])
        self.assertEqual(fest["startTime"], "2027-09-03T00:00:00")
        self.assertEqual(fest["endTime"], "2027-09-13T00:00:00")

    def test_firework_default_duration_and_timezone(self):
        show = self.rendered()["2027/2027-09-12-abschlussfeuerwerk-winzerfest"]
        self.assertEqual(show["startTime"], "2027-09-12T21:30:00")
        self.assertEqual(show["endTime"], "2027-09-12T22:00:00")
        self.assertEqual(show["timeZone"], "Europe/Berlin")
        self.assertEqual(show["availability"], "AVAILABILITY_FREE")
        self.assertFalse(show["useDefaultReminders"])

    def test_description_links_parent_and_shows(self):
        r = self.rendered()
        self.assertIn("🔗 Teil von: Binger Winzerfest (Events und Feste, 03.09.2027–12.09.2027)",
                      r["2027/2027-09-12-abschlussfeuerwerk-winzerfest"]["description"])
        self.assertIn("Abschlussfeuerwerk Winzerfest – 12.09.2027 21:30 Uhr",
                      r["2027/2027-09-03-binger-winzerfest"]["description"])
        self.assertIn("• Kulturufer Bingen", r["2027/2027-09-12-abschlussfeuerwerk-winzerfest"]["description"])
        # Homepage kommt aus der Serie, wenn das Event keine eigene hat
        self.assertIn("https://www.rhein-in-flammen.com/",
                      r["2027/2027-09-12-abschlussfeuerwerk-winzerfest"]["description"])

    def test_footer_and_hash(self):
        fest = self.rendered()["2027/2027-09-03-binger-winzerfest"]
        m = ec.FOOTER_RE.search(fest["description"])
        self.assertEqual(m["id"], "2027/2027-09-03-binger-winzerfest")
        self.assertEqual(m["hash"], fest["hash"])

    def test_hash_stable_and_content_sensitive(self):
        h1 = self.rendered()["2027/2027-09-03-binger-winzerfest"]["hash"]
        self.assertEqual(h1, self.rendered()["2027/2027-09-03-binger-winzerfest"]["hash"])
        self.event("2027/2027-09-03-binger-winzerfest", FEST, opening_hours="täglich 12–22 Uhr")
        self.assertNotEqual(h1, self.rendered()["2027/2027-09-03-binger-winzerfest"]["hash"])

    def test_cancelled_and_past_are_excluded(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST, status="abgesagt")
        r = self.rendered()
        self.assertNotIn("2027/2027-09-03-binger-winzerfest", r)
        self.assertNotIn("Show(s)", r.get("2027/2027-09-03-binger-winzerfest", {}).get("description", ""))
        self.event("2027/2027-09-03-binger-winzerfest", FEST)
        self.assertEqual(self.rendered(since=dt.date(2027, 9, 13)), {})
        self.assertEqual(len(self.rendered(since=dt.date(2027, 9, 12))), 2)

    def test_calendar_filter(self):
        self.assertEqual(list(self.rendered(calendar="feuerwerke")),
                         ["2027/2027-09-12-abschlussfeuerwerk-winzerfest"])


class TestScaffoldAndList(RepoCase):
    def test_slugify(self):
        self.assertEqual(ec.slugify("Weihnachtsmarkt der Nationen – Rüdesheim"),
                         "weihnachtsmarkt-der-nationen-ruedesheim")
        self.assertEqual(ec.slugify("Große Straße"), "grosse-strasse")

    def test_new_event_creates_valid_skeleton(self):
        path = ec.new_event(self.tmp, "feuerwerke", "2027-07-03T22:30", "Rhein in Flammen", "bingen",
                            series="rhein-in-flammen")
        self.assertEqual(path.relative_to(self.tmp).as_posix(),
                         "data/events/2027/2027-07-03-rhein-in-flammen.yaml")
        repo = self.load()
        self.assertEqual(repo.errors, [])
        # Platzhalter-URL ist schema-gültig, wird aber im Review sichtbar
        self.assertEqual(repo.events["2027/2027-07-03-rhein-in-flammen"]["sources"], ["https://TODO"])
        with self.assertRaises(FileExistsError):
            ec.new_event(self.tmp, "feuerwerke", "2027-07-03T22:30", "Rhein in Flammen", "bingen")

    def test_new_event_all_day_firework_sets_time_unknown(self):
        ec.new_event(self.tmp, "feuerwerke", "2027-07-03", "Sommerfeuerwerk", "bingen")
        self.assertEqual(self.errors(), [])

    def test_new_event_events_needs_category(self):
        ec.new_event(self.tmp, "events", "2027-09-03", "Winzerfest", "bingen", end="2027-09-12")
        self.assertTrue(any("Kategorie" in e for e in self.errors()))

    def test_new_location(self):
        path = ec.new_location(self.tmp, "mainz", "Mainz", "Rheinland-Pfalz", "rhein-main")
        self.assertTrue(path.exists())
        self.assertIn("mainz", self.load().locations)

    def test_list_filters(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST, status="geschätzt")
        self.event("2027/2027-09-12-abschlussfeuerwerk-winzerfest", SHOW)
        repo = self.load()
        self.assertEqual([i for i, _ in ec.list_events(repo, status="geschätzt")],
                         ["2027/2027-09-03-binger-winzerfest"])
        self.assertEqual(len(ec.list_events(repo, calendar="feuerwerke")), 1)
        self.assertEqual(ec.list_events(repo, until=dt.date(2027, 9, 2)), [])


class TestCli(RepoCase):
    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = ec.main(["--repo", str(self.tmp), *args])
        return rc, out.getvalue(), err.getvalue()

    def test_validate_exit_codes(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST)
        self.assertEqual(self.run_cli("validate")[0], 0)
        self.event("2027/2027-09-03-binger-winzerfest", FEST, status="kaputt")
        rc, _, err = self.run_cli("validate")
        self.assertEqual(rc, 1)
        self.assertIn("FEHLER", err)

    def test_render_refuses_invalid_data(self):
        self.event("2027/2027-09-03-binger-winzerfest", FEST, status="kaputt")
        self.assertEqual(self.run_cli("render", "--all")[0], 1)

    def test_render_json(self):
        import json
        self.event("2027/2027-09-03-binger-winzerfest", FEST)
        rc, out, _ = self.run_cli("render", "--from", "2027-01-01")
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)[0]["id"], "2027/2027-09-03-binger-winzerfest")

    def test_repo_settings_are_valid(self):
        """Die echte config/settings.yaml des Repos muss schema-gültig sein."""
        repo = ec.Repo.load(REPO)
        self.assertEqual([e for e in repo.errors if e.startswith("config/settings")], [])


if __name__ == "__main__":
    unittest.main()
