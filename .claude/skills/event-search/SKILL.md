---
name: event-search
description: Recherchiert neue Termine für die Kalender Weihnachtsmärkte, Feuerwerke oder Events und Feste und legt sie als Event-Dateien (plus Locations/Eventserien) an. Nutzen bei „suche“, „finde Events“, „neue Termine“ oder einer Eventsuche je Kalender, Region oder Zeitraum.
---

# event-search

Definitionen, Regionen, Statusregeln und Herkunftsregeln stehen in `CLAUDE.md` – sie sind der Maßstab
für jede Aufnahmeentscheidung.

## Schritte

1. **Rahmen festlegen.** Kalender, Regionen und Zeitraum aus dem Auftrag; fehlt etwas, gelten alle drei
   Kalender, alle Regionen mit Stufe `all`/`major` und der Horizont aus `config/settings.yaml`
   (Weihnachtsmärkte: kommende Saison). Den Rahmen am Anfang des Berichts nennen.

2. **Bestand sichten.** `python3 tools/ec.py list --from <heute>` und die Eventserien in
   `config/locations/` – jede bekannte Serie ist ein Kandidat, für den ein Termin im Zeitraum fehlen kann.

3. **Kandidaten sammeln.** WebSearch/WebFetch über Stadtportale, Veranstalterseiten, regionale
   Eventkalender und die `sources` der Serien. Je Region und Kalender systematisch vorgehen, bis die
   offensichtlichen Quellen erschöpft sind. Für Feuerwerke gezielt nach Shows in Festprogrammen suchen
   (Abschlussfeuerwerk, Drohnenshow, Lasershow, Illumination, Silvester).

4. **Jeden Kandidaten entscheiden:** aufnehmen, aktualisieren (Termin existiert schon) oder verwerfen,
   mit Grund (Kategorie passt nicht, Region ausgeschlossen, kein Großevent, zu klein, Dublette).

5. **Anlegen.**
   - Location: vorhandene nutzen, sonst `python3 tools/ec.py new-location` mit Region nach der Liste in
     `CLAUDE.md`. Wiederkehrende Events als Serie eintragen (`id`, `name`, `calendar`, `category`,
     `major`, `homepage`, `sources`, `typical_period`, `has_fireworks`).
   - Termin: `python3 tools/ec.py new-event …`, dann alle Felder füllen – `status` nach den Statusregeln,
     `sources` mit den tatsächlich genutzten URLs (Platzhalter `https://TODO` ersetzen), `checked_at` = heute.
   - Hat ein Event eine Show: das Event anlegen und für **jede** Show (je Datum und Ort) einen eigenen
     Termin im Kalender `feuerwerke` mit `parent` = Event-ID und eigener Uhrzeit.

6. **Validieren und abschließen** gemäß Arbeitsablauf in `CLAUDE.md` (validate → Push auf `main` → `calendar-sync`).

## Bericht

Tabelle aller Kandidaten aus Schritt 4: Titel, Ort, Datum, Entscheidung, Grund bzw. Event-ID.
Fertig ist die Suche, wenn jeder Kandidat eine Entscheidung hat und `ec.py validate` fehlerfrei ist.
