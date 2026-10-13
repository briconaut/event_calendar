# Event Calendar – Spezifikation

Ergebnis der Planungssitzung vom 2026-10-13. Grundsatz: **Das Repository ist führend**, die Google-Kalender werden ausschließlich aus den hier abgelegten Daten befüllt bzw. bereinigt. Umsetzungsplan: taskctl-Store unter `docs/tasks/`.

## Ziel und Randbedingungen

<!-- specctl id=c76b83 type=Ziel nr=001 status=draft
history:
- 2026-10-13T11:24:26+00:00: M | Add
-->

Das Repository verwaltet drei private Google-Kalender (Feuerwerke, Weihnachtsmärkte, Events und Feste).
Es enthält Skills, Event-Daten, Prompts, Hilfsskripte und die Konfiguration der Eventsuche.

- Die Kalender werden ausschließlich von den hier abgelegten Tools bzw. den KI-Agenten, die sie nutzen, geschrieben.
- Alle Abläufe müssen vollständig über das Claude-Code-Webinterface durchführbar sein.
- Bestehende Termine in den Kalendern werden **nicht** importiert; der Nutzer löscht sie vor dem ersten echten Lauf.
- Keine Reisevorschläge und keine Anfahrtsbeschreibungen ab Frankfurt.

## Kalender

<!-- specctl id=e9a6b4 type=Kalend nr=002 status=draft
history:
- 2026-10-13T11:24:27+00:00: M | Add
-->

| Kalender | Google-Kalender | Zeitmodell |
|---|---|---|
| Weihnachtsmärkte | `Weihnachtsmärkte` | ganztägig, mehrtägig |
| Feuerwerke | `Feuerwerke` | zeitgenau |
| Events und Feste | `Veranstaltungen` | ganztägig, mehrtägig |

Öffnungszeiten stehen bei ganztägigen Terminen in der Beschreibung. Unterbrechungen
(z. B. „Totensonntag geschlossen“) werden nur im Text vermerkt, nicht als Lücke im Kalender.

### Weihnachtsmärkte

<!-- specctl id=dd93f0 type=KalWei nr=001 status=draft
history:
- 2026-10-13T11:24:27+00:00: M | Add
-->

**Aufnehmen:**

- mehrtägige Märkte von Stadt, Gemeinde oder Veranstalter, inkl. verwandter Märkte
  (Sternschnuppenmarkt, Wintermärkte, Mittelalter-Weihnachtsmärkte)
- Märkte von nur einem Wochenende, wenn sie überregional beworben werden (z. B. Burg-/Schlossweihnacht)

**Nicht aufnehmen:** eintägige Gemeinde-/Vereinsbasare, reine Eisbahnen/„Winterwelten“ ohne Marktcharakter.

Icon: 🎄

### Feuerwerke

<!-- specctl id=ffdcf2 type=KalFeu nr=002 status=draft
history:
- 2026-10-13T11:24:27+00:00: M | Add
-->

Der Kalender enthält **Shows**: Pyrotechnik, Drohnen-, Laser- und Illuminationsshows.

- Silvester nur, wenn offiziell und öffentlich.
- Pro Datum und Ort ein eigener Termin (z. B. Schlossbeleuchtung Juni/Juli/September, Rhein in Flammen je Ort).
- Zeit und Ort beziehen sich auf die Show selbst, nicht auf das übergeordnete Event.
- Optionaler Verweis (`parent`) auf das übergeordnete Event in einem beliebigen Kalender (auch Weihnachtsmärkte).
- Zeitmodell: zeitgenau; ohne bekannte Endzeit Start + 30 min; ohne bekannte Uhrzeit ganztägig mit `time_unknown`.

#### Show-Icons

<!-- specctl id=4318fe type=KaFeSh nr=001 status=draft
history:
- 2026-10-13T11:24:27+00:00: M | Add
-->

Icons sind kombinierbar (z. B. `🎆🛸`):

| Typ | Wert `show_types` | Icon |
|---|---|---|
| Feuerwerk (Pyrotechnik) | `pyro` | 🎆 |
| Drohnenshow | `drone` | 🛸 |
| Lasershow | `laser` | 🔦 |
| Illumination | `illumination` | 💡 |

### Events und Feste

<!-- specctl id=614937 type=KalEve nr=003 status=draft
history:
- 2026-10-13T11:24:27+00:00: M | Add
-->

Keine Weihnachtsmärkte, keine Kerben/Dorffeste. Events, die eine Show enthalten, verweisen auf
den bzw. die Termine im Feuerwerkskalender. Icon je Kategorie (siehe `settings.yaml`).

#### Kategorien

<!-- specctl id=b0b879 type=KaEvKa nr=001 status=draft
history:
- 2026-10-13T11:24:27+00:00: M | Add
-->

- Großevents mit saisonalem, regionalem oder historischem Bezug
- Jahrmärkte mit Fahrgeschäften
- Regionale Ausstellungen (Bundes-/Landesgartenschau, Rheinland-Pfalz-Ausstellung, Hochheimer Markt)
- Paraden und Umzüge (CSD, Fastnachtsumzüge, …)
- Weinfeste
- Mittelalter- und Historienfeste
- Lichtfeste
- Stadt- und Hafenfeste
- Saisonmärkte außer Weihnachten (Ostermärkte, Kürbis-/Erntefeste)

#### Lichtfeste und Illuminationen

<!-- specctl id=b4b244 type=KaEvLi nr=002 status=draft
history:
- 2026-10-13T11:24:27+00:00: M | Add
-->

Gleiches Muster wie bei Feuerwerken: Die zeitlich festgelegte **Show** (z. B. Schlossbeleuchtung,
Lichtshow am Dom) kommt zeitgenau in den Feuerwerkskalender. Ein mehrtägiges **Lichtfest**
(z. B. Luminale) kommt als übergeordnetes Event nach „Events und Feste“ und verweist auf die Show(s).
Ein Lichtfest ohne zeitlich festgelegte Show (begehbare Installation) steht nur in „Events und Feste“.

## Regionen

<!-- specctl id=1ea0e6 type=Region nr=003 status=draft
history:
- 2026-10-13T11:24:27+00:00: M | Add
-->

Es werden keine Reisezeiten ermittelt. Jede Location hat ein Feld `region`; `settings.yaml` legt pro
Region und Kalender die Stufe fest: `all` | `major` (nur Großevents) | `none`.

| Region | Orte (Beispiele) | Weihnachtsmärkte | Events und Feste | Feuerwerke |
|---|---|---|---|---|
| Rhein-Main | Frankfurt, Offenbach, Wiesbaden, Mainz, Darmstadt, Hanau, Hochheim, Taunus (Bad Homburg, Königstein, Idstein), Wetterau (Friedberg, Bad Nauheim), Aschaffenburg | all | all | all |
| Rheingau / Mittelrhein | Rüdesheim, Eltville, Bingen, Bacharach, Koblenz | all | all | all |
| Rheinhessen / Pfalz | Worms, Alzey, Bad Dürkheim, Speyer | all | all | all |
| Rhein-Neckar | Mannheim, Heidelberg, Weinheim | all | all | all |
| Rheinland | Köln, Düsseldorf, Bonn | none | major | all |
| sonstige | Odenwald, Spessart, Berlin, … | none | none | none |

### Großevents

<!-- specctl id=52505e type=RegGro nr=001 status=draft
history:
- 2026-10-13T11:24:27+00:00: M | Add
-->

Ein Großevent ist ein **überregional bekanntes** Event. Markiert wird es mit `major: true` an der
Eventserie in der Location, damit die Einstufung nicht jedes Jahr neu getroffen wird.

### Ausnahmen

<!-- specctl id=6b6613 type=RegAus nr=002 status=draft
history:
- 2026-10-13T11:24:27+00:00: M | Add
-->

`include: true` bzw. `exclude: true` an einer Location übersteuern die Regionsstufe
(z. B. einzelne Orte im Odenwald wie Michelstadt).

## Datenablage

<!-- specctl id=1eb682 type=Datena nr=004 status=draft
history:
- 2026-10-13T11:24:28+00:00: M | Add
-->

Format: **YAML**, validiert per JSON-Schema. Schlüssel englisch, Inhalte deutsch.

```
CLAUDE.md                              # Grundregeln, Definitionen, Arbeitsablauf
requirements.txt                       # pyyaml, jsonschema
.claude/settings.json                  # SessionStart-Hook: pip install -r requirements.txt
.claude/skills/<skill>/SKILL.md        # event-search, event-verify, series-rollover, calendar-sync
config/settings.yaml                   # Kalender-IDs, Regionen, Kategorien, Icons, Horizont
config/locations/<ort>.yaml            # Orte + Eventserien
data/events/<jahr>/<datum>-<slug>.yaml # ein Termin = eine Datei
schemas/{event,location,settings}.schema.json
tools/ec.py                            # CLI
tests/
prompts/*.md                           # fertige Aufträge für Sessions und Routinen
docs/spec.md, docs/tasks/              # diese Spec (specctl) und der Umsetzungsplan (taskctl)
```

### Event

<!-- specctl id=42837a type=DatEve nr=001 status=draft
history:
- 2026-10-13T11:24:28+00:00: M | Add
-->

Ein Termin = eine Datei unter `data/events/<jahr>/<datum>-<slug>.yaml`.
Die **Event-ID** ist der Pfad ohne Endung relativ zu `data/events/`
(z. B. `2026/2026-07-04-feuerwerk-rhein-in-flammen-bingen`). Sie dient als Sync-Schlüssel und als Ziel
von `parent`-Referenzen. Vergangene Events bleiben als Historie im Repo.

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
| `directions` | lokale Anfahrt/Zugang |
| `viewpoints` | Aussichtspunkte |
| `parent` | Event-ID des übergeordneten Events (optional, nur `feuerwerke`) |
| `status_note` | Begründung/Hinweis zum Status (z. B. Herleitung eines geschätzten Datums) |
| `sources`, `checked_at` | Nachweis-URLs, Datum der letzten Prüfung |

#### Herkunft lokaler Infos

<!-- specctl id=41c7fa type=DaEvHe nr=001 status=draft
history:
- 2026-10-13T11:24:28+00:00: M | Add
-->

- `directions` nur, wenn die Eventseite selbst Anfahrts-/Zugangshinweise anbietet (z. B. Dippemess).
- `viewpoints` nur aus Veranstalter- oder veröffentlichten Quellen (Stadtmarketing, Lokalpresse).
- Beides mit Quellen-URL in `sources`; nie vom Agenten selbst vorgeschlagen.

### Location

<!-- specctl id=eb9ab0 type=DatLoc nr=002 status=draft
history:
- 2026-10-13T11:24:28+00:00: M | Add
-->

Datei `config/locations/<ort>.yaml`. Eine Location ist eine **Stadt oder Gemeinde**; konkrete Plätze
stehen im Event (`venue`). Events über mehrere Orte hängen an einer Haupt-Location.

- `name`, `state` (Bundesland), `region`, `include`/`exclude`, `notes` (Freitext, z. B. eingestellte Serien)
- `series`: Liste der Eventserien mit `id`, `name`, `calendar`, `category`, `major`, `homepage`,
  `sources` (Such-URLs), `typical_period` (z. B. „1. Juli-Wochenende“), `has_fireworks`,
  Default-`directions`/`viewpoints`

Locations sind Konfiguration (sie steuern die Suche), Events sind Daten.

## Konfiguration

<!-- specctl id=e9f6ad type=Konfig nr=005 status=draft
history:
- 2026-10-13T11:24:28+00:00: M | Add
-->

`config/settings.yaml` enthält:

- Google-Kalender-IDs der drei Kalender
- Regionen und Stufen je Kalender (siehe „Regionen“)
- Kategorien und Icons
- Suchhorizont: 12 Monate ab heute; Weihnachtsmärkte immer für die kommende Saison
- Darstellung: keine Erinnerungen, Verfügbarkeit „frei“, Farbe grau für `geschätzt`

## Darstellung im Kalender

<!-- specctl id=da2b87 type=Darste nr=006 status=draft
history:
- 2026-10-13T11:24:28+00:00: M | Add
-->

- Titel: `<Icon> <Name> – <Ort>`; Präfix `❓` bei Status `geschätzt`
- Beschreibung aus fester Vorlage, gerendert von `ec.py`: Kurzbeschreibung, Öffnungszeiten, Ort/Maps,
  Homepage, ggf. lokale Anfahrt, ggf. Aussichtspunkte, ggf. „Teil von: <Event> (<Kalender>, <Zeitraum>)“
  bzw. „Show(s): …“, Status-/Unsicherheitshinweis
- Letzte Zeile: Sync-Fußzeile `ec:<id> · h:<hash>`
- Verknüpfungen nur als Text, keine Google-Event-IDs im Repo
- Keine Erinnerungen (`useDefaultReminders: false`), Verfügbarkeit „frei“, `geschätzt` grau

## Synchronisation

<!-- specctl id=b203b8 type=Synchr nr=007 status=draft
history:
- 2026-10-13T11:24:28+00:00: M | Add
-->

Über den Google-Calendar-MCP-Connector (keine Secrets nötig). Der Connector kann keine
`extendedProperties` setzen, daher steht der Sync-Schlüssel sichtbar in der Beschreibung.

1. `ec.py render --from <heute>` erzeugt den Soll-Zustand je Kalender.
2. Der Agent listet jeden Kalender ab heute.
3. Abgleich über `ec:`-Schlüssel und Hash: neu → anlegen; Hash geändert → aktualisieren;
   Schlüssel nicht im Soll oder Status `abgesagt` → löschen.
4. Vergangene Termine werden nie angefasst.
5. Bericht über angelegte, geänderte und gelöschte Termine.

Fallback bei Problemen mit vielen Terminen: direktes Skript gegen die Google Calendar API
(OAuth-Refresh-Token als Umgebungs-Secret).

## Tools

<!-- specctl id=93b5ed type=Tools_ nr=008 status=draft
history:
- 2026-10-13T11:24:28+00:00: M | Add
-->

`tools/ec.py` (Python; Abhängigkeiten erlaubt, siehe `requirements.txt`), Tests unter `tests/`.

| Befehl | Zweck |
|---|---|
| `validate` | Schema, Pflichtfelder, Referenzen (`location`, `series`, `parent`), Zeiten, Region/Stufe zulässig, Dubletten-Verdacht (gleiche Location+Serie, überlappender Zeitraum) |
| `render [--calendar X] [--from <datum>]` | Soll-Zustand als kompaktes JSON (Titel, Zeiten, Beschreibung, Farbe, Hash) |
| `new-event` / `new-location` | Gerüst mit korrektem Dateinamen/ID |
| `list` | Übersichten, z. B. alle `geschätzt`-Termine der nächsten 3 Monate |

**Architektur-Tools (specctl, taskctl):** Sie stammen aus `com-gft-tsbo-source/ai-architecture-tools`
und werden nicht ins Repo kopiert. Ein SessionStart-Hook klont das Repo auf einen **fest gepinnten Commit**
(`f25ae40a696037be4b9b6507c14cb08abbb73256`), damit das Dateiformat stabil bleibt. Ein Update ist eine
bewusste Änderung des Pins. Voraussetzung: Das Tool-Repo ist in der Session per Git erreichbar.
Aufruf: `specctl --root docs …` (Spec in `docs/spec.md`), `taskctl --root docs …` (Tasks in `docs/tasks/`).

## Skills

<!-- specctl id=f1be0a type=Skills nr=009 status=draft
history:
- 2026-10-13T11:24:28+00:00: M | Add
-->

Ablage unter `.claude/skills/` (in Web-Sessions automatisch geladen).

| Skill | Aufgabe |
|---|---|
| `event-search` | Neue Termine recherchieren (Filter: Kalender, Zeitraum, Region); Events und ggf. Locations/Serien anlegen; Shows separat mit `parent` |
| `event-verify` | `geschätzt`/`angekündigt` prüfen, Status hochstufen, Änderungen und Absagen nachziehen, `checked_at` setzen |
| `series-rollover` | Aus den Eventserien der Locations die Termine des Folgejahres ableiten und recherchieren |
| `calendar-sync` | Ablauf gemäß „Synchronisation“ |

`CLAUDE.md` enthält die Grundregeln: Repo führend; nach jeder Datenänderung `validate` → Sync → Bericht;
Kategorie- und Regionsdefinitionen; Herkunftsregeln für `directions`/`viewpoints`.

## Prompts

<!-- specctl id=b792d7 type=Prompt nr=010 status=draft
history:
- 2026-10-13T11:24:28+00:00: M | Add
-->

Kurze, fertige Aufträge unter `prompts/*.md`, die auf die Skills verweisen – zum Einfügen in eine
Web-Session oder als Routine-Text:

- `search-weihnachtsmaerkte.md`, `search-feuerwerke.md`, `search-events.md`
- `verify-upcoming.md`
- `rollover-next-year.md`
- `sync-all.md`

## Arbeitsweise

<!-- specctl id=7580d2 type=Arbeit nr=011 status=draft
history:
- 2026-10-13T11:24:29+00:00: M | Add
-->

- Der Agent committet **direkt auf `main`**.
- Jede Session mit Datenänderung endet mit `validate`, Sync und Bericht.
- Routinen (geplante Cloud-Sessions) erst, wenn die manuellen Abläufe stabil laufen:
  Weihnachtsmärkte Juli–Oktober, Feuerwerke und Events monatlich, jährlicher Rollover.

## Manuelle Schritte

<!-- specctl id=8c28bf type=Manuel nr=012 status=draft
history:
- 2026-10-13T11:24:29+00:00: M | Add
-->

- Zeitzone des Kalenders `Feuerwerke` von UTC auf Europe/Berlin umstellen.
- Bestehende Termine in allen drei Kalendern vor dem ersten echten Sync löschen.
