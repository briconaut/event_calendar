---
name: series-rollover
description: Leitet aus den Eventserien der Locations die Termine des Folgejahres ab und recherchiert sie. Nutzen bei „Rollover“, „Folgejahr“, „nächstes Jahr anlegen“ oder dem jährlichen Pflegelauf.
---

# series-rollover

Statusregeln und Herkunftsregeln: `CLAUDE.md`.

## Schritte

1. **Zieljahr bestimmen**: aus dem Auftrag, sonst das Kalenderjahr nach dem aktuellen.

2. **Serienliste bilden**: je Kalender
   `python3 tools/ec.py checklist --calendar <kalender> --from <Zieljahr>-01-01 --to <Zieljahr>-12-31` –
   alle Serien aus `config/locations/*.yaml` und die ortsunabhängigen aus `config/series.yaml`, mit
   vorhandenen Terminen im Zieljahr. Serien mit `ausgeschlossen` entfallen.

3. **Je Serie ohne Termin:**
   - Recherche über `homepage` und `sources` der Serie; Fund → Termin mit `angekündigt`/`bestätigt`.
     Zusätzlich die `required_sources` aus der Checkliste lesen, deren `calendars` den Kalender der Serie
     enthält (Umgang mit nicht lesbaren Quellen wie in `event-search`, Schritt 3 b).
   - Ortsunabhängige Serie (`location: null`): zuerst den Austragungsort des Zieljahres ermitteln; der
     Termin hängt an dessen Location (ggf. neu anlegen), die Regionsregeln gelten für diesen Ort.
     Austragungsort unbekannt → kein Termin (nicht schätzen), im Bericht nennen; Ort unzulässig → kein
     Termin, Grund im Bericht.
   - Kein Fund → Termin mit `status: geschätzt`, Datum aus `typical_period` bzw. dem Vorjahrestermin
     (gleicher Wochentag/gleiches Wochenende), Begründung in `status_note`.
   - Serien mit `has_fireworks: true`: die Show(s) als eigene Termine mit `parent` anlegen;
     Uhrzeit unbekannt → `time_unknown: true`.
   - Serie offenbar eingestellt → keinen Termin anlegen, in `notes` der Location (bzw. der Serie in
     `config/series.yaml`) vermerken und im Bericht nennen.

4. **Abschließen** gemäß Arbeitsablauf in `CLAUDE.md`.

## Bericht

Tabelle: Serie, Location, Zieljahr-Termin (Event-ID) bzw. Grund für „kein Termin“, Status.
Fertig ist der Rollover, wenn jede Serie aus Schritt 2 einen Termin im Zieljahr hat oder begründet fehlt.
