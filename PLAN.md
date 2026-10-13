# Event Calendar – Umsetzungsplan

Ergebnis der Planungssitzung. Grundsatz: **Das Repository ist führend**, die Google-Kalender
werden ausschließlich aus den hier abgelegten Daten befüllt bzw. bereinigt. Alle Abläufe
müssen vollständig über das Claude-Code-Webinterface durchführbar sein.

## 1. Kalender

| Kalender | Google-Kalender | Inhalt | Zeitmodell |
|---|---|---|---|
| Weihnachtsmärkte | `Weihnachtsmärkte` | Mehrtägige Märkte von Stadt, Gemeinde oder Veranstalter inkl. verwandter Märkte (Sternschnuppenmarkt, Wintermärkte, Mittelalter-Weihnachtsmärkte). Märkte von nur einem Wochenende nur bei überregionaler Bewerbung (z. B. Burg-/Schlossweihnacht). **Nicht:** eintägige Gemeinde-/Vereinsbasare, reine Eisbahnen/„Winterwelten“ ohne Marktcharakter. | ganztägig, mehrtägig |
| Feuerwerke | `Feuerwerke` | Shows: Pyrotechnik, Drohnen-, Laser- und Illuminationsshows. Silvester nur offiziell und öffentlich. **Pro Datum und Ort ein eigener Termin.** Zeit und Ort beziehen sich auf die Show selbst; optionaler Verweis (`parent`) auf das übergeordnete Event in einem beliebigen Kalender. | zeitgenau; ohne Endzeit Start + 30 min; ohne bekannte Uhrzeit ganztägig mit `time_unknown` |
| Events und Feste | `Veranstaltungen` | Kategorien siehe unten. Keine Weihnachtsmärkte, keine Kerben/Dorffeste. Events mit Show verweisen auf den Termin im Feuerwerkskalender. | ganztägig, mehrtägig (Öffnungszeiten in der Beschreibung) |

### Kategorien „Events und Feste“

- Großevents mit saisonalem, regionalem oder historischem Bezug
- Jahrmärkte mit Fahrgeschäften
- Regionale Ausstellungen (Bundes-/Landesgartenschau, Rheinland-Pfalz-Ausstellung, Hochheimer Markt)
- Paraden und Umzüge (CSD, Fastnachtsumzüge, …)
- Weinfeste
- Mittelalter- und Historienfeste
- Lichtfeste (mehrtägig; zeitlich festgelegte Shows gehen zusätzlich als eigener Termin in den Feuerwerkskalender, Lichtfeste ohne feste Show nur hier)
- Stadt- und Hafenfeste
- Saisonmärkte außer Weihnachten (Ostermärkte, Kürbis-/Erntefeste)

### Show-Icons (Feuerwerkskalender, kombinierbar, z. B. `🎆🛸`)

| Typ | Icon |
|---|---|
| Feuerwerk (Pyrotechnik) | 🎆 |
| Drohnenshow | 🛸 |
| Lasershow | 🔦 |
| Illumination | 💡 |

Weitere Kalender-Icons: 🎄 Weihnachtsmärkte, 🎡 Events und Feste (ggf. je Kategorie verfeinert in `settings.yaml`).

## 2. Regionen

Keine Reisezeitermittlung, keine Anfahrtsbeschreibung ab Frankfurt. Jede Location hat ein Feld
`region`; `settings.yaml` legt pro Region und Kalender die Stufe fest (`alle` | `nur Großevents` | `keine`).

| Region | Orte (Beispiele) | Weihnachtsmärkte | Events und Feste | Feuerwerke |
|---|---|---|---|---|
| Rhein-Main | Frankfurt, Offenbach, Wiesbaden, Mainz, Darmstadt, Hanau, Hochheim, Taunus (Bad Homburg, Königstein, Idstein), Wetterau (Friedberg, Bad Nauheim), Aschaffenburg | alle | alle | alle |
| Rheingau / Mittelrhein | Rüdesheim, Eltville, Bingen, Bacharach, Koblenz | alle | alle | alle |
| Rheinhessen / Pfalz | Worms, Alzey, Bad Dürkheim, Speyer | alle | alle | alle |
| Rhein-Neckar | Mannheim, Heidelberg, Weinheim | alle | alle | alle |
| Rheinland | Köln, Düsseldorf, Bonn | keine | nur Großevents | alle |
| sonstige | Odenwald, Spessart, Berlin, … | keine | keine | keine |

- **Großevent** = überregional bekannt. Markiert als `major: true` an der Eventserie der Location.
- Ausnahmen über `include: true` / `exclude: true` pro Location (z. B. einzelne Orte im Odenwald).

## 3. Datenablage im Repository

```
CLAUDE.md                              # Grundregeln, Kategorie-Definitionen, Arbeitsablauf
PLAN.md                                # dieses Dokument
requirements.txt                       # pyyaml, jsonschema
.claude/settings.json                  # SessionStart-Hook: pip install -r requirements.txt
.claude/skills/
  event-search/SKILL.md
  event-verify/SKILL.md
  series-rollover/SKILL.md
  calendar-sync/SKILL.md
config/settings.yaml                   # Kalender-IDs, Regionen × Kalender-Stufen, Kategorien, Icons, Suchhorizont
config/locations/<ort>.yaml            # Orte + Eventserien
data/events/<jahr>/<datum>-<slug>.yaml # ein Termin = eine Datei
schemas/{event,location,settings}.schema.json
tools/ec.py                            # CLI (Python, Abhängigkeiten erlaubt)
tests/
prompts/*.md                           # fertige Aufträge für Sessions und Routinen
```

- Format: **YAML**, validiert per JSON-Schema. JSON-Schlüssel englisch, Inhalte deutsch.
- **Event-ID** = Pfad ohne Endung, z. B. `2026/2026-07-04-feuerwerk-rhein-in-flammen-bingen`.
  Dient als Sync-Schlüssel und als Ziel von `parent`-Referenzen.
- Vergangene Events bleiben im Repo als Historie.

### Event (`data/events/…`)

| Feld | Bedeutung |
|---|---|
| `calendar` | `weihnachtsmaerkte` \| `feuerwerke` \| `events` |
| `category` | Kategorie (nur `events`) |
| `show_types` | Liste aus `pyro`, `drone`, `laser`, `illumination` (nur `feuerwerke`) |
| `title` | Name ohne Icon/Präfix |
| `status` | `geschätzt` \| `angekündigt` \| `bestätigt` \| `abgesagt` |
| `start`, `end`, `all_day`, `time_unknown` | Zeitangaben gemäß Zeitmodell |
| `location`, `series` | Referenz auf Location und Eventserie |
| `venue`, `maps_url`, `homepage` | konkreter Platz, Karte, offizielle Seite |
| `description`, `opening_hours` | Freitext, Öffnungszeiten |
| `directions` | lokale Anfahrt/Zugang – **nur** wenn die Eventseite selbst welche anbietet (z. B. Dippemess) |
| `viewpoints` | Aussichtspunkte – nur aus Veranstalter- oder veröffentlichten Quellen (Stadtmarketing, Lokalpresse), nie vom Agenten erfunden |
| `parent` | Event-ID des übergeordneten Events (optional, beliebiger Kalender) |
| `sources`, `checked_at` | Nachweis-URLs, Datum der letzten Prüfung |

### Location (`config/locations/<ort>.yaml`)

- `name`, `state` (Bundesland), `region`, `include`/`exclude`
- `series`: Liste der Eventserien mit `id`, `name`, `calendar`, `category`, `major`, `homepage`,
  `sources` (Such-URLs), `typical_period` (z. B. „1. Juli-Wochenende“), `has_fireworks`,
  Default-`directions`/`viewpoints`
- Location = Stadt/Gemeinde; konkrete Plätze stehen im Event (`venue`). Events über mehrere Orte
  hängen an einer Haupt-Location.

## 4. Konfiguration (`config/settings.yaml`)

- Google-Kalender-IDs der drei Kalender
- Regionen und Stufen je Kalender (Tabelle Abschnitt 2)
- Kategorien und Icons
- Suchhorizont: 12 Monate ab heute; Weihnachtsmärkte immer für die kommende Saison
- Darstellung: keine Erinnerungen, Verfügbarkeit „frei“, Farbe grau für `geschätzt`

## 5. Darstellung im Kalender

- Titel: `<Icon> <Name> – <Ort>`; Präfix `❓` bei `geschätzt`
- Beschreibung aus fester Vorlage, gerendert von `ec.py`: Kurzbeschreibung, Öffnungszeiten,
  Ort/Maps, Homepage, ggf. lokale Anfahrt, ggf. Aussichtspunkte, ggf. „Teil von: <Event> (<Kalender>, <Zeitraum>)“
  bzw. „Show(s): …“, Status-/Unsicherheitshinweis. **Keine** Reisevorschläge.
- Letzte Zeile: Sync-Fußzeile `ec:<id> · h:<hash>`
- Verknüpfungen nur als Text, keine Google-Event-IDs im Repo.

## 6. Tools (`tools/ec.py`)

| Befehl | Zweck |
|---|---|
| `validate` | Schema, Pflichtfelder, Referenzen (`location`, `series`, `parent`), Zeiten, Region/Stufe zulässig, Dubletten-Verdacht (gleiche Location+Serie, überlappender Zeitraum) |
| `render [--calendar X] [--from heute]` | Soll-Zustand als kompaktes JSON (Titel, Zeiten, Beschreibung, Farbe, Hash) für den Sync |
| `new-event` / `new-location` | Gerüst mit korrektem Dateinamen/ID |
| `list` | Übersichten, z. B. alle `geschätzt`-Termine der nächsten 3 Monate |

Tests mit `pytest` oder `unittest` unter `tests/`.

## 7. Skills

| Skill | Aufgabe |
|---|---|
| `event-search` | Neue Termine recherchieren (Filter: Kalender, Zeitraum, Region); Events und ggf. Locations/Serien anlegen; Feuerwerke separat mit `parent` |
| `event-verify` | `geschätzt`/`angekündigt` prüfen, Status hochstufen, Änderungen und Absagen nachziehen, `checked_at` setzen |
| `series-rollover` | Aus den Eventserien der Locations die Termine des Folgejahres ableiten und recherchieren |
| `calendar-sync` | `ec.py render --from heute` → Kalender per Google-Calendar-MCP ab heute listen → Abgleich über `ec:`-Schlüssel und Hash: neu → anlegen, Hash geändert → aktualisieren, Schlüssel fehlt im Soll oder `abgesagt` → löschen. Vergangene Termine nie anfassen. Bericht ausgeben. |

`CLAUDE.md` enthält die Grundregeln: Repo führend; nach jeder Datenänderung `validate` → Sync →
Bericht; Kategorie- und Regionsdefinitionen; Herkunftsregeln für `directions`/`viewpoints`.

## 8. Prompts (`prompts/*.md`)

Kurze, fertige Aufträge, die auf die Skills verweisen – zum Einfügen in eine Web-Session oder als
Routine-Text, z. B.:

- `search-weihnachtsmaerkte.md`, `search-feuerwerke.md`, `search-events.md`
- `verify-upcoming.md`
- `rollover-next-year.md`
- `sync-all.md`

## 9. Arbeitsweise

- Agent committet **direkt auf `main`**.
- Jede Session mit Datenänderung endet mit `validate`, Sync und Bericht.
- Sync über den Google-Calendar-MCP-Connector (keine Secrets nötig). Fallback bei Problemen mit vielen
  Terminen: direktes Skript gegen die Google Calendar API (OAuth-Refresh-Token als Umgebungs-Secret).

## 10. Phasen

1. **Gerüst:** Struktur, `CLAUDE.md`, Schemas, `settings.yaml`, `ec.py` mit Tests, SessionStart-Hook
2. **Skills `event-search` und `calendar-sync`** + Prompts; erste Suche je Kalender, erster Sync
3. **Skills `event-verify` und `series-rollover`** + Prompts
4. **Routinen:** Weihnachtsmärkte Juli–Oktober, Feuerwerke und Events monatlich, jährlicher Rollover

## Manuelle Schritte (Nutzer)

- Zeitzone des Kalenders `Feuerwerke` von UTC auf Europe/Berlin umstellen.
- Bestehende Termine in allen drei Kalendern vor dem ersten echten Sync löschen
  (sie werden nicht importiert; der Sync würde Termine ohne `ec:`-Schlüssel ab heute ohnehin löschen).
