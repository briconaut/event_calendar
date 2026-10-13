---
name: series-rollover
description: Leitet aus den Eventserien der Locations die Termine des Folgejahres ab und recherchiert sie. Nutzen bei „Rollover“, „Folgejahr“, „nächstes Jahr anlegen“ oder dem jährlichen Pflegelauf.
---

# series-rollover

Statusregeln und Herkunftsregeln: `CLAUDE.md`.

## Schritte

1. **Zieljahr bestimmen**: aus dem Auftrag, sonst das Kalenderjahr nach dem aktuellen.

2. **Serienliste bilden**: jede Serie in `config/locations/*.yaml`, deren Location für den Kalender der
   Serie zulässig ist (Region/Stufe, `major`). Für jede Serie prüfen, ob im Zieljahr schon ein Termin mit
   dieser `series` existiert (`python3 tools/ec.py list --json --from <Zieljahr>-01-01`).

3. **Je Serie ohne Termin:**
   - Recherche über `homepage` und `sources` der Serie; Fund → Termin mit `angekündigt`/`bestätigt`.
   - Kein Fund → Termin mit `status: geschätzt`, Datum aus `typical_period` bzw. dem Vorjahrestermin
     (gleicher Wochentag/gleiches Wochenende), Begründung in `status_note`.
   - Serien mit `has_fireworks: true`: die Show(s) als eigene Termine mit `parent` anlegen;
     Uhrzeit unbekannt → `time_unknown: true`.
   - Serie offenbar eingestellt → keinen Termin anlegen, in `notes` der Location vermerken
     und im Bericht nennen.

4. **Abschließen** gemäß Arbeitsablauf in `CLAUDE.md`.

## Bericht

Tabelle: Serie, Location, Zieljahr-Termin (Event-ID) bzw. Grund für „kein Termin“, Status.
Fertig ist der Rollover, wenn jede Serie aus Schritt 2 einen Termin im Zieljahr hat oder begründet fehlt.
