# Event Calendar

Verwaltet drei private Google-Kalender (Weihnachtsmärkte, Feuerwerke, Events und Feste).
**Das Repository ist führend**: Die Kalender werden ausschließlich aus `data/events/` befüllt
bzw. bereinigt. Maßgebliche Spezifikation: `docs/spec.md` (verwaltet mit `tools/specctl --root docs`),
Umsetzungsplan: `docs/tasks/` (`tools/taskctl --root docs`).

## Arbeitsablauf

Jede Session, die Daten ändert, endet mit diesen drei Schritten:

1. `python3 tools/ec.py validate` ist fehlerfrei (Warnungen zu Dubletten-Verdacht klären).
2. Commit und Push direkt auf `main`.
3. Skill `calendar-sync` ausführen und dessen Bericht ausgeben.

Aufgaben und ihre Skills:

| Aufgabe | Skill |
|---|---|
| neue Termine finden | `event-search` |
| geschätzte/angekündigte Termine prüfen, Absagen nachziehen | `event-verify` |
| Termine des Folgejahres aus den Eventserien ableiten | `series-rollover` |
| Kalender an den Repo-Stand angleichen | `calendar-sync` |

Fertige Aufträge für Sessions und Routinen liegen in `prompts/`.

## Arbeit am Umsetzungsplan (`docs/tasks/`)

Der Plan wird **sequenziell** abgearbeitet, mit dem Skill `taskctl-worker-cli` (CLI `tools/taskctl`,
Root `docs`):

1. Die nächste Task liefert ausschließlich `tools/taskctl --root docs --json next`.
2. Ist sie offen: beginnen (`~`), bearbeiten, mit `annotate` protokollieren, Ergebnis setzen.
3. Steht sie auf `R`, `C` oder `B`, ist der Plan **blockiert**: Stand berichten und auf den Nutzer warten.
   Die Abnahme einer `R`-Task setzt der Nutzer.

`--force`, `--set-status` und direkte Änderungen an `docs/tasks/` sind dem Nutzer vorbehalten.
Der PreToolUse-Hook `.claude/hooks/task-guard.py` setzt diese Regeln durch.

## Was in welchen Kalender gehört

**Weihnachtsmärkte** (`weihnachtsmaerkte`): mehrtägige Märkte von Stadt, Gemeinde oder Veranstalter,
inkl. verwandter Märkte (Sternschnuppenmarkt, Wintermärkte, Mittelalter-Weihnachtsmärkte). Märkte von
nur einem Wochenende nur bei überregionaler Bewerbung (Burg-/Schlossweihnacht). Eintägige Basare und
reine Eisbahnen/„Winterwelten“ bleiben draußen.

**Feuerwerke** (`feuerwerke`): **Shows** – Pyrotechnik, Drohnen-, Laser- und Illuminationsshows
(`show_types`). Silvester nur offiziell und öffentlich. Pro Datum und Ort ein eigener Termin. Zeit und
Ort beziehen sich auf die Show selbst; das übergeordnete Event steht in `parent`.

**Events und Feste** (`events`): Kategorien aus `config/settings.yaml` – Großevents mit saisonalem,
regionalem oder historischem Bezug, Jahrmärkte mit Fahrgeschäften, regionale Ausstellungen, Paraden und
Umzüge, Weinfeste, Mittelalter-/Historienfeste, Lichtfeste, Stadt- und Hafenfeste, Saisonmärkte außer
Weihnachten. Kerben und Dorffeste bleiben draußen. Ein mehrtägiges Lichtfest steht hier; seine zeitlich
festgelegte Show zusätzlich im Kalender Feuerwerke.

## Region

Jede Location (`config/locations/<ort>.yaml`, eine Stadt oder Gemeinde) hat eine `region`.
`config/settings.yaml` legt je Region und Kalender die Stufe fest: `all`, `major` (nur Serien mit
`major: true`, d. h. überregional bekannt) oder `none`. `include: true`/`exclude: true` an der Location
übersteuern das. Zuordnung neuer Orte:

- `rhein-main`: Frankfurt, Offenbach, Wiesbaden, Mainz, Darmstadt, Hanau, Hochheim, Taunus, Wetterau, Aschaffenburg
- `rheingau-mittelrhein`: Rheingau, Bingen, Mittelrhein bis Koblenz
- `rheinhessen-pfalz`: Worms, Alzey, Bad Dürkheim, Speyer
- `rhein-neckar`: Mannheim, Heidelberg, Weinheim
- `rheinland`: Köln, Düsseldorf, Bonn
- `sonstige`: alles andere (u. a. Odenwald, Spessart)

`ec.py validate` weist Termine außerhalb der zulässigen Stufe zurück.

## Status eines Termins

- `bestätigt`: Veranstalter oder Stadt nennt das Datum für dieses Jahr ausdrücklich.
- `angekündigt`: Datum aus Sekundärquelle (Portal, Presse) oder vom Veranstalter als vorläufig genannt.
- `geschätzt`: aus Vorjahresmuster bzw. `typical_period` abgeleitet; Begründung in `status_note`.
- `abgesagt`: bleibt im Repo, `calendar-sync` löscht ihn aus dem Kalender.

## Herkunft der Inhalte

- Jede Angabe stammt aus einer Quelle in `sources`; `checked_at` ist das Datum der letzten Prüfung.
- Keine Reisevorschläge und keine Anfahrt ab Frankfurt.
- `directions` nur, wenn die Eventseite selbst Anfahrts-/Zugangshinweise gibt (z. B. Dippemess).
- `viewpoints` nur aus Veranstalter- oder veröffentlichten Quellen (Stadtmarketing, Lokalpresse),
  nie selbst ausgedacht.

## Dateien und Werkzeuge

- Event-ID = Pfad unter `data/events/` ohne Endung, z. B. `2026/2026-07-04-rhein-in-flammen`;
  Gerüst mit `ec.py new-event`, Location mit `ec.py new-location` (Optionen: `--help`).
- Zeitmodell: Weihnachtsmärkte und Events ganztägig (`start`/`end` als Datum, `end` inklusive);
  Feuerwerke zeitgenau (`YYYY-MM-DDTHH:MM`, `end: null` = Start + 30 min), ohne bekannte Uhrzeit
  ganztägig mit `time_unknown: true`.
- Felder und erlaubte Werte: `schemas/*.schema.json`.
- Tests: `python3 -m unittest discover -s tests`.
- Python-Pakete und `tools/specctl`/`tools/taskctl` stellt der SessionStart-Hook bereit
  (`.claude/hooks/session-start.sh`, gepinnter Commit der ai-architecture-tools).
